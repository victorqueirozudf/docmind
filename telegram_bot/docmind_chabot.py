import os
from functools import wraps
from dotenv import load_dotenv
import re
import requests
import openai
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from base64 import b64encode
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
)

# Load environment variables
load_dotenv()

# Ensure the temp directory exists
if not os.path.exists('./temp/'):
    os.makedirs('./temp/')

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
API_LOGIN_URL = os.getenv('API_LOGIN_URL')  # Endpoint for authentication
API_BASE_URL = os.getenv('API_BASE_URL')    # Base URL for other API endpoints
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
CYPHER_KEY = os.getenv('KEY_CRYPTOGRAPHY')  # AES Key for encryption (32 bytes for AES-256)
CYPHER_IV = os.getenv('IV_CRYPTOGRAPHY')    # AES IV for encryption (16 bytes for AES)

# States for ConversationHandler
WAITING_FOR_DOCUMENT = 1
WAITING_FOR_CHAT_NAME = 2
LIST_CHAT_WAITING_FOR_SELECTION = 3
ASKING_QUESTION = 4  # State for handling questions
DELETE_CHAT_WAITING_FOR_SELECTION = 5
DELETE_CHAT_CONFIRMATION = 6
SELECT_CHAT = 7
CHOOSE_UPDATE = 8
UPDATE_NAME = 9
UPDATE_DOCUMENT = 10
CONFIRM_UPDATE = 11

# States for Authentication
AUTH_USERNAME_STATE, AUTH_PASSWORD_STATE = range(12, 14)


def escape_markdown(text):
    """
    Escapes special characters for MarkdownV2 to prevent formatting errors in Telegram,
    excluding asterisks used for bold.
    """
    # Remove '*' from characters to be escaped to allow bold
    escape_chars = r'_[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)


def get_audio_answer(audio_path):
    """
    Transcribes audio using OpenAI's Whisper and returns the transcription.
    """
    openai.api_key = OPENAI_API_KEY

    try:
        with open(audio_path, "rb") as audio_file:
            transcription = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file
            )
        print(f"Transcrição do áudio: {transcription['text']}")
        return transcription['text']
    except Exception as e:
        print(f"Erro ao transcrever o áudio: {e}")
        raise e  # Propaga a exceção para ser tratada na função chamadora


def encrypt_password(password: str) -> str:
    """
    Criptografa a senha usando AES-CBC com PKCS7 padding e retorna uma string base64 codificada.
    """
    try:
        key = CYPHER_KEY.encode('utf-8')
        iv = CYPHER_IV.encode('utf-8')
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_password = pad(password.encode('utf-8'), AES.block_size)
        encrypted_password = cipher.encrypt(padded_password)
        encrypted_password_b64 = b64encode(encrypted_password).decode('utf-8')
        return encrypted_password_b64
    except Exception as e:
        print(f"Erro ao criptografar a senha: {e}")
        raise e


def restricted(func):
    """Decorator to restrict access to authorized users."""

    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if not context.user_data.get('authenticated'):
            await update.message.reply_text(
                "Você precisa se autenticar primeiro. Por favor, envie /start para iniciar o processo de autenticação."
            )
            print(f"User {user_id} tentou acessar um comando sem autenticação.")
            return
        return await func(update, context, *args, **kwargs)

    return wrapped


@restricted
async def show_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sends the list of available commands to the user.
    """
    await update.message.reply_text(
        "Comandos disponíveis:\n"
        "/subir_documento - Envie um documento para criar um novo chat.\n"
        "/listar_chats - Liste todos os chats disponíveis.\n"
        "/apagar_chat - Apagar um chat existente.\n"
        "/atualizar_chat - Atualizar um chat existente.\n"
        "/help - Mostrar esta lista de comandos.\n"
        "/cancel - Cancelar a operação atual.\n"
        "/logout - Sair da sessão atual."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sends the list of available commands to the user.
    """
    await show_commands(update, context)


@restricted
async def upload_document_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Initiates the document upload process by requesting the chat name.
    """
    user_id = update.effective_user.id
    print(f"User {user_id} initiated the /subir_documento command.")
    await update.message.reply_text(
        "Por favor, insira o nome que deseja dar ao chat:"
    )
    return WAITING_FOR_CHAT_NAME


@restricted
async def upload_document_receive_chat_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Receives the chat name and requests the document upload.
    """
    user_id = update.effective_user.id
    chat_name = update.message.text.strip()

    if not chat_name:
        await update.message.reply_text("O nome do chat não pode estar vazio. Por favor, insira um nome válido:")
        return WAITING_FOR_CHAT_NAME

    context.user_data['chat_name'] = chat_name
    print(f"User {user_id} set the chat name to: {chat_name}")
    await update.message.reply_text(
        "Nome do chat recebido com sucesso!\n\nPor favor, envie o documento que deseja subir (PDF ou DOCX).\n\nATENÇÃO: o nosso sistema utiliza sistemas terceiros para realizar o processamento do documento. Portanto, caso seu documento possua dados sensíveis, recomendamos não utilizar este sistema."
    )
    return WAITING_FOR_DOCUMENT


