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
from .controllers import call_model, get_vectorstore_from_files, load_vectorstore_from_file, num_tokens_from_string

# Onde é carregador as variáveis de ambiente
load_dotenv(find_dotenv())

# Criação da pasta temp (./docmind/temp)
temp_dir = os.path.dirname(os.path.abspath(__file__))
temp_dir = os.path.dirname(os.path.dirname(temp_dir))
temp_dir = os.path.join(temp_dir, 'temp')
os.makedirs(temp_dir, exist_ok=True)

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