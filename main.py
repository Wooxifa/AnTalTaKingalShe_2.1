import logging
import random
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from datetime import datetime

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

# это временно ради прикола, потом удалим
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


# старт и приветственная фраза
async def start(update, context):
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет {user.mention_html()}! Спасибо, что используешь этот бот. Загляни в перечень команд написав /help",
    )


# список с командами
async def help_command(update, context):
    await update.message.reply_text(
        "Я могу помочь с следующими командами:\n"
        "/start - начать общение\n"
        "/help - помощь\n"
        "/time - текущее время\n"
        "/date - текущая дата\n"
        "/joke - получить шутку\n"
        "/quote - получить цитату\n"
        "/bread_test - тест 'какой ты хлебушек'")


# вывлод времени но это так, балуюсь
async def time_command(update, context):
    current_time = datetime.now().strftime("%H:%M:%S")
    await update.message.reply_text(f"Текущее время: {current_time}")


# тоже баловство, удалю потом
async def date_command(update, context):
    current_date = datetime.now().strftime("%Y-%m-%d")
    await update.message.reply_text(f"Текущая дата: {current_date}")


# просто вывод шутки, удалю потом
async def joke_command(update, context):
    joke = random.choice(jokes)
    await update.message.reply_text(joke)


# и это надо будеть удалить, не обращайте внимание
async def quote_command(update, context):
    quote = random.choice(quotes)
    await update.message.reply_text(quote)


async def bread_test_command(update, context):
    # список вопросов и варииантов ответа
    questions = [
        {
            "question": "Какой ваш любимый цвет?",
            "options": ["Красный", "Синий", "Зеленый"]
        },
        {
            "question": "Какой ваш любимый фрукт?",
            "options": ["Яблоко", "Банан", "Апельсин"]
        }
    ]

    # функция отправки вопроса
    async def send_question(index: int) -> None:
        if index < len(questions):
            question = questions[index]
            keyboard = [
                [InlineKeyboardButton(option, callback_data=f"q{index}_{option}") for option in question["options"]]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(question["question"], reply_markup=reply_markup)
        else:
            await update.message.reply_text("Тест завершен! Спасибо за участие.")

    # начало теста от первого вопроса
    await send_question(0)

    # ответ пользователя
    async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        data = query.data.split("_")
        question_index = int(data[0][1])
        answer = data[1]

        context.user_data[f"answer_{question_index}"] = answer

        # отправка следующего вопроса
        await send_question(question_index + 1)

    context.application.add_handler(CallbackQueryHandler(handle_answer))


def main():
    application = Application.builder().token("7426528925:AAGMlHmJSM8GBy02Wf0j5edzUg2QmucPjc4").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("time", time_command))
    application.add_handler(CommandHandler("date", date_command))
    application.add_handler(CommandHandler("joke", joke_command))
    application.add_handler(CommandHandler("quote", quote_command))
    application.add_handler(CommandHandler("bread_test", bread_test_command))

    # text_handler = MessageHandler(filters.TEXT, echo)
    # application.add_handler(text_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