@restricted
async def upload_document_receive_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Receives the document from the user and creates the chat via the API.
    """
    user_id = update.effective_user.id
    document = update.message.document
    chat_name = context.user_data.get('chat_name')

    if document:
        file_type = document.mime_type
        print(f"User {user_id} sent a document with MIME type: {file_type}")
        if file_type not in ['application/pdf',
                             'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            await update.message.reply_text("Por favor, envie um arquivo PDF ou DOCX válido.")
            return WAITING_FOR_DOCUMENT
        # Store document information in context for future use
        context.user_data['document'] = document
        await update.message.reply_text("Documento recebido com sucesso!\n\nProcessando o documento...")

        # Prepare data for the API
        headers = {
            'Authorization': f'Bearer {context.user_data.get("access_token")}'
        }
        data = {
            'chat_name': chat_name
        }

        # Download the file
        try:
            file = await document.get_file()
            file_extension = os.path.splitext(file.file_path)[1] if file.file_path else '.pdf'
            pdf_path = f"./temp/{file.file_id}{file_extension}"
            await file.download_to_drive(pdf_path)
            print(f"File downloaded to {pdf_path}")
        except Exception as e:
            print(f"Error downloading the file: {e}")
            await update.message.reply_text("Ocorreu um erro ao processar o documento. Por favor, tente novamente.")
            return WAITING_FOR_DOCUMENT

        files = {
            'pdfs': open(pdf_path, 'rb')
        }

        try:
            # Send POST request to create the chat
            print(f"Creating a new chat '{chat_name}' for user {user_id}...")
            response = requests.post(
                API_BASE_URL,
                headers=headers,
                data=data,
                files=files
            )
            files['pdfs'].close()
            os.remove(pdf_path)  # Remove the temporary file

            if response.status_code == 201:
                chat = response.json()
                chat_id = chat.get('thread_id')
                if not chat_id:
                    # If 'thread_id' is not present, log the entire chat object for debugging
                    print(f"Chat object does not contain 'thread_id': {chat}")
                    await update.message.reply_text("Falha ao obter o ID do chat na resposta da API.")
                    await show_commands(update, context)  # Envia comandos disponíveis
                    return ConversationHandler.END
                context.user_data['chat_id'] = chat_id  # Store the chat_id
                await update.message.reply_text(f"Chat '{chat_name}' criado com sucesso!\nID do Chat: {chat_id}. Para acessá-lo, digite /listar_chats")
                print(f"Chat created: {chat}")
            elif response.status_code == 400:
                # Check if the error is due to chat already existing
                error_msg = response.json().get('error', 'Unknown error.')
                if "já existe" in error_msg.lower():
                    await update.message.reply_text(f"O chat '{chat_name}' já existe.")
                    print(f"Chat '{chat_name}' already exists for user {user_id}.")
                else:
                    await update.message.reply_text(f"Falha ao criar chat: {error_msg}")
                    print(f"Failed to create chat: {response.status_code} - {response.text}")
            else:
                error_msg = response.json().get('error', 'Unknown error.')
                await update.message.reply_text(f"Falha ao criar chat: {error_msg}")
                print(f"Failed to create chat: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error interacting with the API: {e}")
            await update.message.reply_text("Ocorreu um erro ao processar o documento. Por favor, tente novamente.")

        await show_commands(update, context)  # Envia a lista de comandos após a operação
        return ConversationHandler.END
    else:
        print(f"User {user_id} did not send a valid document.")
        await update.message.reply_text("Não foi possível receber o documento. Tente novamente.")
        return WAITING_FOR_DOCUMENT


@restricted
async def listar_chats_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Initiates the process to list existing chats and enter ask mode.
    """
    user_id = update.effective_user.id
    print(f"User {user_id} initiated the /listar_chats command.")
    headers = {
        'Authorization': f'Bearer {context.user_data.get("access_token")}'
    }
    try:
        print(f"Retrieving chats for user {user_id}...")
        response = requests.get(
            f"{API_BASE_URL}",  # Ensure this is the correct endpoint for listing chats
            headers=headers
        )
        if response.status_code == 200:
            chats = response.json()
            print(f"Chats retrieved: {chats}")  # Debugging line
            if not chats:
                await update.message.reply_text("Nenhum chat encontrado.")
                return ConversationHandler.END
            else:
                # Build a message listing the chats
                message = "Chats disponíveis:\n"
                for idx, chat in enumerate(chats, start=1):
                    message += f"{idx}. {chat.get('chat_name')} (ID: {chat.get('thread_id')})\n"
                message += "\nPor favor, envie o número correspondente ao chat que deseja selecionar."
                await update.message.reply_text(message)
                # Store the list of chats in context for future reference
                context.user_data['chats'] = chats
                return LIST_CHAT_WAITING_FOR_SELECTION
        else:
            try:
                error_msg = response.json().get('error', 'Unknown error.')
            except:
                error_msg = 'Unknown error.'
            await update.message.reply_text(f"Falha ao recuperar chats: {error_msg}")
            print(f"Failed to retrieve chats: {response.status_code} - {response.text}")
            return ConversationHandler.END
    except Exception as e:
        print(f"Error interacting with the API: {e}")
        await update.message.reply_text("Ocorreu um erro ao tentar recuperar os chats. Por favor, tente novamente.")
        return ConversationHandler.END


