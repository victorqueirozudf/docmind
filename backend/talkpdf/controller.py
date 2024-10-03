from PyPDF2 import PdfReader

from dotenv import load_dotenv, find_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

from langchain_community.vectorstores import FAISS

from langchain.text_splitter import CharacterTextSplitter
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

import pickle
import os

load_dotenv(find_dotenv())

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
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


def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore


def get_conversation_chain(vectorstore):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain

# Processa o PDF
text_chunks = lista_curriculos()
vectorstore = get_vectorstore(text_chunks)

# Cria a cadeia de conversação
while True:
    question = str(input('Faça sua pergunta: '))
    conversation_chain = get_conversation_chain(vectorstore)
    raw_answer = conversation_chain({'question': question})
    try:
        print(raw_answer['chat_history'].content)
    except:
        print("Deu ruim e foda-se!")
        pass
    answer = raw_answer['chat_history'][-1].content
    print(answer)
