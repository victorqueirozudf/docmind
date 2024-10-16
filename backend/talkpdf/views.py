# LÓGICA DO SISTEMA AQUI, COMENTADO PARA SER FEITO MAIS TESTES

# https://blog.logrocket.com/django-rest-framework-create-api/

import os
import json
import uuid
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from langchain_core.messages import HumanMessage, AIMessage
from langchain.text_splitter import CharacterTextSplitter
from langgraph.graph import START, MessagesState, StateGraph
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from pypdf import PdfReader
from .checkpointer import DjangoSaver
from dotenv import load_dotenv, find_dotenv
from .models import DjCheckpoint, ChatDetails
from .serializers import ChatDetailSerializer
import tiktoken
import pickle

load_dotenv(find_dotenv())

#temp_dir = "c:\\docmind\\temp"

temp_dir = os.path.dirname(os.path.abspath(__file__))
temp_dir = os.path.dirname(os.path.dirname(temp_dir))

# Define o caminho para a pasta 'temp'
temp_dir = os.path.join(temp_dir, 'temp')

# Cria a pasta 'temp' se ela não existir
os.makedirs(temp_dir, exist_ok=True)

def num_tokens_from_string(string: str) -> int:
    # Returns the number of tokens in a text string.
    encoding = tiktoken.encoding_for_model("gpt-4o-mini")
    num_tokens = len(encoding.encode(string))
    return num_tokens

