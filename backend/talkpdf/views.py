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
from PyPDF2 import PdfReader
from langchain_community.vectorstores import FAISS
from .checkpointer import DjangoSaver
from dotenv import load_dotenv, find_dotenv
from .models import DjCheckpoint, DjWrite

load_dotenv(find_dotenv())

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


class PDFProcessView(APIView):
    def get(self, request, *args, **kwargs):
        """Listar todos os chats ou filtrar por thread_id."""
        thread_id = request.query_params.get("thread_id")

        try:
            if thread_id:
                # Filtrar pelo thread_id específico e retornar as mensagens associadas
                chats = DjCheckpoint.objects.filter(thread_id=thread_id).values('thread_id', 'metadata')
                print("Filtrando por thread_id específico")
                #print(chats)  # Verificando os chats retornados
            else:
                # Listar todos os chats com thread_id distintos
                chats = DjCheckpoint.objects.values('thread_id').distinct()
                print("Listando todos os thread_ids distintos")
                #print(chats)

            # Se thread_id for fornecido, retornar as mensagens
            if thread_id:
                chat_data = []
                for chat in chats:
                    # Convertendo metadata de string JSON para dicionário
                    metadata = json.loads(chat['metadata'])

                    # Tentando acessar o content dentro da estrutura JSON
                    try:
                        content = metadata['writes']['model']['messages']['kwargs']['content']
                    except (KeyError, TypeError):
                        content = None  # Caso o campo não exista ou a estrutura não esteja correta

                    # Adicionando os dados formatados na lista
                    chat_data.append({
                        "thread_id": chat["thread_id"],
                        "content": content
                    })

                print(chat_data)
                return JsonResponse({"status": "success", "chat": chat_data}, status=status.HTTP_200_OK)
            else:
                # Retornar apenas os thread_ids distintos
                chat_list = [{"thread_id": chat["thread_id"]} for chat in chats]
                return JsonResponse({"status": "success", "chats": chat_list}, status=status.HTTP_200_OK)

        except Exception as e:
            print(str(e))
            return JsonResponse({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        # os arquivos que iria receber
        pdf = request.FILES.getlist("pdfs")
        question = request.data.get("question")
        thread_id = request.data.get("thread_id", str(uuid.uuid4()))  # Usar 123 como padrão se não for passado

        print(thread_id)

        # Verificar se o PDF e a pergunta foram fornecidos
        if not pdf or not question:
            return Response({"error": "PDF e pergunta são necessários"}, status=status.HTTP_400_BAD_REQUEST)

        # Criar uma instância do DjangoSaver para checkpoints
        checkpointer = DjangoSaver()

        # Definir um novo grafo
        workflow = StateGraph(state_schema=MessagesState)

        # Definir os nós no grafo
        workflow.add_edge(START, "model")
        workflow.add_node("model", lambda state: call_model(state, vectorstore, question))  # Passar o vectorstore dentro da função

        config = {"configurable": {"thread_id": thread_id}}

        app = workflow.compile(checkpointer=checkpointer)

        # Extraindo e processando o PDF
        files = extract_text_from_pdf(pdf)
        chucks = get_text_chunks(files)
        vectorstore = get_vectorstore(chucks)

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

        return JsonResponse({'status': 'success', 'answer': answer}, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        """Apagar um chat baseado no thread_id."""
        thread_id = request.data.get("thread_id")

        if not thread_id:
            return JsonResponse({"status": "error", "message": "O thread_id é necessário para apagar um chat"},
                                status=status.HTTP_400_BAD_REQUEST)

        try:
            # Buscar o chat no banco de dados
            chat = DjCheckpoint.objects.filter(thread_id=thread_id)
            chat.delete()  # Apagar o chat
            return JsonResponse({"status": "success", "message": f"Chat {thread_id} apagado com sucesso"},
                                status=status.HTTP_200_OK)
        except DjCheckpoint.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Chat não encontrado"}, status=status.HTTP_404_NOT_FOUND)

class TelegramBotView(APIView):
    nome = None

class PDFExtractorView(APIView):
    nome = None