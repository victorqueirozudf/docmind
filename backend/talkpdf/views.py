# LÓGICA DO SISTEMA AQUI, COMENTADO PARA SER FEITO MAIS TESTES

import os
import uuid
import shutil

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status

from django.shortcuts import get_object_or_404

from dotenv import load_dotenv, find_dotenv
from .models import ChatCheckpoint, ChatDetails
from .serializers import ChatDetailsSerializer, ChatCheckpointSerializer
from .controllers import get_vectorstore_from_files, get_anwser

# Onde é carregador as variáveis de ambiente
load_dotenv(find_dotenv())

# Criação da pasta temp (./docmind/temp)
temp_dir = os.path.dirname(os.path.abspath(__file__))
temp_dir = os.path.dirname(os.path.dirname(temp_dir))
temp_dir = os.path.join(temp_dir, 'temp')
os.makedirs(temp_dir, exist_ok=True)

class PDFChatView(APIView):
    """
    View para gerenciar chats baseados em PDFs para usuários autenticados.
    """

    #authentication_classes = [JWTAuthentication]
    #permission_classes = [IsAuthenticated]

    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """
        Recupera e lista todos os chats do usuário autenticado.

        Args:
            request (HttpRequest): O objeto HTTP da requisição.
            *args: Argumentos posicionais adicionais.
            **kwargs: Argumentos nomeados adicionais.

        Returns:
            Response: Resposta HTTP contendo a lista de chats serializados e o status 200 OK.

        Example:
            [
                {
                    "thread_id": "36e9d38f-413f-4866-8609-8d657ed9fd29",
                    "chatName": "Chat de Projeto",
                    "path": "/path/to/vectorstore",
                    "created_at": "2024-04-27T12:34:56Z"
                },
                {
                    "thread_id": "a12b34c5-d678-90ef-gh12-3456ijkl7890",
                    "chatName": "Chat de Suporte",
                    "path": "/path/to/vectorstore",
                    "created_at": "2024-04-28T08:22:33Z"
                }
            ]
        """
        chats = ChatDetails.objects.filter(user=request.user)
        serializer = ChatDetailsSerializer(chats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    #@transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        Cria um novo chat associado a um arquivo PDF enviado e gera os vetores necessários.

        Args:
            request (HttpRequest): O objeto HTTP da requisição contendo 'chatName' e 'pdfs'.
            *args: Argumentos posicionais adicionais.
            **kwargs: Argumentos nomeados adicionais.

        Returns:
            Response: Resposta HTTP contendo os dados do chat criado serializados e o status 201 CREATED.

        Raises:
            HTTP_400_BAD_REQUEST: Se o arquivo PDF não for fornecido ou se o thread_id já existir.
            HTTP_500_INTERNAL_SERVER_ERROR: Se ocorrer um erro ao processar o PDF.

        Example (Success):
            {
                "thread_id": "36e9d38f-413f-4866-8609-8d657ed9fd29",
                "chatName": "Chat de Projeto",
                "path": "/path/to/vectorstore",
                "created_at": "2024-04-27T12:34:56Z"
            }

        Example (Error - PDF não fornecido):
            {
                "error": "Arquivo PDF é obrigatório."
            }

        Example (Error - Thread ID já existe):
            {
                "error": "Chat com este thread_id já existe."
            }

        Example (Error - Processamento do PDF falhou):
            {
                "error": "Erro ao processar o PDF: Detalhes do erro."
            }
        """
        thread_id = uuid.uuid4()
        chat_name = request.data.get('chatName')
        pdf_file = request.FILES.get('pdfs')

        if not pdf_file:
            return Response({'error': 'Arquivo PDF é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

        if ChatDetails.objects.filter(thread_id=thread_id).exists():
            return Response(
                {'error': 'Chat com este thread_id já existe.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Definir o caminho para armazenar os vetores
        path = os.path.join(temp_dir, str(thread_id))

        # Criar a instância de ChatDetails
        chat = ChatDetails.objects.create(
            user=request.user,
            thread_id=thread_id,
            path=path,
            chatName=chat_name
        )

        # Criar os vetores a partir do documento PDF
        try:
            get_vectorstore_from_files(pdf_file, thread_id)
        except Exception as e:
            # Se ocorrer um erro durante a criação dos vetores, desfazer a criação do chat e remover arquivos
            print(f"Error: {e}")
            chat.delete()
            if os.path.exists(path):
                shutil.rmtree(path, ignore_errors=True)
            return Response({'error': f'Erro ao processar o PDF: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = ChatDetailsSerializer(chat)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, thread_id, *args, **kwargs):
        """
        Deleta um chat específico e seus dados associados.

        Args:
            request (HttpRequest): O objeto HTTP da requisição.
            thread_id (UUID): O identificador único do chat a ser deletado.
            *args: Argumentos posicionais adicionais.
            **kwargs: Argumentos nomeados adicionais.

        Returns:
            Response: Resposta HTTP com o status 204 NO CONTENT se a exclusão for bem-sucedida.

        Raises:
            HTTP_500_INTERNAL_SERVER_ERROR: Se ocorrer um erro ao deletar os arquivos do chat.

        Example (Success):
            Status Code: 204 NO CONTENT

        Example (Error):
            {
                "error": "Erro ao deletar os arquivos do chat: Detalhes do erro."
            }
        """
        # Recuperar o ChatDetails com base no thread_id e no usuário autenticado
        chat = get_object_or_404(ChatDetails, thread_id=thread_id, user=request.user)

        # Lógica para apagar a pasta associada ao chat
        try:
            if os.path.exists(chat.path):
                shutil.rmtree(chat.path, ignore_errors=True)  # Remove a pasta e todo o seu conteúdo
        except Exception as e:
            return Response({'error': f'Erro ao deletar os arquivos do chat: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Excluir o chat e seus objetos relacionados (DjCheckpoint e DjWrite) devido ao on_delete=models.CASCADE
        chat.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PDFChatDetailView(APIView):
    """
    View para gerenciar detalhes específicos de um chat, incluindo o histórico de checkpoints e respostas às perguntas dos usuários.
    """

    #authentication_classes = [JWTAuthentication]
    #permission_classes = [IsAuthenticated]
    permission_classes = (IsAuthenticated,)

    def get(self, request, thread_id):
        """
        Recupera o histórico de checkpoints de um chat específico.

        Args:
            request (HttpRequest): O objeto HTTP da requisição.
            thread_id (UUID): O identificador único do chat cujo histórico será recuperado.

        Returns:
            Response: Resposta HTTP contendo o status de sucesso e a lista de checkpoints serializados com o status 200 OK.

        Example:
            {
                "status": "success",
                "messages": [
                    {
                        "checkpoint_id": 1,
                        "content": "Primeira mensagem do checkpoint.",
                        "timestamp": "2024-04-27T12:34:56Z"
                    },
                    {
                        "checkpoint_id": 2,
                        "content": "Segunda mensagem do checkpoint.",
                        "timestamp": "2024-04-27T13:00:00Z"
                    }
                ]
            }
        """
        # Recuperar o ChatDetails com base no thread_id e no usuário autenticado
        chat = get_object_or_404(ChatDetails, thread_id=thread_id, user=request.user)

        # Filtrar checkpoints relacionados ao chat
        chat_checkpoints = ChatCheckpoint.objects.filter(chat=chat)

        # Serializar os checkpoints
        serializer = ChatCheckpointSerializer(chat_checkpoints, many=True)

        return Response({"status": "success", "messages": serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, thread_id, *args, **kwargs):
        """
        Recebe uma pergunta do usuário e retorna uma resposta baseada no histórico do chat.

        Args:
            request (HttpRequest): O objeto HTTP da requisição contendo a pergunta.
            thread_id (UUID): O identificador único do chat ao qual a pergunta será associada.
            *args: Argumentos posicionais adicionais.
            **kwargs: Argumentos nomeados adicionais.

        Returns:
            Response: Resposta HTTP contendo o status de sucesso e a resposta à pergunta com o status 200 OK.

        Raises:
            HTTP_400_BAD_REQUEST: Se a pergunta não for fornecida.
            HTTP_500_INTERNAL_SERVER_ERROR: Se ocorrer um erro ao obter a resposta.

        Example (Success):
            {
                "status": "success",
                "answer": "A resposta gerada pelo chatbot com base no histórico do chat."
            }

        Example (Error - Pergunta não fornecida):
            {
                "error": "Pergunta é necessária"
            }

        Example (Error - Falha ao obter resposta):
            {
                "error": "Não foi possível obter uma resposta: Detalhes do erro."
            }
        """
        question = request.data.get("question")

        if not question:
            return Response({"error": "Pergunta é necessária"}, status=status.HTTP_400_BAD_REQUEST)

        # Recuperar o ChatDetails com base no thread_id e no usuário autenticado
        chat = get_object_or_404(ChatDetails, thread_id=thread_id, user=request.user)

        try:
            answer = get_anwser(str(chat.thread_id), question)
        except Exception as e:
            print(f"Error {e}")
            return Response({"error": f"Não foi possível obter uma resposta: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'status': 'success', 'answer': answer}, status=status.HTTP_200_OK)

class TelegraChatbotView(APIView):
    none = None