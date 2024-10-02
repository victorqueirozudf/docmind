from django.contrib.messages.context_processors import messages
from django.core.serializers import serialize
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import MessageTalkPdf
from .serializers import MessageTalkPdfSerializer

from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
import os

from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from rest_framework.parsers import MultiPartParser

# carrega o meu arquivo .env, que contem minha chave openai
load_dotenv(find_dotenv())

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

        """# essa variavel é responsável por criar uma mensagem no nosso objeto
        new_message = MessageTalkPdf.objects.create(
            message = curiosidade_da_openai(),
            created_at = timezone.now()
        )"""

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

class PDFProcessView(APIView):
    parser_classes = [MultiPartParser]

    def get_pdf_text(self, pdf_docs):
        text = ""
        for pdf in pdf_docs:
            pdf_reader = PdfReader(pdf)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text

    def get_text_chunks(self, text):
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=512,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
        return chunks

    def get_vectorstore(self, text_chunks):
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
        return vectorstore

    def get_conversation_chain(self, vectorstore):
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)
        memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
        conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever(),
            memory=memory
        )
        return conversation_chain

    def post(self, request, *args, **kwargs):
        pdf_files = request.FILES.getlist('pdfs')
        question = request.data.get('question', '')

        # Extrai texto dos PDFs
        raw_text = self.get_pdf_text(pdf_files)
        text_chunks = self.get_text_chunks(raw_text)

        # Cria o vectorstore
        vectorstore = self.get_vectorstore(text_chunks)

        # Gera resposta com o modelo
        conversation_chain = self.get_conversation_chain(vectorstore)
        raw_answer = conversation_chain({'question': question})
        answer = raw_answer['chat_history'][-1].content
        print(answer)
        print(pdf_files)
        # Retorna a resposta em JSON
        return JsonResponse({'status': 'success', 'answer': answer}, status=status.HTTP_201_CREATED)