"""RESPONSÁVEIS POR CRIAR OS ARQUIVOS PARA PESQUISA DE DADOS"""
# Função para extrair texto de documentos PDF
def extract_text_from_pdf(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

# Função para dividir o texto em chunks
def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1024,
        chunk_overlap=256,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

# Função para gerar o vetor a partir dos chunks de texto
def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

# Função para criar o vetor e salvar o índice FAISS
def load_vectorstore(thread_id, pdf_docs):
    # Extrair texto dos PDFs e gerar vetores
    raw_text = extract_text_from_pdf(pdf_docs)
    text_chunks = get_text_chunks(raw_text)
    vectorstore = get_vectorstore(text_chunks)

    # Define o caminho da pasta e do arquivo FAISS
    folder_path = os.path.join(temp_dir, thread_id)

    # Cria a pasta se ela não existir
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Pasta criada: {folder_path}\n")

    # Salva o índice FAISS
    vectorstore.save_local(folder_path)
    print(f"Vetores salvos em {folder_path}\n")

    return vectorstore

# Função para carregar o vetor do arquivo FAISS ou criar se não existir
def load_vectorstore_from_file(thread_id, pdf_docs):
    folder_path = os.path.join(temp_dir, thread_id)
    file_path = os.path.join(folder_path, "index.pkl")

    # Verifica se o arquivo FAISS já existe
    if os.path.exists(file_path):
        print(f"Carregando vetores do arquivo {folder_path}\n")
        vectorstore = FAISS.load_local(folder_path, OpenAIEmbeddings(), allow_dangerous_deserialization=True)
        return vectorstore
    else:
        print(f"O arquivo {file_path} não existe. Criando novos vetores.\n")
        # Caso não exista, cria os vetores e salva o arquivo FAISS
        return load_vectorstore(thread_id, pdf_docs)

def call_model(state: MessagesState, vectorstore, question):
    # Modelo de chat
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    # Filtrar apenas HumanMessage
    human_messages = [msg.content for msg in state['messages'] if isinstance(msg, HumanMessage)]

    retriever = vectorstore.as_retriever()
    retrieved_docs = retriever.invoke(state["messages"][-1].content)

    # Ordena os documentos pela ordem de inserção, assumindo que eles têm um campo 'insertion_order'
    sorted_docs = sorted(retrieved_docs, key=lambda doc: doc.metadata.get('insertion_order', 0))

    print(sorted_docs)

    # Concatene os resultados dos documentos recuperados em ordem
    pdf_response = "\n".join([doc.page_content for doc in sorted_docs])

    #memory = model.invoke(state["messages"])
    #print(memory)

    input_user = "Históricos de mensagens passadas: \n " + str(human_messages) + "\n" + str([HumanMessage(content=pdf_response)])

    #print(f"Pergunta: {question}\n\nAqui está um trecho do documento:\n\n{input_user}\n\nPor favor, responda à pergunta com base no documento de forma direta.")

    prompt = [
        (
            "system",
            "Você é um assistente especializado em leitura de documentos PDF. Responda às perguntas do usuário de forma clara, concisa e relevante, limitando a resposta aos pontos mais importantes."
        ),
        (
            "human",
            f"Pergunta: {question}\n\nAqui está um trecho do documento:\n\n{input_user}\n\nPor favor, responda à pergunta com base no documento de forma direta."
        )
    ]

    print(prompt)

    #print("O que é mandado: " + prompt)

    #print()

    # Chama o modelo passando todas as mensagens do estado
    response = model.invoke(prompt)

    input_tokens = num_tokens_from_string(prompt[0][1]) + num_tokens_from_string(prompt[1][1])
    output_tokens = num_tokens_from_string(response.content)

    price_per_one_million = 0.150

    print(f"""Total de tokens e valor total:\nInput: {input_tokens} - US${(input_tokens * price_per_one_million)/1000000:.8f}\nOutput: {output_tokens} - US${(output_tokens * price_per_one_million)/1000000:.8f}\nTotal tokens: {input_tokens + output_tokens} - Total gasto: US${((input_tokens + output_tokens) * price_per_one_million)/1000000:.8f}\n\n""",end="")

    return {"messages": response}

class PDFChatView(APIView):
    def get(self, request, *args, **kwargs):

        # Listar todos os chats criados.

        chats = ChatDetails.objects.all()
        serializer = ChatDetailSerializer(chats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        thread_id = uuid.uuid4()
        chat_name = request.data.get('chatName')
        pdf_file = request.FILES.get('pdfs')

        if not pdf_file:
            return Response({'error': 'Arquivo PDF é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

        # Salva o arquivo no diretório desejado
        path = os.path.join(temp_dir, str(pdf_file.name))

        # Verificar se o thread_id já existe
        if ChatDetails.objects.filter(thread_id=thread_id).exists():
            return Response(
                {'error': 'Chat com este thread_id já existe.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Dados para criar o novo chat
        data = {
            'thread_id': thread_id,
            'path': path,  # Salva o caminho absoluto do arquivo no servidor
            'chatName': chat_name,
        }

        serializer = ChatDetailSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PDFChatDetailView(APIView):
    def get(self, request, thread_id):

        # Retorna as mensagens associadas ao thread_id especificado.

        try:
            print(temp_dir)

            # Filtrar mensagens com base no thread_id
            chat_messages = DjCheckpoint.objects.filter(thread_id=thread_id)
            # Aqui, você pode converter as mensagens em um formato serializável
            messages = [
                {
                    "metadata": message.metadata,
                }
                for message in chat_messages
            ]

            return Response({"status": "success", "messages": messages}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, *args, **kwargs):
        """
        Atualiza ou cria uma nova entrada de chat.
        """
        pdfs = request.data.get('path_file')  # Altera para pegar o caminho
        question = request.data.get("question")
        thread_id = request.data.get("thread_id")

        pdf_path = [pdfs]
        print(pdf_path)

        if not pdfs or not question or not thread_id:
            return Response({"error": "PDF, pergunta ou thread_id são necessários"},
                            status=status.HTTP_400_BAD_REQUEST)

        if not os.path.exists(pdfs):
            return Response({"error": "Arquivo PDF não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # Criar uma instância do DjangoSaver para checkpoints
        checkpointer = DjangoSaver()

        # Definir um novo grafo
        workflow = StateGraph(state_schema=MessagesState)

        # Definir os nós no grafo
        workflow.add_edge(START, "model")
        workflow.add_node("model", lambda state: call_model(state, vectorstore,
                                                            question))

        config = {"configurable": {"thread_id": thread_id}}

        app = workflow.compile(checkpointer=checkpointer)

        # Extraindo e processando o PDF
        files = extract_text_from_pdf(pdf_path)
        chunks = get_text_chunks(files)
        vectorstore = load_vectorstore_from_file(thread_id, pdf_path)

        # Criar a mensagem de entrada
        input_message = HumanMessage(content=question)
        events = []

        # Executar o fluxo de conversa
        for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
            events.append(event)

        # Retornar o último estado do chat e o UUID do thread
        answer = {
            "thread_id": thread_id,
            "last_message": events[-1]["messages"][-1].content if events else "Sem resposta disponível"
        }

        values = app.get_state(config).values
        #print(values)

        return Response({'status': 'success', 'answer': answer}, status=status.HTTP_200_OK)