@restricted
async def list_chats_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Receives the user's selection and sets the chat_id, entering ask mode.
    """
    user_id = update.effective_user.id
    selection = update.message.text.strip()
    chats = context.user_data.get('chats', [])

    if not selection.isdigit():
        await update.message.reply_text("Por favor, envie um número válido correspondente ao chat.")
        return LIST_CHAT_WAITING_FOR_SELECTION

    selection = int(selection)
    if selection < 1 or selection > len(chats):
        await update.message.reply_text("Seleção inválida. Por favor, envie um número válido correspondente ao chat.")
        return LIST_CHAT_WAITING_FOR_SELECTION

    selected_chat = chats[selection - 1]
    chat_id = selected_chat.get('thread_id')

    if not chat_id:
        # If 'thread_id' is not present, log the entire chat object for debugging
        print(f"Selected chat does not contain 'thread_id': {selected_chat}")
        await update.message.reply_text("Falha ao obter o ID do chat selecionado.")
        return LIST_CHAT_WAITING_FOR_SELECTION

    context.user_data['chat_id'] = chat_id
    await update.message.reply_text(
        f"Chat '{selected_chat.get('chat_name')}' selecionado com sucesso!\nID do Chat: {chat_id}\n\n"
        "Você está agora no modo de perguntas. Envie a sua pergunta ou /cancel para sair."
    )
    print(f"User {user_id} selected chat_id {chat_id} via /listar_chats.")
    return ASKING_QUESTION  # Transition to ASKING_QUESTION state


@restricted
async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Processes questions sent in ask mode within a ConversationHandler.
    Handles both text and audio messages.
    """
    user_id = update.effective_user.id

    # Check if the message contains audio or voice
    if update.message.voice or update.message.audio:
        # Processing audio message
        audio = update.message.voice or update.message.audio

        # Download the audio file
        try:
            file = await audio.get_file()
            # Define the temporary path to store the audio
            audio_path = f"./temp/{file.file_id}.ogg"  # Telegram usually sends in OGG format
            await file.download_to_drive(audio_path)
            print(f"Audio file downloaded to {audio_path}")
        except Exception as e:
            print(f"Error downloading the audio file: {e}")
            await update.message.reply_text("Ocorreu um erro ao baixar o áudio. Por favor, tente novamente.")
            return ASKING_QUESTION

        # Transcribe the audio
        try:
            transcription = get_audio_answer(audio_path)
            print(f"Transcrição do áudio: {transcription}")
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            await update.message.reply_text("Ocorreu um erro ao transcrever o áudio. Por favor, tente novamente.")
            return ASKING_QUESTION
        finally:
            # Remove the temporary audio file
            try:
                os.remove(audio_path)
                print(f"Audio file {audio_path} removed.")
            except Exception as e:
                print(f"Error removing the audio file: {e}")

        question = transcription  # Use the transcription as the question

    else:
        # Processing text message
        question = update.message.text.strip()

        if not question:
            await update.message.reply_text("A pergunta não pode estar vazia. Por favor, envie uma pergunta válida:")
            return ASKING_QUESTION

    chat_id = context.user_data.get('chat_id')
    if not chat_id:
        await update.message.reply_text(
            "ID do chat não encontrado. Por favor, inicie novamente com /listar_chats."
        )
        return ConversationHandler.END

    # Prepare the request to the API
    headers = {
        'Authorization': f'Bearer {context.user_data.get("access_token")}',
        'Content-Type': 'application/json',
    }

    payload = {
        'question': question
    }

    api_endpoint = f"{API_BASE_URL}{chat_id}/"

    try:
        print(f"Sending question to chat_id {chat_id}: {question}")
        response = requests.put(api_endpoint, headers=headers, json=payload)
        if response.status_code == 200:
            answer = response.json().get('answer', 'Nenhuma resposta recebida.')
            # Escape special MarkdownV2 characters, excluding asterisks
            answer = escape_markdown(answer)
            # Specify parse_mode to maintain formatting
            await update.message.reply_text(answer, parse_mode='MarkdownV2')
            print(f"Received answer for user {user_id}: {answer}")
        else:
            try:
                error_msg = response.json().get('error', 'Erro desconhecido.')
            except:
                error_msg = 'Erro desconhecido.'
            await update.message.reply_text(f"Falha ao obter resposta: {error_msg}")
            print(f"Failed to get response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error interacting with the API: {e}")
        await update.message.reply_text("Ocorreu um erro ao processar a sua pergunta. Por favor, tente novamente.")

    return ASKING_QUESTION  # Remain in ASKING_QUESTION state to allow more questions


# **Funções de Atualização de Chat**

