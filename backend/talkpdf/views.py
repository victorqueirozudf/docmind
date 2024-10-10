"""
import os
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from langchain_core.messages import HumanMessage
from langgraph.graph import START, MessagesState, StateGraph
from langchain_openai import ChatOpenAI
from .checkpointer import DjangoSaver
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class PDFProcessView(APIView):
    def post(self, request, *args, **kwargs):
        question = request.data.get("question")
        thread_id = request.data.get("thread_id", "123")  # Usar 123 como padrão se não for passado

        # Verificar se a pergunta foi fornecida
        if not question:
            return Response({"error": "A pergunta é necessária"}, status=status.HTTP_400_BAD_REQUEST)

        # Criar uma instância do DjangoSaver para checkpoints
        checkpointer = DjangoSaver()

        # Definir um novo grafo
        workflow = StateGraph(state_schema=MessagesState)

        # Modelo de chat
        model = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)

        def call_model(state: MessagesState):
            print("Estado antes da chamada ao modelo:", state)
            query = state["messages"][-1].content  # Pegue a última mensagem do usuário
            print("Última pergunta:", query)

            print(str(state["messages"]))

            response = model.invoke(state["messages"])  # Chama o modelo
            # print("Resposta do modelo:", response)
            return {"messages": response}

        # Definir os nós no grafo
        workflow.add_edge(START, "model")
        workflow.add_node("model", lambda state: call_model(state))

        config = {"configurable": {"thread_id": thread_id}}

        # Compilando o app
        app = workflow.compile(checkpointer=checkpointer)

        # Criar a mensagem de entrada
        input_message = HumanMessage(content=question)
        events = []

        # Executar o fluxo de conversa
        for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
            events.append(event)

        # Retornar o último estado do chat e o UUID do thread
        response = {
            "thread_id": thread_id,
            "last_message": events[-1]["messages"][-1].content if events else "Sem resposta disponível"
        }

        return Response(response, status=status.HTTP_200_OK)
"""

# LÓGICA DO SISTEMA AQUI, COMENTADO PARA SER FEITO MAIS TESTES

# https://blog.logrocket.com/django-rest-framework-create-api/

import os
import json
import uuid
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from langchain_core.messages import HumanMessage
from langchain.text_splitter import CharacterTextSplitter
from langgraph.graph import START, MessagesState, StateGraph
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from PyPDF2 import PdfReader
from .checkpointer import DjangoSaver
from dotenv import load_dotenv, find_dotenv
from .models import DjCheckpoint, ChatDetails
from .serializers import ChatDetailSerializer

load_dotenv(find_dotenv())

temp_pdf = f'C:\\docmind\\temp\\'

def extract_text_from_pdf(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1024,
        chunk_overlap=256,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

def call_model(state: MessagesState, vectorstore, question):
    # Modelo de chat
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    retriever = vectorstore.as_retriever()
    retrieved_docs = retriever.invoke(state["messages"][-1].content)

    # Ordena os documentos pela ordem de inserção, assumindo que eles têm um campo 'insertion_order'
    sorted_docs = sorted(retrieved_docs, key=lambda doc: doc.metadata.get('insertion_order', 0))

    # Concatene os resultados dos documentos recuperados em ordem
    pdf_response = "\n".join([doc.page_content for doc in sorted_docs])

    # print(pdf_response)

    input_user = state["messages"] + [HumanMessage(content=pdf_response)]

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

    # print("O que é mandado: " + prompt)

    # Chama o modelo passando todas as mensagens do estado
    response = model.invoke(prompt)

    return {"messages": response}

class PDFChatView(APIView):
    def get(self, request, *args, **kwargs):
        """Listar todos os chats criados."""
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
        path = temp_pdf + str(pdf_file.name)

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
        """
        Retorna as mensagens associadas ao thread_id especificado.
        """
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
                                                            question))  # Passar o vectorstore dentro da função

        config = {"configurable": {"thread_id": thread_id}}

        app = workflow.compile(checkpointer=checkpointer)

        # Extraindo e processando o PDF
        files = extract_text_from_pdf(pdf_path)
        chunks = get_text_chunks(files)
        vectorstore = get_vectorstore(chunks)

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
        print(values)

        return Response({'status': 'success', 'answer': answer}, status=status.HTTP_200_OK)

class TelegramBotView(APIView):
    nome = None

class PDFExtractorView(APIView):
    nome = None