import os
import io
from langchain_core.messages import HumanMessage
from langchain.text_splitter import CharacterTextSplitter
from langgraph.graph import START, MessagesState, StateGraph
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from pypdf import PdfReader
import tiktoken

temp_dir = os.path.dirname(os.path.abspath(__file__))
temp_dir = os.path.dirname(os.path.dirname(temp_dir))
temp_dir = os.path.join(temp_dir, 'temp')
os.makedirs(temp_dir, exist_ok=True)

# Define o número de tokens de um texto
def num_tokens_from_string(string: str) -> int:
    # Returns the number of tokens in a text string.
    encoding = tiktoken.encoding_for_model("gpt-4o-mini")
    num_tokens = len(encoding.encode(string))
    return num_tokens

"""RESPONSÁVEIS POR CRIAR OS ARQUIVOS PARA PESQUISA DE DADOS"""
def get_vectorstore_from_files(pdf_docs, thread_id):
    text = ""

    # Verifica se é uma lista de arquivos ou um único arquivo
    if not isinstance(pdf_docs, list):
        pdf_docs = [pdf_docs]

    print(f"Recebendo {len(pdf_docs)} documentos PDF para o thread_id {thread_id}.\n")

    for pdf in pdf_docs:
        # Verifica se o pdf tem o atributo 'name', caso contrário, assume que é um objeto bytes
        if hasattr(pdf, 'name'):
            print(f"Lendo arquivo: {pdf.name}")
        else:
            print(f"Lendo arquivo anônimo (sem nome), tamanho: {len(pdf)} bytes")

        # Lê o conteúdo do arquivo em memória
        pdf_bytes = pdf.read() if hasattr(pdf, 'read') else pdf  # Se for um arquivo, chama o read()
        pdf_stream = io.BytesIO(pdf_bytes)
        #print(f"Tamanho do arquivo em bytes: {len(pdf_bytes)}")

        # Processa o PDF
        pdf_reader = PdfReader(pdf_stream)

        for page in pdf_reader.pages:
            page_text = page.extract_text()
            text += page_text

    # Split do texto em chunks
    #print("Iniciando divisão do texto em chunks...\n")
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1024,
        chunk_overlap=256,
        length_function=len
    )

    chunks = text_splitter.split_text(text)
    #print(f"{len(chunks)} chunks gerados.\n")

    # Criação dos embeddings
    embeddings = OpenAIEmbeddings()

    # Criação da store FAISS
    vectorstore = FAISS.from_texts(texts=chunks, embedding=embeddings)

    # Define o caminho da pasta e do arquivo FAISS
    folder_path = os.path.join(temp_dir, str(thread_id))

    # Cria a pasta se ela não existir
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Pasta criada: {folder_path}\n")

    # Salva o índice FAISS
    vectorstore.save_local(folder_path)
    print(f"Vetores salvos em {folder_path}\n")

    return vectorstore

# Função para carregar o vetor do arquivo FAISS ou criar se não existir
def load_vectorstore_from_file(thread_id):
    folder_path = os.path.join(temp_dir, thread_id)
    file_path = os.path.join(folder_path, "index.pkl")

    # Verifica se o arquivo FAISS já existe
    if os.path.exists(file_path):
        print(f"Carregando vetores do arquivo {folder_path}\n")
        vectorstore = FAISS.load_local(folder_path, OpenAIEmbeddings(), allow_dangerous_deserialization=True)
        return vectorstore
    else:
        print(f"O arquivo {file_path} não existe. Subir arquivo novamente.\n")
        # Caso não exista, cria os vetores e salva o arquivo FAISS
        #return get_vectorstore_from_files(thread_id, pdf_docs)

def call_model(state: MessagesState, vectorstore, question):
    # Modelo de chat
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    # Filtrar apenas HumanMessage
    human_messages = [msg.content for msg in state['messages'] if isinstance(msg, HumanMessage)]

    retriever = vectorstore.as_retriever()
    retrieved_docs = retriever.invoke(state["messages"][-1].content)

    # Ordena os documentos pela ordem de inserção, assumindo que eles têm um campo 'insertion_order'
    sorted_docs = sorted(retrieved_docs, key=lambda doc: doc.metadata.get('insertion_order', 0))

    print(sorted_docs)

    # Concatene os resultados dos documentos recuperados em ordem
    pdf_response = "\n".join([doc.page_content for doc in sorted_docs])

    #memory = model.invoke(state["messages"])
    #print(memory)

    input_user = "Históricos de mensagens passadas: \n " + str(human_messages) + "\n" + str([HumanMessage(content=pdf_response)])

    #print(f"Pergunta: {question}\n\nAqui está um trecho do documento:\n\n{input_user}\n\nPor favor, responda à pergunta com base no documento de forma direta.")

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

    #print(prompt)

    response = model.invoke(prompt)

    input_tokens = num_tokens_from_string(prompt[0][1]) + num_tokens_from_string(prompt[1][1])
    output_tokens = num_tokens_from_string(response.content)

    price_per_one_million = 0.150

    print(f"""Total de tokens e valor total:\nInput: {input_tokens} - US${(input_tokens * price_per_one_million)/1000000:.8f}\nOutput: {output_tokens} - US${(output_tokens * price_per_one_million)/1000000:.8f}\nTotal tokens: {input_tokens + output_tokens} - Total gasto: US${((input_tokens + output_tokens) * price_per_one_million)/1000000:.8f}\n\n""",end="")

    return {"messages": response}