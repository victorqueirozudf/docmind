# views.py

import uuid
import shutil
import os

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django.shortcuts import get_object_or_404

from .models import ChatCheckpoint, ChatDetails
from .serializers import ChatDetailsSerializer, ChatCheckpointSerializer
from .rag import get_vectorstore_from_files, get_anwser

class PDFChatView(APIView):
    """
    View para gerenciar chats baseados em PDFs para usuários autenticados.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """
        Recupera e lista todos os chats do usuário autenticado.

        **URL:** `GET /api/chats/`

        **Cabeçalhos HTTP:**
            - Authorization: 'Bearer <token>'

        Args:
            request (HttpRequest): O objeto HTTP da requisição.
            *args: Argumentos posicionais adicionais.
            **kwargs: Argumentos nomeados adicionais.

        Returns:
            Response: Resposta HTTP contendo a lista de chats serializados e o status 200 OK.

        **Exemplo de Resposta:**
        ```json
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
        ```
        """
        chats = ChatDetails.objects.filter(user=request.user)
        serializer = ChatDetailsSerializer(chats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        Cria um novo chat associado a múltiplos arquivos PDF enviados e gera os vetores necessários.

        **URL:** `POST /api/chats/`

        **Cabeçalhos HTTP:**
            - Authorization: 'Bearer <token>'
            - Content-Type: 'multipart/form-data'

        **Corpo da Requisição:**
            - chatName: Nome do chat.
            - pdfs: Lista de arquivos PDF a serem enviados.

        Args:
            request (HttpRequest): O objeto HTTP da requisição contendo 'chatName' e 'pdfs'.
            *args: Argumentos posicionais adicionais.
            **kwargs: Argumentos nomeados adicionais.

        Returns:
            Response: Resposta HTTP contendo os dados do chat criado serializados e o status 201 CREATED.

        Raises:
            HTTP_400_BAD_REQUEST: Se nenhum arquivo PDF for fornecido.
            HTTP_500_INTERNAL_SERVER_ERROR: Se ocorrer um erro ao processar os PDFs.

        **Exemplo de Resposta (Sucesso):**
        ```json
        {
            "thread_id": "36e9d38f-413f-4866-8609-8d657ed9fd29",
            "chatName": "Chat de Projeto",
            "path": "/path/to/vectorstore",
            "created_at": "2024-04-27T12:34:56Z"
        }
        ```

        **Exemplo de Erro (PDFs não fornecidos):**
        ```json
        {
            "error": "Ao menos um arquivo PDF é obrigatório."
        }
        ```

        **Exemplo de Erro (Processamento dos PDFs falhou):**
        ```json
        {
            "error": "Erro ao processar os PDFs: Detalhes do erro."
        }
        """
        thread_id = uuid.uuid4()
        chat_name = request.data.get('chat_name')
        pdf_files = request.FILES.getlist('pdfs')  # Obter lista de PDFs enviados

        if not pdf_files:
            return Response({'error': 'Ao menos um arquivo PDF é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

        if ChatDetails.objects.filter(thread_id=thread_id).exists():
            return Response(
                {'error': 'Chat com este thread_id já existe.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Extraia os nomes dos arquivos
        file_names = [file.name for file in pdf_files]

        # Criar a instância de ChatDetails
        chat = ChatDetails.objects.create(
            user=request.user,
            thread_id=thread_id,
            path=os.path.join('temp', str(thread_id)),  # O controller já configura 'temp_dir'
            chat_name=chat_name,
            file_names=file_names  # Adicione os nomes dos arquivos
        )

        # Processar todos os arquivos PDF enviados
        try:
            # Supondo que o controller possa processar múltiplos arquivos de uma vez
            folder_path = get_vectorstore_from_files(pdf_files, thread_id)
        except Exception as e:
            # Se ocorrer um erro durante a criação dos vetores, desfazer a criação do chat
            print(f"Error: {e}")
            chat.delete()
            return Response({'error': f'Erro ao processar os PDFs: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Atualizar o caminho do chat com o caminho retornado pelo controller
        chat.path = folder_path
        chat.save()

        serializer = ChatDetailsSerializer(chat)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, thread_id, *args, **kwargs):
        """
        Deleta um chat específico e seus dados associados.

        **URL:** `DELETE /api/chats/delete/<thread_id>/`

        **Cabeçalhos HTTP:**
            - Authorization: 'Bearer <token>'

        Args:
            request (HttpRequest): O objeto HTTP da requisição.
            thread_id (UUID): O identificador único do chat a ser deletado.
            *args: Argumentos posicionais adicionais.
            **kwargs: Argumentos nomeados adicionais.

        Returns:
            Response: Resposta HTTP com o status 204 NO CONTENT se a exclusão for bem-sucedida.

        Raises:
            HTTP_500_INTERNAL_SERVER_ERROR: Se ocorrer um erro ao deletar os arquivos do chat.

        **Exemplo de Uso:**
            DELETE /api/chats/delete/36e9d38f-413f-4866-8609-8d657ed9fd29/

        **Exemplo de Erro:**
        ```json
        {
            "error": "Erro ao deletar os arquivos do chat: Detalhes do erro."
        }
        ```
        """
        # Recuperar o ChatDetails com base no thread_id e no usuário autenticado
        chat = get_object_or_404(ChatDetails, thread_id=thread_id, user=request.user)

        # Lógica para apagar a pasta associada ao chat usando o controller
        try:
            # Obter o caminho completo da pasta
            folder_path = chat.path
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path, ignore_errors=True)  # Ou crie uma função no controller para isso
        except Exception as e:
            return Response({'error': f'Erro ao deletar os arquivos do chat: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Excluir o chat e seus objetos relacionados devido ao on_delete=models.CASCADE
        chat.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, thread_id, *args, **kwargs):
        """
        Atualiza um chat existente com um novo nome e/ou um novo arquivo PDF, regenerando os vetores necessários.

        **URL:** PUT /api/chats/put/<thread_id>/

        **Cabeçalhos HTTP:**
            - Authorization: 'Bearer <token>'
            - Content-Type: 'multipart/form-data' (se estiver enviando um novo PDF)

        **Corpo da Requisição (opcional):**
            - chatName: Novo nome para o chat.
            - pdfs: Novo arquivo PDF para atualizar o chat.

        Args:
            request (HttpRequest): O objeto HTTP da requisição contendo 'chatName' (opcional) e/ou 'pdfs' (opcional).
            thread_id (UUID): O identificador único do chat a ser atualizado.
            *args: Argumentos posicionais adicionais.
            **kwargs: Argumentos nomeados adicionais.

        Returns:
            Response: Resposta HTTP contendo os dados do chat atualizado serializados e o status 200 OK.

        Raises:
            HTTP_400_BAD_REQUEST: Se nenhum dado for fornecido para atualização.
            HTTP_500_INTERNAL_SERVER_ERROR: Se ocorrer um erro ao processar o PDF ou atualizar o chat.

        **Exemplo de Uso:**
            PUT /api/chats/36e9d38f-413f-4866-8609-8d657ed9fd29/

        **Exemplo de Erro:**

json
        {
            "error": "Nenhum dado fornecido para atualização."
        }

        """
        chat = get_object_or_404(ChatDetails, thread_id=thread_id, user=request.user)

        chat_name = request.data.get('chat_name', chat.chat_name)
        pdf_files = request.FILES.getlist('pdfs')

        if not pdf_files and 'chat_name' not in request.data:
            return Response({'error': 'Nenhum dado fornecido para atualização.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Atualizar o nome do chat, se fornecido
        if 'chat_name' in request.data:
            chat.chat_name = chat_name

        # Se novos PDFs forem fornecidos, processe-os
        if pdf_files:
            try:
                folder_path = get_vectorstore_from_files(pdf_files, thread_id)

                # Extraia os nomes dos arquivos e atualize no banco de dados
                file_names = [file.name for file in pdf_files]
                chat.file_names = file_names

                chat.path = folder_path
            except Exception as e:
                return Response({'error': f'Erro ao processar os PDFs: {str(e)}'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Salvar as alterações no chat
        chat.save()

        serializer = ChatDetailsSerializer(chat)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PDFChatDetailView(APIView):
    """
    View para gerenciar detalhes específicos de um chat, incluindo o histórico de checkpoints e respostas às perguntas dos usuários.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request, thread_id):
        """
        Recupera o histórico de checkpoints de um chat específico.

        **URL:** `GET /api/chats/<thread_id>/`

        **Cabeçalhos HTTP:**
            - Authorization: 'Bearer <token>'

        Args:
            request (HttpRequest): O objeto HTTP da requisição.
            thread_id (UUID): O identificador único do chat cujo histórico será recuperado.

        Returns:
            Response: Resposta HTTP contendo o status de sucesso e a lista de checkpoints serializados com o status 200 OK.

        **Exemplo de Resposta:**
        ```json
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
        ```
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

        **URL:** `PUT /api/chats/<thread_id>/`

        **Cabeçalhos HTTP:**
            - Authorization: 'Bearer <token>'
            - Content-Type: 'application/json'

        **Corpo da Requisição:**
        ```json
        {
            "question": "Sua pergunta aqui"
        }
        ```

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

        **Exemplo de Resposta (Sucesso):**
        ```json
        {
            "status": "success",
            "answer": "A resposta gerada pelo chatbot com base no histórico do chat."
        }
        ```

        **Exemplo de Erro (Pergunta não fornecida):**
        ```json
        {
            "error": "Pergunta é necessária"
        }
        ```

        **Exemplo de Erro (Falha ao obter resposta):**
        ```json
        {
            "error": "Não foi possível obter uma resposta: Detalhes do erro."
        }
        ```
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