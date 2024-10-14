# 📄 **DocMind** 

O **DocMind** é um aplicativo que permite que você converse com seus arquivos PDF, aumentando sua produtividade em diversos tipos de trabalho! 🚀 Ainda estamos em fase de desenvolvimento 😉

---

## 🛠️ **Pré-requisitos**

Antes de começar, certifique-se de ter as seguintes ferramentas instaladas em sua máquina:

- [Python](https://www.python.org/) >= 3.10 🐍
- [Node.js](https://nodejs.org/) >= *ADICIONAR_VERSÃO* 🟢

---

## 🚀 **Como executar**

### 🎯 **Backend**

1. Faça o *download* do repositório.
2. Na raiz do projeto, navegue até o diretório do backend:
   ```bash
   cd backend
   ```
3. Crie um ambiente virtual:
   ```bash
   python -m venv venv
   ```
4. Ative o ambiente virtual:
   - No Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - No macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
5. Para desativar o ambiente virtual, use:
   ```bash
   deactivate
   ```
6. Com o ambiente virtual ativado, instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
7. Aplique as migrações do banco de dados:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
8. Agora, inicie o servidor:
   ```bash
   python manage.py runserver
   ```
9. Crie o arquivo `.env` na raiz do projeto e adicione sua chave da API da OpenAI:
   ```plaintext
   OPENAI_API_KEY = "sua_api"
   ```

### 🌐 **Frontend**

1. Na raiz do projeto, navegue até o diretório do *frontend*:
   ```bash
   cd frontend
   ```
2. Instale as dependências do *frontend*:
   ```bash
   npm install
   ```
3. Por fim, inicie o *frontend*:
   ```bash
   npm start
   ```

---

## 💡 **Contribuição**

Sinta-se à vontade para contribuir! 🤝 Vamos construir o **DocMind** juntos para aumentar ainda mais a produtividade de todos!

---

Feito com 💙 pela equipe **DocMind**.