@restricted
async def atualizar_chat_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Inicia o processo de atualização de chat listando os chats disponíveis.
    """
    user_id = update.effective_user.id
    print(f"User {user_id} initiated the /atualizar_chat command.")
    headers = {
        'Authorization': f'Bearer {context.user_data.get("access_token")}'
    }
    try:
        print(f"Retrieving chats for user {user_id} to update...")
        response = requests.get(
            f"{API_BASE_URL}",  # Certifique-se de que este é o endpoint correto para listar chats
            headers=headers
        )
        if response.status_code == 200:
            chats = response.json()
            print(f"Chats retrieved for update: {chats}")  # Linha de depuração
            if not chats:
                await update.message.reply_text("Nenhum chat encontrado para atualizar.")
                return ConversationHandler.END
            else:
                # Construir uma mensagem listando os chats
                message = "Chats disponíveis para atualizar:\n"
                for idx, chat in enumerate(chats, start=1):
                    message += f"{idx}. {chat.get('chat_name')} (ID: {chat.get('thread_id')})\n"
                message += "\nPor favor, envie o número correspondente ao chat que deseja atualizar."
                await update.message.reply_text(message)
                # Armazenar a lista de chats no contexto para referência futura
                context.user_data['chats_to_update'] = chats
                return SELECT_CHAT
        else:
            try:
                error_msg = response.json().get('error', 'Erro desconhecido.')
            except:
                error_msg = 'Erro desconhecido.'
            await update.message.reply_text(f"Falha ao recuperar chats: {error_msg}")
            print(f"Failed to retrieve chats for update: {response.status_code} - {response.text}")
            return ConversationHandler.END
    except Exception as e:
        print(f"Error interacting with the API: {e}")
        await update.message.reply_text("Ocorreu um erro ao tentar recuperar os chats. Por favor, tente novamente.")
        return ConversationHandler.END


@restricted
async def atualizar_chat_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Recebe a seleção do usuário para qual chat atualizar e pergunta o que atualizar.
    """
    user_id = update.effective_user.id
    selection = update.message.text.strip()
    chats = context.user_data.get('chats_to_update', [])

    if not selection.isdigit():
        await update.message.reply_text("Por favor, envie um número válido correspondente ao chat.")
        return SELECT_CHAT

    selection = int(selection)
    if selection < 1 or selection > len(chats):
        await update.message.reply_text("Seleção inválida. Por favor, envie um número válido correspondente ao chat.")
        return SELECT_CHAT

    selected_chat = chats[selection - 1]
    chat_id = selected_chat.get('thread_id')
    chat_name = selected_chat.get('chat_name')

    if not chat_id:
        # Se 'thread_id' não estiver presente, logar o objeto completo para depuração
        print(f"Selected chat does not contain 'thread_id': {selected_chat}")
        await update.message.reply_text("Falha ao obter o ID do chat selecionado.")
        return SELECT_CHAT

    # Armazenar o chat_id selecionado para atualização
    context.user_data['chat_id_to_update'] = chat_id
    context.user_data['chat_name_to_update'] = chat_name

    # Perguntar o que o usuário deseja atualizar
    update_options = (
        "O que você deseja atualizar?\n"
        "1. Nome do chat\n"
        "2. Arquivo PDF\n"
        "3. Ambos (Nome e PDF)\n"
        "Por favor, envie o número correspondente à opção desejada."
    )
    await update.message.reply_text(update_options)
    return CHOOSE_UPDATE


@restricted
async def atualizar_chat_choose_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Recebe a escolha do usuário sobre o que atualizar (nome, PDF ou ambos).
    """
    user_id = update.effective_user.id
    choice = update.message.text.strip()

    if choice not in ['1', '2', '3']:
        await update.message.reply_text("Por favor, envie um número válido (1, 2 ou 3).")
        return CHOOSE_UPDATE

    context.user_data['update_choice'] = choice

    if choice == '1':
        await update.message.reply_text("Por favor, envie o novo nome para o chat:")
        return UPDATE_NAME
    elif choice == '2':
        await update.message.reply_text("Por favor, envie o novo arquivo PDF para o chat:\n\nATENÇÃO: o nosso sistema utiliza sistemas terceiros para realizar o processamento do documento. Portanto, caso seu documento possua dados sensíveis, recomendamos não utilizar este sistema.")
        return UPDATE_DOCUMENT
    elif choice == '3':
        await update.message.reply_text("Por favor, envie o novo nome para o chat:")
        return UPDATE_NAME


@restricted
async def atualizar_chat_new_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Recebe o novo nome do chat.
    """
    user_id = update.effective_user.id
    new_name = update.message.text.strip()

    if not new_name:
        await update.message.reply_text("O nome do chat não pode estar vazio. Por favor, envie um nome válido:")
        return UPDATE_NAME

    context.user_data['new_chat_name'] = new_name
    choice = context.user_data.get('update_choice')

    if choice in ['2', '3']:
        await update.message.reply_text("Por favor, envie o novo arquivo PDF para o chat:\n\nATENÇÃO: o nosso sistema utiliza sistemas terceiros para realizar o processamento do documento. Portanto, caso seu documento possua dados sensíveis, recomendamos não utilizar este sistema.")
        return UPDATE_DOCUMENT
    else:
        # Se apenas o nome está sendo atualizado, proceder para confirmação
        return await confirmar_atualizacao(update, context)


@restricted
async def atualizar_chat_new_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Recebe o novo arquivo PDF para o chat.
    """
    user_id = update.effective_user.id
    document = update.message.document

    if not document:
        await update.message.reply_text("Por favor, envie um arquivo PDF válido.")
        return UPDATE_DOCUMENT

    file_type = document.mime_type
    print(f"User {user_id} sent a document with MIME type: {file_type}")
    if file_type not in ['application/pdf']:
        await update.message.reply_text("Por favor, envie um arquivo PDF válido.")
        return UPDATE_DOCUMENT

    # Armazenar o documento no contexto para uso futuro
    context.user_data['new_pdf_document'] = document
    return await confirmar_atualizacao(update, context)


@restricted
async def confirmar_atualizacao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Solicita a confirmação do usuário antes de proceder com a atualização.
    """
    user_id = update.effective_user.id
    confirmation_message = "Você confirma a atualização do chat? Responda com Sim ou Não."
    await update.message.reply_text(confirmation_message)
    return CONFIRM_UPDATE


