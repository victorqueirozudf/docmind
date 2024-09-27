from django.contrib.messages.context_processors import messages
from django.core.serializers import serialize
from django.shortcuts import render
from django.http import HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import MessageTalkPdf
from .serializers import MessageTalkPdfSerializer

from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
import os

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
            #'created_at': timezone.now()
        }

        # Usa o serializer para criar a nova mensagem
        serializer = MessageTalkPdfSerializer(data=message_data)

        if serializer.is_valid():
            serializer.save()  # Salva a nova mensagem no banco de dados
            return Response({'status': 'success', 'message': response_message}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
