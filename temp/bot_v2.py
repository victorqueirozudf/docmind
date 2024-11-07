import os
import logging
import uuid
import requests
import openai
from telegram import Update, InputMediaDocument
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from dotenv import load_dotenv

TELEGRAM_BOT_TOKEN = '8082392422:AAEdpZuEgPuEr7PBAUMPB8PxQK_L1o9IU7o'
OPENAI_API_KEY = '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'

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Variáveis de Ambiente
BACKEND_API_URL = 'localhost:8000/'
BACKEND_USERNAME = 'telegram'
BACKEND_PASSWORD = 'aeVflYy+VLOUWwkxgTbNcQ=='

# Estados para ConversationHandler
CHAT_NAME, WAITING_FOR_PDF = range(2)

# Mapeamento de usuários do Telegram para thread_id do backend
user_thread_mapping = {}

# Inicializar Whisper
openai.api_key = OPENAI_API_KEY

def start(update: Update, context: CallbackContext):
    """Envia uma mensagem de boas-vindas e inicia a conversa."""
    update.message.reply_text(
        "Olá! Sou seu assistente. Para começar, envie um arquivo PDF para criar um novo chat."
    )
    return ConversationHandler.END

def login_to_backend():
    """Autentica-se no backend e retorna o access_token."""
    login_url = f"{BACKEND_API_URL}/authentication/login/"
    payload = {
        "username": BACKEND_USERNAME,
        "password": BACKEND_PASSWORD
    }
    try:
        response = requests.post(login_url, json=payload)
        response.raise_for_status()
        access_token = response.json().get('access')
        if not access_token:
            logger.error("Login bem-sucedido, mas access_token não encontrado.")
            return None
        return access_token
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao fazer login no backend: {e}")
        return None

def verify_token(access_token):
    """Verifica se o access_token é válido."""
    verify_url = f"{BACKEND_API_URL}/api/authentication/verify-token/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(verify_url, headers=headers)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Token inválido ou expirado: {e}")
        return False

def create_chat(access_token, chat_name, pdf_file_path):
    """Cria um novo chat no backend com o PDF fornecido."""
    create_chat_url = f"{BACKEND_API_URL}/api/chats/"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    files = {
        'pdfs': open(pdf_file_path, 'rb')
    }
    data = {
        'chatName': chat_name
    }
    try:
        response = requests.post(create_chat_url, headers=headers, files=files, data=data)
        response.raise_for_status()
        chat_data = response.json()
        thread_id = chat_data.get('thread_id')
        return thread_id
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao criar chat: {e}")
        return None

def send_question(access_token, thread_id, question):
    """Envia uma pergunta ao backend e obtém a resposta."""
    send_question_url = f"{BACKEND_API_URL}/api/chats/{thread_id}/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "question": question
    }
    try:
        response = requests.put(send_question_url, headers=headers, json=payload)
        response.raise_for_status()
        answer = response.json().get('answer')
        return answer
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao enviar pergunta: {e}")
        return None

def handle_document(update: Update, context: CallbackContext):
    """Inicia a criação de um novo chat ao receber um PDF."""
    user = update.message.from_user
    document = update.message.document

    if document.mime_type != 'application/pdf':
        update.message.reply_text("Por favor, envie apenas arquivos PDF.")
        return ConversationHandler.END

    # Salvar o PDF localmente temporariamente
    pdf_file = context.bot.get_file(document.file_id)
    pdf_path = os.path.join('temp_pdfs', f"{uuid.uuid4()}_{document.file_name}")
    os.makedirs('temp_pdfs', exist_ok=True)
    pdf_file.download(custom_path=pdf_path)

    # Solicitar o nome do chat
    update.message.reply_text("Por favor, envie um nome para este chat.")
    # Armazenar o caminho do PDF no contexto para uso posterior
    context.user_data['pdf_path'] = pdf_path
    return CHAT_NAME

def receive_chat_name(update: Update, context: CallbackContext):
    """Recebe o nome do chat e cria o chat no backend."""
    user = update.message.from_user
    chat_name = update.message.text.strip()
    pdf_path = context.user_data.get('pdf_path')

    if not pdf_path or not os.path.exists(pdf_path):
        update.message.reply_text("Erro ao processar o PDF. Por favor, tente novamente.")
        return ConversationHandler.END

    # Autenticação com o backend
    access_token = login_to_backend()
    if not access_token:
        update.message.reply_text("Erro ao autenticar no backend. Tente novamente mais tarde.")
        return ConversationHandler.END

    # Verificar se o token é válido
    if not verify_token(access_token):
        update.message.reply_text("Token de autenticação inválido. Por favor, tente novamente.")
        return ConversationHandler.END

    # Criar o chat no backend
    thread_id = create_chat(access_token, chat_name, pdf_path)
    if not thread_id:
        update.message.reply_text("Erro ao criar o chat no backend. Por favor, tente novamente.")
        return ConversationHandler.END

    # Remover o PDF temporário
    os.remove(pdf_path)

    # Mapear o usuário do Telegram para o thread_id
    user_thread_mapping[user.id] = thread_id

    update.message.reply_text(f"Chat '{chat_name}' criado com sucesso! Você pode começar a fazer perguntas.")
    return ConversationHandler.END

