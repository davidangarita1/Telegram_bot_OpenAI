import requests
import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, CallbackContext, Filters

load_dotenv()

# Estados de la conversación
SELECTING_PROMPT = 0
GENERATING_IMAGE = 1

# Almacena el prompt ingresado por el usuario
user_prompt = None

# Función para manejar el comando /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Por favor, ingresa una descripción para generar la imagen.")
    return SELECTING_PROMPT

def set_prompt(update: Update, context: CallbackContext):
    API_URL = os.getenv("API_URL")

    global user_prompt
    user_prompt = update.message.text
    context.user_data['prompt'] = user_prompt

    update.message.reply_text(f'Generando la imagen...')

    # Realiza la solicitud POST a la API con el prompt
    response = requests.post(API_URL, json={'prompt': user_prompt, 'num': 1, 'size': '512x512'})
	
    try:
        response.raise_for_status()
        imagen_url = response.text  # La respuesta es un string, lo almacenamos directamente
        # logging.info("URL de la imagen: %s", imagen_url)
        context.bot.send_photo(chat_id=update.message.chat_id, photo=imagen_url)
    except requests.exceptions.RequestException as e:
        logging.error("Error en la solicitud a la API: %s", e)
        update.message.reply_text('Hubo un problema al generar la imagen. Inténtalo de nuevo más tarde.')

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("Operación cancelada.")
    return ConversationHandler.END

def main():
    # Inicializa el bot de Telegram.
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Crea un conversación para manejar el ingreso del prompt
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECTING_PROMPT: [MessageHandler(Filters.text & ~Filters.command, set_prompt)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(conversation_handler)
    # Inicia el bot.
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()