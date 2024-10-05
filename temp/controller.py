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
    pdf_folder_path = f"/temp"
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
    question = "" #str(input('Faça sua pergunta: '))
    conversation_chain = get_conversation_chain(vectorstore)
    raw_answer = conversation_chain({'question': question})
    try:
        print(raw_answer['chat_history'].content)
    except:
        print("Deu ruim e foda-se!")
        pass
    answer = raw_answer['chat_history'][-1].content
    print(answer)



# funções originais da nossas views
"""
# função simples para teste, neste, com um prompt já pré-determinado, gero um mensagem da api da openai
def curiosidade_da_openai(input) -> str:

    client = OpenAI(api_key = os.getenv('OPENAI_API_KEY'))

    input = str(input)

    curiosidade = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um assistente que fala português e é muito curioso."},
            {"role": "user", "content": input},
        ]
    )

    curiosidade = dict(curiosidade.choices[0].message)

    return curiosidade['content']

# Create your views here. View para teste
def index(request):

    client = OpenAI(api_key = os.getenv('OPENAI_API_KEY'))

    curiosidade = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um assistente que fala português e é muito curioso."},
            {"role": "user", "content": "Me fala uma curiosidade aleatória sobre história."},
        ]
    )

    curiosidade = dict(curiosidade.choices[0].message)

    return HttpResponse(curiosidade['content'])

# Classe para uma api simples, com o objetivo de retornar uma mensagem da função curiosidade_da_openai
class MessageTalkPdfView(APIView):

    # neste metodo, e obtido nossa mensage, o metodo get retorna todos os dados quando requisitado
    def get(self, request, *args, **kwargs):

        ""# essa variavel é responsável por criar uma mensagem no nosso objeto
        new_message = MessageTalkPdf.objects.create(
            message = curiosidade_da_openai(),
            created_at = timezone.now()
        )""

        # query para retornar todas os dados do nosso metodo
        messages = MessageTalkPdf.objects.all()

        # o serializers serve para padronizar os dados dos nosso objetos, ele os transforma em json
        serializers = MessageTalkPdfSerializer(messages, many=True)

        # aqui é retornado o resultado da nossa consulta
        return Response({'status': 'success', "MessageTalkPdf": serializers.data}, status=200)

    def post(self, request, *args, **kwargs):
        user_input = request.data.get('text', '')  # Recebe o texto do usuário

        # Lógica para gerar uma resposta com base na entrada do usuário
        if user_input == '':
            response_message = curiosidade_da_openai('Me manda uma mensagem de motivação, por favor.')
        else:
            response_message = curiosidade_da_openai(user_input)

        print('Texto recebido:', user_input)

        # Cria um dicionário com os dados que serão validados pelo serializer
        message_data = {
            'message': response_message,
        }

        # Usa o serializer para criar a nova mensagem
        serializer = MessageTalkPdfSerializer(data=message_data)

        if serializer.is_valid():
            serializer.save()  # Salva a nova mensagem no banco de dados
            return Response({'status': 'success', 'message': response_message}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
"""