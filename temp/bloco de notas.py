import uuid
from langchain_core.messages import HumanMessage
from langchain.text_splitter import CharacterTextSplitter
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_openai import ChatOpenAI, OpenAIEmbeddings  # Atualizado para usar o novo pacote
from PyPDF2 import PdfReader
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

def lista_curriculos():
    print("Loading data...")
    pdf_folder_path = f"C:\\docmind\\temp"
    print(os.listdir(pdf_folder_path))

    # Load multiple PDF files
    loaders = [os.path.join(pdf_folder_path, fn) for fn in os.listdir(pdf_folder_path) if fn.endswith('.pdf')]

    print(loaders)

    all_documents = []

    for file in loaders:
        text = ""
        pdf_reader = PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()

        # Define the text splitter
        text_splitter = CharacterTextSplitter(
            separator="\n\n",
            chunk_size=800,
            chunk_overlap=100,
            length_function=len,
        )

        # Since text_splitter expects a list of documents, wrap text in a dictionary
        documents = text_splitter.split_text(text)
        all_documents.extend(documents)

    return all_documents

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=512,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

# Função para ler e extrair texto de PDFs
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Indexar o texto extraído com FAISS
def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

# Definir um novo grafo
workflow = StateGraph(state_schema=MessagesState)

# Modelo de chat
model = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)

# Função que chama o modelo e busca no PDF
def call_model(state: MessagesState, vectorstore):
    query = state["messages"][-1].content  # Pegue a última mensagem do usuário
    retriever = vectorstore.as_retriever()
    retrieved_docs = retriever.get_relevant_documents(query)
    pdf_response = "\n".join([doc.page_content for doc in retrieved_docs])  # Concatene os resultados

    response = model.invoke([state["messages"][-1], HumanMessage(content=pdf_response)])  # Chama o modelo e inclui os resultados do PDF
    return {"messages": response}

# Definir os nós no grafo
workflow.add_edge(START, "model")
workflow.add_node("model", lambda state: call_model(state, vectorstore))  # Passar o vectorstore dentro da função

# Adicionando memória
memory = MemorySaver()

# Compilando o app
app = workflow.compile(
    checkpointer=memory
)

# Gerar UUID para identificar conversas
thread_id = uuid.uuid4()
config = {"configurable": {"thread_id": thread_id}}

# Extrair texto de um PDF e indexar
curriculos = lista_curriculos() # Substitua pelo caminho do seu PDF
vectorstore = get_vectorstore(curriculos)

# Agora, podemos conversar com base no PDF e a conversa será lembrada
while True:
    question = str(input("Faça sua pergunta: "))
    input_message = HumanMessage(content=question)
    for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
        print(event)
        event["messages"][-1].pretty_print()


"""import uuid

# from IPython.display import Image, display
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_openai import OpenAI, ChatOpenAI
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# Define a new graph
workflow = StateGraph(state_schema=MessagesState)

# Define a chat model
model = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)


# Define the function that calls the model
def call_model(state: MessagesState):
    response = model.invoke(state["messages"])
    # We return a list, because this will get added to the existing list
    return {"messages": response}


# Define the two nodes we will cycle between
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)


# Adding memory is straight forward in langgraph!
memory = MemorySaver()

app = workflow.compile(
    checkpointer=memory
)


# The thread id is a unique key that identifies
# this particular conversation.
# We'll just generate a random uuid here.
# This enables a single application to manage conversations among multiple users.
thread_id = uuid.uuid4()
config = {"configurable": {"thread_id": thread_id}}


input_message = HumanMessage(content="Olá, sou o victor!")
for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
    event["messages"][-1].pretty_print()

# Here, let's confirm that the AI remembers our name!
input_message = HumanMessage(content="Qual é meu nome?")
for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
    event["messages"][-1].pretty_print()

input_message = HumanMessage(content="Tenho 24 anos de idade, e você?")
for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
    event["messages"][-1].pretty_print()

input_message = HumanMessage(content="Consegue lembrar minha idade?")
for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
    event["messages"][-1].pretty_print()
"""