@restricted
async def atualizar_chat_execute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Executa a atualização do chat após a confirmação do usuário.
    """
    user_id = update.effective_user.id
    confirmation = update.message.text.strip().lower()

    if confirmation not in ['sim', 's', 'não', 'nao', 'n']:
        await update.message.reply_text("Por favor, responda com Sim ou Não.")
        return CONFIRM_UPDATE

    if confirmation in ['sim', 's']:
        chat_id = context.user_data.get('chat_id_to_update')
        new_chat_name = context.user_data.get('new_chat_name')
        new_pdf_document = context.user_data.get('new_pdf_document')

        if not chat_id:
            await update.message.reply_text("ID do chat não encontrado. Por favor, inicie novamente com /atualizar_chat.")
            return ConversationHandler.END

        # Preparar os dados para a requisição PUT
        headers = {
            'Authorization': f'Bearer {context.user_data.get("access_token")}'
        }

        data = {}
        files = {}

        if new_chat_name:
            data['chat_name'] = new_chat_name

        if new_pdf_document:
            try:
                # Download do arquivo PDF
                file = await new_pdf_document.get_file()
                pdf_path = f"./temp/{file.file_id}.pdf"
                await file.download_to_drive(pdf_path)
                print(f"New PDF file downloaded to {pdf_path}")
                files['pdfs'] = open(pdf_path, 'rb')
            except Exception as e:
                print(f"Error downloading the new PDF file: {e}")
                await update.message.reply_text("Ocorreu um erro ao baixar o novo PDF. Por favor, tente novamente.")
                return ConversationHandler.END

        api_endpoint = f"{API_BASE_URL}put/{chat_id}/"  # Atualizar para o endpoint correto

        try:
            # Enviar a requisição PUT para atualizar o chat
            print(f"Sending PUT request to update chat_id {chat_id}...")
            response = requests.put(
                api_endpoint,
                headers=headers,
                data=data,
                files=files if files else None
            )

            if files:
                files['pdfs'].close()
                os.remove(pdf_path)  # Remover o arquivo PDF temporário

            if response.status_code == 200:
                updated_chat = response.json()
                await update.message.reply_text(f"Chat '{updated_chat.get('chat_name')}' atualizado com sucesso! Digite /listar_chats para conversar com seu pdf.")
                print(f"Chat updated successfully: {updated_chat}")
            else:
                try:
                    error_msg = response.json().get('error', 'Erro desconhecido.')
                except:
                    error_msg = 'Erro desconhecido.'
                await update.message.reply_text(f"Falha ao atualizar o chat: {error_msg}")
                print(f"Failed to update chat: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error interacting with the API: {e}")
            await update.message.reply_text("Ocorreu um erro ao atualizar o chat. Por favor, tente novamente.")

        # Limpar os dados armazenados no contexto após a atualização
        context.user_data.pop('chat_id_to_update', None)
        context.user_data.pop('new_chat_name', None)
        context.user_data.pop('new_pdf_document', None)
        context.user_data.pop('chats_to_update', None)

        await show_commands(update, context)  # Envia a lista de comandos após a operação
        return ConversationHandler.END

    else:
        await update.message.reply_text("Operação de atualização de chat cancelada.")
        print(f"User {user_id} canceled the chat update.")
        # Limpar os dados armazenados no contexto
        context.user_data.pop('chat_id_to_update', None)
        context.user_data.pop('new_chat_name', None)
        context.user_data.pop('new_pdf_document', None)
        context.user_data.pop('chats_to_update', None)
        return ConversationHandler.END


@restricted
async def apagar_chat_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Initiates the chat deletion process by listing available chats.
    """
    user_id = update.effective_user.id
    print(f"User {user_id} initiated the /apagar_chat command.")
    headers = {
        'Authorization': f'Bearer {context.user_data.get("access_token")}'
    }
    try:
        print(f"Retrieving chats for user {user_id} to delete...")
        response = requests.get(
            f"{API_BASE_URL}",  # Ensure this is the correct endpoint for listing chats
            headers=headers
        )
        if response.status_code == 200:
            chats = response.json()
            print(f"Chats retrieved for deletion: {chats}")  # Debugging line
            if not chats:
                await update.message.reply_text("Nenhum chat encontrado para apagar.")
                return ConversationHandler.END
            else:
                # Build a message listing the chats
                message = "Chats disponíveis para apagar:\n"
                for idx, chat in enumerate(chats, start=1):
                    message += f"{idx}. {chat.get('chat_name')} (ID: {chat.get('thread_id')})\n"
                message += "\nPor favor, envie o número correspondente ao chat que deseja apagar."
                await update.message.reply_text(message)
                # Store the list of chats in context for future reference
                context.user_data['chats_to_delete'] = chats
                return DELETE_CHAT_WAITING_FOR_SELECTION
        else:
            try:
                error_msg = response.json().get('error', 'Erro desconhecido.')
            except:
                error_msg = 'Erro desconhecido.'
            await update.message.reply_text(f"Falha ao recuperar chats: {error_msg}")
            print(f"Failed to retrieve chats for deletion: {response.status_code} - {response.text}")
            return ConversationHandler.END
    except Exception as e:
        print(f"Error interacting with the API: {e}")
        await update.message.reply_text("Ocorreu um erro ao tentar recuperar os chats. Por favor, tente novamente.")
        return ConversationHandler.END


