import logging
from telegram.ext import Updater, CommandHandler, CallbackContext
from datetime import datetime
import pytz

import my_token

# Impostazione del logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


# Definisci una funzione per inviare una notifica
def send_notification(context: CallbackContext):
    # Inserisci qui il codice per inviare una notifica (ad esempio tramite Telegram)
    # Esempio con telegram.ext:
    chat_id = 'CHAT_ID_DEL_DESTINATARIO'
    message = "E' ora di ricevere un messaggio speciale!"
    context.bot.send_message(chat_id=chat_id, text=message)


def main():
    # Imposta il token del tuo bot Telegram
    updater = Updater(my_token.TOKEN, use_context=True)

    # Ottieni il dispatcher per registrare i gestori di comandi
    dp = updater.dispatcher

    # Aggiungi un gestore di comandi per avviare il bot
    dp.add_handler(CommandHandler("start", start))

    # Avvia il bot
    updater.start_polling()

    # Pianifica l'esecuzione della funzione send_notification() agli orari specificati
    tz = pytz.timezone('Europe/Rome')
    for time_str in ["10:01", "11:11", "12:21", "13:31", "14:41"]:
        time_obj = datetime.strptime(time_str, "%H:%M").time()
        time_obj = tz.localize(datetime.combine(datetime.today(), time_obj))
        updater.job_queue.run_daily(send_notification, time_obj.time(), days=(0, 1, 2, 3, 4, 5, 6))

    # Esegui il bot fino a quando non viene premuto CTRL+C o il processo riceve SIGINT,
    # SIGTERM o SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
