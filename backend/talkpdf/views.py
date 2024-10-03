import os
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from langchain_core.messages import HumanMessage
from langchain.text_splitter import CharacterTextSplitter
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from PyPDF2 import PdfReader
from langchain_community.vectorstores import FAISS
from .models import ChatGraph

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=512,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks


def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore


class ChatGraphView(APIView):
    def post(self, request):
        user_id = request.data.get("user_id", str(uuid.uuid4()))  # Gera um novo UUID se não for fornecido
        files = request.FILES.getlist("files")
        question = request.data.get("question")

        # Tenta buscar um grafo existente associado ao user_id
        chat_graph, created = ChatGraph.objects.get_or_create(user_id=user_id)

        # Extrair e indexar texto dos PDFs
        all_documents = []
        for file in files:
            temp_file_path = os.path.join('/tmp', file.name)  # Salva o arquivo temporariamente
            with open(temp_file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            text = extract_text_from_pdf(temp_file_path)
            all_documents.extend(get_text_chunks(text))

        # Atualiza o grafo existente ou cria um novo
        if created:
            # Se um novo grafo foi criado, armazena os documentos
            chat_graph.graph_data = all_documents  # Certifique-se de que graph_data é o campo correto
        else:
            # Se o grafo já existia, atualiza os dados existentes
            existing_documents = get_text_chunks(chat_graph.graph_data)  # Obtenha os documentos existentes
            all_documents = existing_documents + all_documents  # Combine os documentos
            chat_graph.graph_data = all_documents  # Atualize o grafo com novos dados

        chat_graph.save()  # Salva as alterações no grafo

        # Recuperar o grafo existente para uso posterior
        existing_graph_data = chat_graph.graph_data

        # Criar o workflow com o estado existente
        workflow = StateGraph(state_schema=MessagesState)

        # Modelo de chat
        model = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)

        # Função que chama o modelo e busca no PDF
        def call_model(state: MessagesState, vectorstore):
            query = state["messages"][-1].content  # Pegue a última mensagem do usuário
            retriever = vectorstore.as_retriever()
            retrieved_docs = retriever.get_relevant_documents(query)
            pdf_response = "\n".join([doc.page_content for doc in retrieved_docs])  # Concatene os resultados

            response = model.invoke([state["messages"][-1], HumanMessage(
                content=pdf_response)])  # Chama o modelo e inclui os resultados do PDF
            return {"messages": response}

        # Definir os nós no grafo
        workflow.add_edge(START, "model")
        workflow.add_node("model",
                          lambda state: call_model(state, vectorstore))  # Passar o vectorstore dentro da função

        # Adicionando memória
        memory = MemorySaver()

        # Compilando o app
        app = workflow.compile(
            checkpointer=memory
        )

        # Gerar UUID para identificar conversas
        thread_id = uuid.uuid4()
        config = {"configurable": {"thread_id": thread_id}}

        # Indexar os dados do grafo existente
        vectorstore = get_vectorstore(existing_graph_data)

        # Preparar a mensagem do usuário
        input_message = HumanMessage(content=question)

        # Interagir com o modelo
        for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
            response_message = event["messages"][-1].content  # Captura a última mensagem gerada
            return Response({"response": response_message}, status=status.HTTP_200_OK)

        return Response({"error": "Failed to generate response."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)