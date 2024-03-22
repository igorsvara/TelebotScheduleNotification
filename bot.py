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
    message = f"{context.job.data}"
    message += "\nReminder!!! Drin Drin"
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

        timer_description = None
        if len(context.args) > 1:
            timer_description = " ".join(context.args[1:])

        timer_click = datetime.datetime.now() - datetime.timedelta(seconds=scadenza)
        timer_click_string = timer_click.strftime("%H:%M:%S - %a, %d %b")

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_once(send_notification, scadenza, name=timer_click_string, chat_id=chat_id,
                                   data=timer_description)

        text = f"Timer set for {scadenza} seconds. Will ring at: {timer_click_string}"
        if job_removed:
            text += "\nOld one was removed"
        await update.effective_message.reply_text(text)
    except(IndexError, ValueError):
        await update.effective_message.reply_text("Usage: /set_t <seconds> timer-description")


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

        timer_description = None
        if len(context.args) > 1:
            timer_description = " ".join(context.args[1:])

        if not (0 <= hour <= 23) or not (0 <= minute <= 59) or not (0 <= second <= 59):
            await update.effective_message.reply_text("Invalid time format. Please use HH:MM(:SS)? format.")
            return

        datetime_obj = datetime.time(hour, minute, second, tzinfo=ZoneInfo("Europe/Rome"))
        job_name = datetime_obj.strftime('%H:%M:%S')

        job_removed = remove_job_if_exists(job_name, context)
        context.job_queue.run_daily(send_notification, datetime_obj, name=job_name, chat_id=chat_id,
                                    data=timer_description)

        text = f"Timer set at {datetime_obj} with description: {timer_description}"
        if job_removed:
            text += "\nOld one was removed"
        await update.effective_message.reply_text(text)
    except(IndexError, ValueError):
        await update.effective_message.reply_text("Usage: /set_d <HH:MM(:SS)?> timer-description")


async def unset_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_message.chat_id
    try:
        timer_to_remove = int(context.args[0])

        all_jobs = context.job_queue.jobs()
        chat_jobs = [job for job in all_jobs if job.chat_id == chat_id]

        if timer_to_remove > len(chat_jobs) or timer_to_remove < 1:
            await update.effective_message.reply_text(
                f"Invalid numer range. Select a valid timer index. [from {1} to {len(chat_jobs)}]")
            await show_timers(update, context)
            return

        context.job_queue.jobs()[timer_to_remove-1].schedule_removal()
        text = f"Timer '{timer_to_remove}' was successfully removed!"

        await update.effective_message.reply_text(text)
    except (ValueError, IndexError):
        await update.effective_message.reply_text("Usage: /unset number")


async def remove_all_timers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_message.chat_id
    chat_jobs = context.job_queue.jobs()
    text = ""
    for job in chat_jobs:
        if job.chat_id == chat_id:
            text += f"Timer '{job.name}' was successfully removed!\n"
            job.schedule_removal()
    if text == "":
        text = "There is no timer set!"
    await update.effective_message.reply_text(text)


async def show_timers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jobs = context.job_queue.jobs()
    text = "To ineract with the timers use <'HH:MM:SS'>\n\n"
    if len(jobs) == 0:
        text = "The list is empty."
    for i, job in enumerate(jobs):
        text += f"{i + 1} : {job.name}  -  {job.data}\n"
    await update.effective_message.reply_text(text)


def main():
    application = Application.builder().token(my_token.TOKEN).build()

    jq = application.job_queue

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set_t", set_timer))
    application.add_handler(CommandHandler("set_d", set_daily))
    application.add_handler(CommandHandler("unset", unset_timer))
    application.add_handler(CommandHandler("unset_all", remove_all_timers))
    application.add_handler(CommandHandler("show", show_timers))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

# start - Initializes the scheduler
# set_t - Set a one-time task with description. Usage: /set_t 120 Empty the dishwasher (Insert an amount of seconds from the current moment as the offset)
# set_d - Set a daily task at the specified time with description. Usage: /set_d 15:45:30 Take out trash (Time can also be without seconds)
# unset - Deletes the specified timer from the list of active timers. Usage: /unset 5
# unset_all - Deletes all tasks for the current chat. Usage /unset_all
# show - Shows all currently active tasks. Usage: /show