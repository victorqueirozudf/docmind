from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import openai

# Insira o seu token do Bot aqui
TELEGRAM_BOT_TOKEN = '8082392422:AAEdpZuEgPuEr7PBAUMPB8PxQK_L1o9IU7o'
OPENAI_API_KEY = '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'

def get_audio_anwser(audio):
    openai.api_key = OPENAI_API_KEY

    audioFile = audio

    audio_file = open(audioFile, "rb")
    transcription = openai.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )

    print(transcription.text)

    userInput = transcription.text

    completion = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": userInput
            }
        ]
    )

    print(completion.choices[0].message)

    return completion.choices[0].message.content

# Função que será chamada para qualquer mensagem recebida
async def respond_hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Responde "Hello, world!" ao usuário que enviou a mensagem
    await update.message.reply_text()


# Função para receber e processar o áudio
async def processa_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Baixa o arquivo de áudio enviado pelo usuário
    print("rodando")
    file = await context.bot.get_file(update.message.voice.file_id)
    file_path = "audio_telegram.ogg"
    await file.download_to_drive(file_path)

    # Processa o áudio usando a função específica
    resposta = get_audio_anwser(file_path)

    # Responde ao usuário com o resultado do processamento
    await update.message.reply_text(f"{resposta}")

def main():
    # Inicializa a aplicação com o token do bot
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Define o handler que recebe mensagens de áudio (voz)
    audio_handler = MessageHandler(filters.VOICE, processa_audio)
    application.add_handler(audio_handler)

    # Inicia o bot e aguarda mensagens
    application.run_polling()

# Executa o bot
if __name__ == "__main__":
    main()