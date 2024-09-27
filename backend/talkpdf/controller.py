from PyPDF2 import PdfReader

from dotenv import load_dotenv, find_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS

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

def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain
"""
def load_vectorstore_from_file(course):
    filename = f"engenharia_de_controle_e_automacao.pkl" # Fallback will be engenharia de controle e automação

    if course.lower() == "engenharia de controle e automação":
        filename = f"engenharia_de_controle_e_automacao.pkl"

    elif course.lower() == "engenharia química":
        filename = f"engenharia_quimica.pkl"

    with open(filename, "rb") as f:
        vectorstore = pickle.load(f)
    return vectorstore

def load_vectorstore(course, pdf_docs):
    raw_text = get_pdf_text(pdf_docs)
    text_chunks = get_text_chunks(raw_text)
    vectorstore = get_vectorstore(text_chunks)

    # Save the vectorstore to a file
    if course.lower() == "engenharia de controle e automação":
        with open("engenharia_de_controle_e_automacao.pkl", "wb") as f:
            pickle.dump(vectorstore, f)

    elif course.lower() == "engenharia química":
        with open("engenharia_quimica.pkl", "wb") as f:
            pickle.dump(vectorstore, f)

    return vectorstore"""

#def ask_question():
    # Obtém o arquivo PDF e a pergunta
pdf_file = [f'Profile.pdf']

# Salva o arquivo PDF
#pdf_path = default_storage.save(f"temp/{pdf_file.name}", pdf_file)

# Processa o PDF
raw_text = get_pdf_text(pdf_file)
text_chunks = get_text_chunks(raw_text)
vectorstore = get_vectorstore(text_chunks)

# Cria a cadeia de conversação
while True:
    question = str(input('Faça sua pergunta: '))
    conversation_chain = get_conversation_chain(vectorstore)
    raw_answer = conversation_chain({'question': question})
    answer = raw_answer['chat_history'][-1].content
    print(answer)