@restricted
async def apagar_chat_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Receives the user's selection for which chat to delete and asks for confirmation.
    """
    user_id = update.effective_user.id
    selection = update.message.text.strip()
    chats = context.user_data.get('chats_to_delete', [])

    if not selection.isdigit():
        await update.message.reply_text("Por favor, envie um número válido correspondente ao chat.")
        return DELETE_CHAT_WAITING_FOR_SELECTION

    selection = int(selection)
    if selection < 1 or selection > len(chats):
        await update.message.reply_text("Seleção inválida. Por favor, envie um número válido correspondente ao chat.")
        return DELETE_CHAT_WAITING_FOR_SELECTION

    selected_chat = chats[selection - 1]
    chat_id = selected_chat.get('thread_id')
    chat_name = selected_chat.get('chat_name')

    if not chat_id:
        # If 'thread_id' is not present, log the entire chat object for debugging
        print(f"Selected chat does not contain 'thread_id': {selected_chat}")
        await update.message.reply_text("Falha ao obter o ID do chat selecionado.")
        return DELETE_CHAT_WAITING_FOR_SELECTION

    # Store the selected chat_id for deletion
    context.user_data['chat_id_to_delete'] = chat_id
    context.user_data['chat_name_to_delete'] = chat_name

    # Ask for confirmation
    confirmation_message = f"Tem certeza que deseja apagar o chat '{chat_name}'? Responda com Sim ou Não."
    await update.message.reply_text(confirmation_message)
    return DELETE_CHAT_CONFIRMATION


@restricted
async def apagar_chat_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Receives the user's confirmation to delete the selected chat.
    """
    user_id = update.effective_user.id
    confirmation = update.message.text.strip().lower()

    if confirmation not in ['sim', 's', 'não', 'nao', 'n']:
        await update.message.reply_text("Por favor, responda com Sim ou Não.")
        return DELETE_CHAT_CONFIRMATION

    if confirmation in ['sim', 's']:
        chat_id = context.user_data.get('chat_id_to_delete')
        chat_name = context.user_data.get('chat_name_to_delete')

        if not chat_id:
            await update.message.reply_text("ID do chat não encontrado. Por favor, inicie novamente com /apagar_chat.")
            return ConversationHandler.END

        # Prepare the DELETE request to the API
        headers = {
            'Authorization': f'Bearer {context.user_data.get("access_token")}'
        }
        api_endpoint = f"{API_BASE_URL}delete/{chat_id}/"

        try:
            print(f"Sending DELETE request for chat_id {chat_id} by user {user_id}...")
            response = requests.delete(api_endpoint, headers=headers)
            if response.status_code in [200, 204]:
                await update.message.reply_text(f"Chat '{chat_name}' apagado com sucesso!")
                print(f"Chat '{chat_name}' (ID: {chat_id}) deleted successfully.")
            elif response.status_code == 404:
                await update.message.reply_text("Chat não encontrado ou já foi apagado.")
                print(f"Chat '{chat_name}' (ID: {chat_id}) not found or already deleted.")
            else:
                try:
                    error_msg = response.json().get('error', 'Erro desconhecido.')
                except:
                    error_msg = 'Erro desconhecido.'
                await update.message.reply_text(f"Falha ao apagar o chat: {error_msg}")
                print(f"Failed to delete chat: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error interacting with the API: {e}")
            await update.message.reply_text("Ocorreu um erro ao apagar o chat. Por favor, tente novamente.")

    else:
        await update.message.reply_text("Operação de exclusão de chat cancelada.")
        print(f"User {user_id} canceled the chat deletion.")

    # Clear the stored chat data
    context.user_data.pop('chat_id_to_delete', None)
    context.user_data.pop('chat_name_to_delete', None)
    context.user_data.pop('chats_to_delete', None)

    await show_commands(update, context)  # Envia a lista de comandos após a operação
    return ConversationHandler.END


