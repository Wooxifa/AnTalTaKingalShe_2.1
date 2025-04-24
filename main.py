import logging
import random
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from datetime import datetime

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

jokes = [
    "Почему программисты не любят природу? Потому что в ней слишком много багов.",
    "Какой язык программирования самый оптимистичный? Python, потому что он всегда находит решение!",
    "Почему Java разработчики предпочитают темный кофе? Потому что светлый кофе вызывает исключение!"
]

quotes = [
    "Будущее зависит от того, что вы делаете сегодня. — Махатма Ганди",
    "Не бойтесь делать ошибки. Учитесь на них. — Ричард Бренсон",
    "Секрет успеха в том, чтобы начать. — Марк Твен"
]


async def start(update, context):
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет {user.mention_html()}! Я эхо-бот. Напишите мне что-нибудь, и я пришлю это назад!",
    )


async def echo(update, context):
    response_message = f"Я получил сообщение: {update.message.text}"
    await update.message.reply_text(response_message)


async def help_command(update, context):
    await update.message.reply_text(
        "Я могу помочь с следующими командами:\n/start - начать общение\n/help - помощь\n/time - текущее время\n/date - текущая дата\n/joke - получить шутку\n/quote - получить цитату")


async def time_command(update, context):
    current_time = datetime.now().strftime("%H:%M:%S")
    await update.message.reply_text(f"Текущее время: {current_time}")


async def date_command(update, context):
    current_date = datetime.now().strftime("%Y-%m-%d")
    await update.message.reply_text(f"Текущая дата: {current_date}")


async def joke_command(update, context):
    joke = random.choice(jokes)
    await update.message.reply_text(joke)


async def quote_command(update, context):
    quote = random.choice(quotes)
    await update.message.reply_text(quote)


def main():
    application = Application.builder().token("7426528925:AAGMlHmJSM8GBy02Wf0j5edzUg2QmucPjc4").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("time", time_command))
    application.add_handler(CommandHandler("date", date_command))
    application.add_handler(CommandHandler("joke", joke_command))
    application.add_handler(CommandHandler("quote", quote_command))

    text_handler = MessageHandler(filters.TEXT, echo)
    application.add_handler(text_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
