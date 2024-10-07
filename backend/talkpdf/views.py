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

class PDFProcessView(APIView):
    def get(self, request, *args, **kwargs):
        """Listar todos os chats ou filtrar por thread_id."""
        thread_id = request.query_params.get("thread_id")

        try:
            if thread_id:
                # Filtrar pelo thread_id específico
                chats = DjCheckpoint.objects.filter(thread_id=thread_id).values('thread_id').distinct()
            else:
                # Listar todos os chats com thread_id distintos
                chats = DjCheckpoint.objects.values('thread_id').distinct()
                print(chats)

            # Retornar apenas os thread_ids distintos
            chat_list = [{"thread_id": chat["thread_id"]} for chat in chats]
            return JsonResponse({"status": "success", "chats": chat_list}, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        # os arquivos que iria receber
        pdf = request.FILES.getlist("pdfs")
        question = request.data.get("question")
        thread_id = request.data.get("thread_id", str(uuid.uuid4()))  # Usar 123 como padrão se não for passado

        # Verificar se o PDF e a pergunta foram fornecidos
        if not pdf or not question:
            return Response({"error": "PDF e pergunta são necessários"}, status=status.HTTP_400_BAD_REQUEST)

        # Criar uma instância do DjangoSaver para checkpoints
        checkpointer = DjangoSaver()

        # Definir um novo grafo
        workflow = StateGraph(state_schema=MessagesState)

        # Modelo de chat
        model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

        def call_model(state: MessagesState, vectorstore):
            retriever = vectorstore.as_retriever()
            retrieved_docs = retriever.invoke(state["messages"][-1].content)

            # Ordena os documentos pela ordem de inserção, assumindo que eles têm um campo 'insertion_order'
            sorted_docs = sorted(retrieved_docs, key=lambda doc: doc.metadata.get('insertion_order', 0))

            # Concatene os resultados dos documentos recuperados em ordem
            pdf_response = "\n".join([doc.page_content for doc in sorted_docs])

            #print(pdf_response)

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

            #print("O que é mandado: " + prompt)

            # Chama o modelo passando todas as mensagens do estado
            response = model.invoke(prompt)

            return {"messages": response}

        # Definir os nós no grafo
        workflow.add_edge(START, "model")
        workflow.add_node("model", lambda state: call_model(state, vectorstore))  # Passar o vectorstore dentro da função

        print(thread_id)

        config = {"configurable": {"thread_id": thread_id}}

        app = workflow.compile(checkpointer=checkpointer)

        # Extraindo e processando o PDF
        curriculos = extract_text_from_pdf(pdf)
        chucks = get_text_chunks(curriculos)
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