@restricted
async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Logs out the user by clearing the authentication status.
    """
    user_id = update.effective_user.id
    context.user_data.pop('access_token', None)
    context.user_data.pop('refresh_token', None)
    context.user_data.pop('session_id', None)
    context.user_data.pop('authenticated', None)
    await update.message.reply_text("Você foi desautenticado com sucesso. Para acessar novamente, envie /start.")
    print(f"User {user_id} logged out.")
    return ConversationHandler.END


@restricted
async def atualizar_chat_execute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Executa a atualização do chat após a confirmação do usuário.
    """
    user_id = update.effective_user.id
    confirmation = update.message.text.strip().lower()

    if confirmation not in ['sim', 's', 'não', 'nao', 'n']:
        await update.message.reply_text("Por favor, responda com Sim ou Não.")
        return CONFIRM_UPDATE

    if confirmation in ['sim', 's']:
        chat_id = context.user_data.get('chat_id_to_update')
        new_chat_name = context.user_data.get('new_chat_name')
        new_pdf_document = context.user_data.get('new_pdf_document')

        if not chat_id:
            await update.message.reply_text("ID do chat não encontrado. Por favor, inicie novamente com /atualizar_chat.")
            return ConversationHandler.END

        # Preparar os dados para a requisição PUT
        headers = {
            'Authorization': f'Bearer {context.user_data.get("access_token")}'
        }

        data = {}
        files = {}

        if new_chat_name:
            data['chat_name'] = new_chat_name

        if new_pdf_document:
            try:
                # Download do arquivo PDF
                file = await new_pdf_document.get_file()
                pdf_path = f"./temp/{file.file_id}.pdf"
                await file.download_to_drive(pdf_path)
                print(f"New PDF file downloaded to {pdf_path}")
                files['pdfs'] = open(pdf_path, 'rb')
            except Exception as e:
                print(f"Error downloading the new PDF file: {e}")
                await update.message.reply_text("Ocorreu um erro ao baixar o novo PDF. Por favor, tente novamente.")
                return ConversationHandler.END

        api_endpoint = f"{API_BASE_URL}put/{chat_id}/"  # Atualizar para o endpoint correto

        try:
            # Enviar a requisição PUT para atualizar o chat
            print(f"Sending PUT request to update chat_id {chat_id}...")
            response = requests.put(
                api_endpoint,
                headers=headers,
                data=data,
                files=files if files else None
            )

            if files:
                files['pdfs'].close()
                os.remove(pdf_path)  # Remover o arquivo PDF temporário

            if response.status_code == 200:
                updated_chat = response.json()
                await update.message.reply_text(f"Chat '{updated_chat.get('chat_name')}' atualizado com sucesso! Digite /listar_chats para conversar com seu pdf.")
                print(f"Chat updated successfully: {updated_chat}")
            else:
                try:
                    error_msg = response.json().get('error', 'Erro desconhecido.')
                except:
                    error_msg = 'Erro desconhecido.'
                await update.message.reply_text(f"Falha ao atualizar o chat: {error_msg}")
                print(f"Failed to update chat: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error interacting with the API: {e}")
            await update.message.reply_text("Ocorreu um erro ao atualizar o chat. Por favor, tente novamente.")

        # Limpar os dados armazenados no contexto após a atualização
        context.user_data.pop('chat_id_to_update', None)
        context.user_data.pop('new_chat_name', None)
        context.user_data.pop('new_pdf_document', None)
        context.user_data.pop('chats_to_update', None)

        await show_commands(update, context)  # Envia a lista de comandos após a operação
        return ConversationHandler.END

    else:
        await update.message.reply_text("Operação de atualização de chat cancelada.")
        print(f"User {user_id} canceled the chat update.")
        # Limpar os dados armazenados no contexto
        context.user_data.pop('chat_id_to_update', None)
        context.user_data.pop('new_chat_name', None)
        context.user_data.pop('new_pdf_document', None)
        context.user_data.pop('chats_to_update', None)
        return ConversationHandler.END


@restricted
async def delete_chat_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Cancels the chat deletion operation.
    """
    user_id = update.effective_user.id
    print(f"User {user_id} canceled the chat deletion.")
    # Clear any stored data related to chat deletion
    context.user_data.pop('chat_id_to_delete', None)
    context.user_data.pop('chat_name_to_delete', None)
    context.user_data.pop('chats_to_delete', None)
    await show_commands(update, context)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Cancels the current operation and deactivates ask mode.
    """
    user_id = update.effective_user.id
    print(f"User {user_id} canceled the operation.")
    # Clear any stored data related to ongoing operations
    context.user_data.pop('chat_id', None)
    context.user_data.pop('chats', None)
    context.user_data.pop('chat_id_to_update', None)
    context.user_data.pop('new_chat_name', None)
    context.user_data.pop('new_pdf_document', None)
    context.user_data.pop('chats_to_update', None)
    context.user_data.pop('chat_id_to_delete', None)
    context.user_data.pop('chat_name_to_delete', None)
    context.user_data.pop('chats_to_delete', None)
    # Invalida a autenticação se estiver no meio do processo
    context.user_data.pop('auth_username', None)
    await update.message.reply_text("Operação cancelada.")
    await show_commands(update, context)
    return ConversationHandler.END


@restricted
async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Responds to unknown commands.
    """
    user_id = update.effective_user.id
    print(f"User {user_id} sent an unknown command: {update.message.text}")
    await update.message.reply_text(
        "Desculpe, eu não reconheço esse comando. Use /help para ver os comandos disponíveis."
    )


# Handlers para Autenticação

async def start_auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Inicia o fluxo de autenticação ao enviar /start.
    """
    user_id = update.effective_user.id
    print(f"User {user_id} started the bot.")
    await update.message.reply_text(
        "Bem-vindo ao Docmind! Para acessar, por favor, insira seu username."
    )
    return AUTH_USERNAME_STATE


