import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import datetime
from zoneinfo import ZoneInfo

import my_token

# Impostazione del logger
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text("Hi there let me help you set up some reminder!")


async def send_notification(context: ContextTypes.DEFAULT_TYPE):
    message = "Reminder!!! Drin Drin"
    await context.bot.send_message(chat_id=context.job.chat_id, text=message)


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE):
    current_job = context.job_queue.get_jobs_by_name(name)
    if not current_job:
        return False
    for job in current_job:
        job.schedule_removal()
    return True


async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_message.chat_id
    try:
        scadenza = float(context.args[0])
        if scadenza < 0:
            await update.effective_message.reply_text("Can't set the timer in the past.")
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_once(send_notification, scadenza, name=str(chat_id), chat_id=chat_id)

        text = "Timer set!"
        if job_removed:
            text += "\nOld one was removed"
        await update.effective_message.reply_text(text)
    except(IndexError, ValueError):
        await update.effective_message.reply_text("Usage: /set <seconds>")


async def set_daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_message.chat_id
    try:
        time_input = context.args[0].split(':')
        hour = int(time_input[0])
        minute = int(time_input[1])
        try:
            second = int(time_input[2])
        except IndexError:
            second = 0

        if not (0 <= hour <= 23) or not (0 <= minute <= 59) or not (0 <= second <= 59):
            await update.effective_message.reply_text("Invalid time format. Please use HH:MM(:SS)? format.")
            return

        datetime_obj = datetime.time(hour, minute, second, tzinfo=ZoneInfo("Europe/Rome"))
        job_name = datetime_obj.strftime('%H:%M:%S')

        job_removed = remove_job_if_exists(job_name, context)
        context.job_queue.run_daily(send_notification, datetime_obj, name=job_name, chat_id=chat_id)

        text = f"Timer set at {datetime_obj}!"
        if job_removed:
            text += "\nOld one was removed"
        await update.effective_message.reply_text(text)
    except(IndexError, ValueError):
        await update.effective_message.reply_text("Usage: /set_daily <HH:MM(:SS)?>")


async def unset_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Timer was successfully removed!" if job_removed else "There is no timer set!"
    await update.effective_message.reply_text(text)


def main():
    application = Application.builder().token(my_token.TOKEN).build()

    jq = application.job_queue

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set", set_timer))
    application.add_handler(CommandHandler("set_daily", set_daily))
    application.add_handler(CommandHandler("unset", unset_timer))

    # Avvia il bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

    # Pianifica l'esecuzione della funzione send_notification() agli orari specificati
    # tz = pytz.timezone('Europe/Rome')
    # for time_str in ["10:01", "11:11", "12:21", "13:31", "14:41"]:
    #     time_obj = datetime.strptime(time_str, "%H:%M").time()
    #     time_obj = tz.localize(datetime.combine(datetime.today(), time_obj))
    #     updater.job_queue.run_daily(send_notification, time_obj.time(), days=(0, 1, 2, 3, 4, 5, 6))


if __name__ == '__main__':
    main()
