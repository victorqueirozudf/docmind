# LÓGICA DO SISTEMA AQUI, COMENTADO PARA SER FEITO MAIS TESTES

import os
import uuid
import io

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

from langchain_core.messages import HumanMessage
from langchain.text_splitter import CharacterTextSplitter
from langgraph.graph import START, MessagesState, StateGraph
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from pypdf import PdfReader
import tiktoken

from .checkpointer import DjangoSaver
from dotenv import load_dotenv, find_dotenv
from .models import DjCheckpoint, ChatDetails
from .serializers import ChatDetailSerializer, UserSerializer

# Onde é carregador as variáveis de ambiente
load_dotenv(find_dotenv())

# Criação da pasta temp (./docmind/temp)
temp_dir = os.path.dirname(os.path.abspath(__file__))
temp_dir = os.path.dirname(os.path.dirname(temp_dir))
temp_dir = os.path.join(temp_dir, 'temp')
os.makedirs(temp_dir, exist_ok=True)

# Define o número de tokens de um texto
def num_tokens_from_string(string: str) -> int:
    # Returns the number of tokens in a text string.
    encoding = tiktoken.encoding_for_model("gpt-4o-mini")
    num_tokens = len(encoding.encode(string))
    return num_tokens

"""RESPONSÁVEIS POR CRIAR OS ARQUIVOS PARA PESQUISA DE DADOS"""
def get_vectorstore_from_files(pdf_docs, thread_id):
    text = ""

    # Verifica se é uma lista de arquivos ou um único arquivo
    if not isinstance(pdf_docs, list):
        pdf_docs = [pdf_docs]

    print(f"Recebendo {len(pdf_docs)} documentos PDF para o thread_id {thread_id}.\n")

    for pdf in pdf_docs:
        # Verifica se o pdf tem o atributo 'name', caso contrário, assume que é um objeto bytes
        if hasattr(pdf, 'name'):
            print(f"Lendo arquivo: {pdf.name}")
        else:
            print(f"Lendo arquivo anônimo (sem nome), tamanho: {len(pdf)} bytes")

        # Lê o conteúdo do arquivo em memória
        pdf_bytes = pdf.read() if hasattr(pdf, 'read') else pdf  # Se for um arquivo, chama o read()
        pdf_stream = io.BytesIO(pdf_bytes)
        #print(f"Tamanho do arquivo em bytes: {len(pdf_bytes)}")

        # Processa o PDF
        pdf_reader = PdfReader(pdf_stream)

        for page in pdf_reader.pages:
            page_text = page.extract_text()
            text += page_text

    # Split do texto em chunks
    #print("Iniciando divisão do texto em chunks...\n")
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1024,
        chunk_overlap=256,
        length_function=len
    )

    chunks = text_splitter.split_text(text)
    #print(f"{len(chunks)} chunks gerados.\n")

    # Criação dos embeddings
    embeddings = OpenAIEmbeddings()

    # Criação da store FAISS
    vectorstore = FAISS.from_texts(texts=chunks, embedding=embeddings)

    # Define o caminho da pasta e do arquivo FAISS
    folder_path = os.path.join(temp_dir, str(thread_id))

    # Cria a pasta se ela não existir
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Pasta criada: {folder_path}\n")

    # Salva o índice FAISS
    vectorstore.save_local(folder_path)
    print(f"Vetores salvos em {folder_path}\n")

    return vectorstore

# Função para carregar o vetor do arquivo FAISS ou criar se não existir
def load_vectorstore_from_file(thread_id):
    folder_path = os.path.join(temp_dir, thread_id)
    file_path = os.path.join(folder_path, "index.pkl")

    # Verifica se o arquivo FAISS já existe
    if os.path.exists(file_path):
        print(f"Carregando vetores do arquivo {folder_path}\n")
        vectorstore = FAISS.load_local(folder_path, OpenAIEmbeddings(), allow_dangerous_deserialization=True)
        return vectorstore
    else:
        print(f"O arquivo {file_path} não existe. Subir arquivo novamente.\n")
        # Caso não exista, cria os vetores e salva o arquivo FAISS
        #return get_vectorstore_from_files(thread_id, pdf_docs)

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

    #print(prompt)

    response = model.invoke(prompt)

    input_tokens = num_tokens_from_string(prompt[0][1]) + num_tokens_from_string(prompt[1][1])
    output_tokens = num_tokens_from_string(response.content)

    price_per_one_million = 0.150

    print(f"""Total de tokens e valor total:\nInput: {input_tokens} - US${(input_tokens * price_per_one_million)/1000000:.8f}\nOutput: {output_tokens} - US${(output_tokens * price_per_one_million)/1000000:.8f}\nTotal tokens: {input_tokens + output_tokens} - Total gasto: US${((input_tokens + output_tokens) * price_per_one_million)/1000000:.8f}\n\n""",end="")

    return {"messages": response}

@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HomeView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user  # Obtém o usuário autenticado
        content = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }
        return Response(content)

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):

        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class PDFChatView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        chats = ChatDetails.objects.filter(user=request.user)
        serializer = ChatDetailSerializer(chats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        thread_id = uuid.uuid4()
        chat_name = request.data.get('chatName')
        pdf_file = request.FILES.get('pdfs')

        if not pdf_file:
            return Response({'error': 'Arquivo PDF é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

        print(f'Tipo de pdf_file: {type(pdf_file)}')

        if ChatDetails.objects.filter(thread_id=thread_id).exists():
            return Response(
                {'error': 'Chat com este thread_id já existe.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        path = os.path.join(temp_dir, str(thread_id))

        data = {
            'thread_id': thread_id,
            'path': path,
            'chatName': chat_name,
        }

        print(thread_id)

        # criando os vetores a partir do documento, não sendo necessário hostear o mesmo
        get_vectorstore_from_files(pdf_file, thread_id)

        serializer = ChatDetailSerializer(data=data)

        print(thread_id)

        if serializer.is_valid():
            print(f'Serializer validated data: {serializer.validated_data}')
            serializer.save(user=request.user)  # Salva com o usuário autenticado
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # imprima os erros do serializer
        print(f'Serializer errors: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, thread_id, *args, **kwargs):
        try:
            chat = ChatDetails.objects.get(thread_id=thread_id, user=request.user)
            chat.delete()  # Exclui o chat
            return Response(status=status.HTTP_204_NO_CONTENT)  # Retorna um status de sucesso
        except ChatDetails.DoesNotExist:
            return Response({'error': 'Chat não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

class PDFChatDetailView(APIView):
    def get(self, request, thread_id):

        # Retorna as mensagens associadas ao thread_id especificado.

        try:
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

        vectorstore = load_vectorstore_from_file(thread_id)

        if not question or not thread_id:
            return Response({"error": "Pergunta ou thread_id são necessários"},
                            status=status.HTTP_400_BAD_REQUEST)

        if not vectorstore:
            return Response({"error": "É necessário ter uma base de dados."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Criar uma instância do DjangoSaver para checkpoints
        checkpointer = DjangoSaver()

        # Definir um novo grafo
        workflow = StateGraph(state_schema=MessagesState)

        # Definir os nós no grafo
        workflow.add_edge(START, "model")
        workflow.add_node("model", lambda state: call_model(state, vectorstore, question))

        config = {"configurable": {"thread_id": thread_id}}

        app = workflow.compile(checkpointer=checkpointer)

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

        return Response({'status': 'success', 'answer': answer}, status=status.HTTP_200_OK)