async def auth_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Recebe o username do usuário e solicita a senha.
    """
    user_id = update.effective_user.id
    username = update.message.text.strip()
    
    if not username:
        await update.message.reply_text("O username não pode estar vazio. Por favor, insira um username válido:")
        return AUTH_USERNAME_STATE
    
    context.user_data['auth_username'] = username
    print(f"User {user_id} entered username: {username}")
    await update.message.reply_text("Por favor, insira sua senha:")
    return AUTH_PASSWORD_STATE


async def auth_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Recebe a senha do usuário, criptografa, e realiza a autenticação enviando para o backend.
    """
    user_id = update.effective_user.id
    password = update.message.text.strip()
    username = context.user_data.get('auth_username')
    
    if not password:
        await update.message.reply_text("A senha não pode estar vazia. Por favor, insira uma senha válida:")
        return AUTH_PASSWORD_STATE
    
    # Criptografar a senha usando o método AES-CBC
    try:
        encrypted_password = encrypt_password(password)
    except Exception as e:
        await update.message.reply_text("Ocorreu um erro ao criptografar a senha. Por favor, tente novamente.")
        print(f"Error encrypting password for user {user_id}: {e}")
        return ConversationHandler.END

    # Preparar os dados para a requisição de autenticação
    auth_payload = {
        'username': username,
        'password': encrypted_password
    }

    try:
        # Enviar a requisição POST para o backend de autenticação
        print(f"Sending authentication request for user {user_id}...")
        response = requests.post(API_LOGIN_URL, data=auth_payload)
        
        if response.status_code == 200:
            auth_response = response.json()
            access_token = auth_response.get('access')
            refresh_token = auth_response.get('refresh')
            session_id = auth_response.get('sessionid')

            if access_token and refresh_token and session_id:
                # Armazenar os tokens no user_data para uso futuro
                context.user_data['access_token'] = access_token
                context.user_data['refresh_token'] = refresh_token
                context.user_data['session_id'] = session_id
                context.user_data['authenticated'] = True

                await update.message.reply_text(
                    "Autenticação bem-sucedida! Você agora tem acesso aos comandos do bot."
                )
                # Opcional: Envie a lista de comandos disponíveis
                await show_commands(update, context)
                print(f"User {user_id} authenticated successfully.")
                return ConversationHandler.END
            else:
                await update.message.reply_text(
                    "Autenticação falhou. Resposta inesperada do servidor."
                )
                print(f"User {user_id} received unexpected authentication response: {auth_response}")
                return ConversationHandler.END
        elif response.status_code == 404:
            await update.message.reply_text(
                "Autenticação falhou. Usuário não encontrado.\nTente novamente ou envie /start para reiniciar o processo."
            )
            print(f"User {user_id} authentication failed: User not found.")
            return ConversationHandler.END
        elif response.status_code == 401:
            await update.message.reply_text(
                "Autenticação falhou. Senha incorreta.\nTente novamente ou envie /start para reiniciar o processo."
            )
            print(f"User {user_id} authentication failed: Incorrect password.")
            return ConversationHandler.END
        else:
            try:
                error_msg = response.json().get('message', 'Erro desconhecido.')
            except:
                error_msg = 'Erro desconhecido.'
            await update.message.reply_text(f"Autenticação falhou: {error_msg}\nTente novamente ou envie /start para reiniciar o processo.")
            print(f"User {user_id} authentication failed: {response.status_code} - {response.text}")
            return ConversationHandler.END
    except Exception as e:
        await update.message.reply_text("Ocorreu um erro durante a autenticação. Por favor, tente novamente.")
        print(f"Error during authentication request for user {user_id}: {e}")
        return ConversationHandler.END


def main():
    """
    Starts the bot.
    """
    # Remove a autenticação inicial do bot
    # authenticate_bot()
    # if not JWT_TOKEN:
    #     print("Failed to authenticate with the API. The bot will not start.")
    #     return

    # Create the Telegram bot application
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # ConversationHandler para Autenticação
    auth_conv = ConversationHandler(
        entry_points=[CommandHandler('start', start_auth)],
        states={
            AUTH_USERNAME_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, auth_username)],
            AUTH_PASSWORD_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, auth_password)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    application.add_handler(auth_conv)

    # Handler para o comando /help
    application.add_handler(CommandHandler("help", help_command))

    # Handler para o comando /logout
    application.add_handler(CommandHandler("logout", logout))

    # ConversationHandler para /subir_documento
    upload_document_conv = ConversationHandler(
        entry_points=[CommandHandler('subir_documento', upload_document_start)],
        states={
            WAITING_FOR_CHAT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, upload_document_receive_chat_name)],
            WAITING_FOR_DOCUMENT: [MessageHandler(filters.Document.ALL, upload_document_receive_document)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    application.add_handler(upload_document_conv)

    # ConversationHandler para /listar_chats
    list_chats_conv = ConversationHandler(
        entry_points=[CommandHandler('listar_chats', listar_chats_start)],
        states={
            LIST_CHAT_WAITING_FOR_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, list_chats_selection)],
            ASKING_QUESTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question),
                MessageHandler(filters.VOICE | filters.AUDIO, handle_question)  # Suporte a áudio
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    application.add_handler(list_chats_conv)

    # ConversationHandler para /apagar_chat
    apagar_chat_conv = ConversationHandler(
        entry_points=[CommandHandler('apagar_chat', apagar_chat_start)],
        states={
            DELETE_CHAT_WAITING_FOR_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, apagar_chat_selection)],
            DELETE_CHAT_CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, apagar_chat_confirmation)],
        },
        fallbacks=[CommandHandler('cancel', delete_chat_cancel)],
    )
    application.add_handler(apagar_chat_conv)

    # ConversationHandler para /atualizar_chat
    atualizar_chat_conv = ConversationHandler(
        entry_points=[CommandHandler('atualizar_chat', atualizar_chat_start)],
        states={
            SELECT_CHAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, atualizar_chat_selection)],
            CHOOSE_UPDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, atualizar_chat_choose_update)],
            UPDATE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, atualizar_chat_new_name)],
            UPDATE_DOCUMENT: [MessageHandler(filters.Document.ALL, atualizar_chat_new_document)],
            CONFIRM_UPDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, atualizar_chat_execute)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    application.add_handler(atualizar_chat_conv)

    # Handler para comandos desconhecidos (deve ser adicionado por último)
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    # Start the bot
    print("Bot is starting...")
    application.run_polling()


if __name__ == '__main__':
    main()
