from telegram import Update
from telegram.ext import Updater, MessageHandler, filters, Application, CommandHandler, ContextTypes

import my_token

# Inserisci il token del tuo bot Telegram
TOKEN = my_token.TOKEN

def get_chat_id(update, context):
    chat_id = update.message.chat_id
    print("Chat ID:", chat_id)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    print("Chat ID:", chat_id)


def main():
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start_command))

    app.run_polling(poll_interval=3)  # 3 seconds


if __name__ == '__main__':
    main()
