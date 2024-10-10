# DOCMIND

O projeto DocMind é um aplicativo que permite que você converse com seus PDF, aumentando, assim, sua produtividade em diversos tipos de trabalho. Ainda estamos em fase de desenvolvimento ;)

## Como executar

Primeiramente, é necessário ter instalado no seu computador: Python V >= 3.10 , Node.js >= ADICIONAR_VERSAO.

## Como executar o Backend

Para executar o backend, é bem simples. Após baixar o nosso projeto, você vai na raíz. Na raíz, digite os seguintes comandos: **cd backend**

Para criar o ambiente virtual: **python -m venv venv**

Sempre que você for executar o aplicativo, é necessário executar esse comando para iniciar o ambiente virtual: **.\venv\Scripts\activate**

Para desativar o ambiente virtual: **deactivate**

Com o ambiente virtual criado, vamos baixar as bibliotecas necessárias para nosso aplicativo e executar o nosso aplicativo

***pip install -r requirements.txt***

***python manage.py makemigrations***

***python manage.py migrate***

***python manage.py runserver***

Após executar esses comando, ainda na raíz, você vai criar um arquivo chamado **".env"**. Neste arquivo, você vai colocar a seguinte variável: ***OPENAI_API_KEY = "sua_api"***. É aqui onde vamos guardar nossa chave de segurança

## Como executar o Frontend

Para executar o backend, é bem simples. Após baixar o nosso projeto, você vai na raíz. Na raíz, digite os seguintes comandos: **cd backend**

Digite **npm install**

Depois, digite **npm start**