def handle_text(update: Update, context: CallbackContext):
    """Handle text messages as questions to the chatbot."""
    user = update.message.from_user
    question = update.message.text.strip()

    thread_id = user_thread_mapping.get(user.id)
    if not thread_id:
        update.message.reply_text("Você não tem um chat ativo. Por favor, envie um PDF para criar um chat.")
        return

    # Autenticação com o backend
    access_token = login_to_backend()
    if not access_token:
        update.message.reply_text("Erro ao autenticar no backend. Tente novamente mais tarde.")
        return

    # Verificar se o token é válido
    if not verify_token(access_token):
        update.message.reply_text("Token de autenticação inválido. Por favor, tente novamente.")
        return

    # Enviar a pergunta ao backend
    answer = send_question(access_token, thread_id, question)
    if answer:
        update.message.reply_text(answer)
    else:
        update.message.reply_text("Desculpe, não consegui obter uma resposta no momento. Tente novamente mais tarde.")

def handle_voice(update: Update, context: CallbackContext):
    """Handle voice messages: transcribe and send as question."""
    user = update.message.from_user
    voice = update.message.voice

    # Baixar o arquivo de áudio
    audio_file = context.bot.get_file(voice.file_id)
    audio_path = os.path.join('temp_audio', f"{uuid.uuid4()}.ogg")
    os.makedirs('temp_audio', exist_ok=True)
    audio_file.download(custom_path=audio_path)

    # Transcrever o áudio usando Whisper
    try:
        result = whisper_model.transcribe(audio_path)
        question = result['text'].strip()
        if not question:
            update.message.reply_text("Desculpe, não consegui transcrever o áudio. Tente novamente.")
            os.remove(audio_path)
            return
    except Exception as e:
        logger.error(f"Erro ao transcrever áudio: {e}")
        update.message.reply_text("Desculpe, ocorreu um erro ao processar seu áudio.")
        os.remove(audio_path)
        return

    # Remover o áudio temporário
    os.remove(audio_path)

    # Enviar a pergunta como se fosse uma mensagem de texto
    update.message.reply_text(f"Transcrição da sua pergunta: {question}")

    # Obter thread_id do usuário
    thread_id = user_thread_mapping.get(user.id)
    if not thread_id:
        update.message.reply_text("Você não tem um chat ativo. Por favor, envie um PDF para criar um chat.")
        return

    # Autenticação com o backend
    access_token = login_to_backend()
    if not access_token:
        update.message.reply_text("Erro ao autenticar no backend. Tente novamente mais tarde.")
        return

    # Verificar se o token é válido
    if not verify_token(access_token):
        update.message.reply_text("Token de autenticação inválido. Por favor, tente novamente.")
        return

    # Enviar a pergunta ao backend
    answer = send_question(access_token, thread_id, question)
    if answer:
        update.message.reply_text(answer)
    else:
        update.message.reply_text("Desculpe, não consegui obter uma resposta no momento. Tente novamente mais tarde.")

def cancel(update: Update, context: CallbackContext):
    """Cancela a conversa."""
    user = update.message.from_user
    update.message.reply_text('Operação cancelada. Você pode iniciar novamente enviando um PDF.')
    return ConversationHandler.END

def main():
    """Inicia o bot."""
    # Autenticação com o backend
    access_token = login_to_backend()
    if not access_token:
        logger.error("Falha ao autenticar com o backend. O bot não será iniciado.")
        return

    # Verificar se o token é válido
    if not verify_token(access_token):
        logger.error("Token de autenticação inválido. O bot não será iniciado.")
        return

    # Inicializar o Updater e Dispatcher
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Configurar ConversationHandler para criação de chat
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.document.mime_type("application/pdf"), handle_document)],
        states={
            CHAT_NAME: [MessageHandler(Filters.text & ~Filters.command, receive_chat_name)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(conv_handler)
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
    dp.add_handler(MessageHandler(Filters.voice, handle_voice))

    # Iniciar o Bot
    updater.start_polling()
    logger.info("Bot iniciado.")
    updater.idle()

if __name__ == '__main__':
    main()
