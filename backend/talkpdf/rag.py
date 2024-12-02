# controller.py

import os
import io
from langchain_core.messages import HumanMessage, AIMessage
from langchain.text_splitter import CharacterTextSplitter
from langgraph.graph import START, MessagesState, StateGraph
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from pypdf import PdfReader
import tiktoken
from .checkpointer import DjangoSaver


# Criação da pasta temp (./docmind/temp)
temp_dir = os.path.dirname(os.path.abspath(__file__))
temp_dir = os.path.dirname(os.path.dirname(temp_dir))
temp_dir = os.path.join(temp_dir, 'temp')
os.makedirs(temp_dir, exist_ok=True)

# Define o número de tokens de um texto
def num_tokens_from_string(string: str) -> int:
    # Retorna o número de tokens em uma string de texto.
    encoding = tiktoken.encoding_for_model("gpt-4o-mini")
    num_tokens = len(encoding.encode(string))
    return num_tokens

def get_vectorstore_from_files(pdf_docs, thread_id):
    chunks = []
    metadatas = []

    # Verifica se é uma lista de arquivos ou um único arquivo
    if not isinstance(pdf_docs, list):
        pdf_docs = [pdf_docs]

    print(f"Recebendo {len(pdf_docs)} documentos PDF para o thread_id {thread_id}.\n")

    for pdf in pdf_docs:
        # Determina o nome do arquivo
        if hasattr(pdf, 'name'):
            file_name = pdf.name
            print(f"Lendo arquivo: {file_name}")
        else:
            file_name = "arquivo_anônimo"
            print(f"Lendo arquivo anônimo (sem nome), tamanho: {len(pdf)} bytes")

        # Lê o conteúdo do arquivo em memória
        pdf_bytes = pdf.read() if hasattr(pdf, 'read') else pdf  # Se for um arquivo, chama o read()
        pdf_stream = io.BytesIO(pdf_bytes)

        # Processa o PDF
        pdf_reader = PdfReader(pdf_stream)

        for page_number, page in enumerate(pdf_reader.pages, start=1):
            page_text = page.extract_text()
            if not page_text:
                continue  # Pula páginas sem texto

            # Split do texto em chunks
            text_splitter = CharacterTextSplitter(
                separator="\n",
                chunk_size=1024,
                chunk_overlap=256,
                length_function=len
            )
            page_chunks = text_splitter.split_text(page_text)

            # Adiciona os chunks e seus metadados
            for chunk in page_chunks:
                cleaned_chunk = chunk.replace('\xa0', ' ').strip()
                if cleaned_chunk:  # Verifica se o chunk não está vazio
                    chunks.append(cleaned_chunk)
                    metadatas.append({
                        "source": file_name,
                        "page": page_number
                        # Adicione outros metadados aqui, se necessário
                    })
    # Criação dos embeddings
    embeddings = OpenAIEmbeddings()

    # Criação da store FAISS com metadados
    vectorstore = FAISS.from_texts(texts=chunks, embedding=embeddings, metadatas=metadatas)

    # Define o caminho da pasta e do arquivo FAISS
    folder_path = os.path.join(temp_dir, str(thread_id))

    # Cria a pasta se ela não existir
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Pasta criada: {folder_path}\n")

    # Salva o índice FAISS
    vectorstore.save_local(folder_path)
    print(f"Vetores salvos em {folder_path}\n")

    return folder_path  # Retorna o caminho do índice FAISS

# Função para carregar o vetor do arquivo FAISS ou criar se não existir
def load_vectorstore_from_file(thread_id):
    # definido caminho para o vetor
    folder_path = os.path.join(temp_dir, thread_id)
    file_path = os.path.join(folder_path, "index.pkl")

    # Verifica se o arquivo FAISS já existe
    if os.path.exists(file_path):
        print(f"Carregando vetores do arquivo {folder_path}\n")
        vectorstore = FAISS.load_local(folder_path, OpenAIEmbeddings(), allow_dangerous_deserialization=True)
        return vectorstore, folder_path
    else:
        print(f"O arquivo {file_path} não existe. Subir arquivo novamente.\n")
        # Caso não exista, cria os vetores e salva o arquivo FAISS
        # É necessário passar os pdf_docs aqui se for para criar
        # Exemplo: return get_vectorstore_from_files(pdf_docs, thread_id)
        return None, folder_path  # Ajuste conforme a lógica desejada

def call_model(state: MessagesState, vectorstore, question):
    # Modelo de chat
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    # Filtrar apenas HumanMessage
    human_messages = [msg.content for msg in state['messages'] if isinstance(msg, HumanMessage)]
    ai_messages = [msg.content for msg in state['messages'] if isinstance(msg, AIMessage)][-3:]

    retriever = vectorstore.as_retriever()
    retrieved_docs = retriever.invoke(state["messages"][-1].content)

    # Concatene os resultados dos documentos recuperados em ordem
    pdf_response = "\n\n".join([
    f"**Fonte:** {doc.metadata.get('source', 'Desconhecido')} - **Página:** {doc.metadata.get('page', 'N/A')}\n{doc.page_content}"
        for doc in retrieved_docs
    ])


    input_user = "Históricos de mensagens passadas: \n " + str(human_messages)

    prompt = [
        (
            "system",
            "Você é um assistente especializado em leitura de documentos PDF. Responda às perguntas do usuário de forma clara, concisa e relevante, limitando a resposta aos pontos mais importantes."
        ),
        (
            "human",
            f"""
                ***Pergunta:*** {question}\n\n
                ***Aqui está um trecho do documento:***\n{pdf_response}\n
                ***Históricos de perguntas passadas:***\n {input_user}
                ***Históricos das últimas três respostas do chatbot:***\n {ai_messages}
                Por favor, responda à pergunta com base no documento de forma direta.
            """
        )
    ]

    print(prompt)
    
    response = model.invoke(prompt)

#    input_tokens = num_tokens_from_string(prompt[0][1]) + num_tokens_from_string(prompt[1][1])
#   output_tokens = num_tokens_from_string(response.content)

#    price_per_one_million = 0.150

    #print(f"""Total de tokens e valor total:
#Input: {input_tokens} - US${(input_tokens * price_per_one_million)/1000000:.8f}
#Output: {output_tokens} - US${(output_tokens * price_per_one_million)/1000000:.8f}
#Total tokens: {input_tokens + output_tokens} - Total gasto: US${((input_tokens + output_tokens) * price_per_one_million)/1000000:.8f}\n\n""", end="")

    return {"messages": response}

def get_anwser(thread_id, question):
    vectorstore, folder_path = load_vectorstore_from_file(thread_id)
    if not vectorstore:
        # Lógica para carregar ou criar o vectorstore se não existir
        # Por exemplo, se você tiver acesso aos pdf_docs aqui, você poderia chamar get_vectorstore_from_files
        pass  # Implemente conforme necessário

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
    answer = events[-1]["messages"][-1].content if events else "Sem resposta disponível"

    return answer
