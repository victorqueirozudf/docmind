from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import generics

from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
import os

load_dotenv(find_dotenv())

# Create your views here.
def index(request):

    client = OpenAI(api_key = os.getenv('OPENAI_API_KEY'))

    curiosidade = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um assistente que fala português e é muito curioso."},
            {"role": "user", "content": "Me fala uma curiosidade sobre o jogo grand thelf auto iv."},
        ]
    )

    curiosidade = dict(curiosidade.choices[0].message)

    return HttpResponse(curiosidade['content'])
