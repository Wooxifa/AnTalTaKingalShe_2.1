import logging
import random
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, Update, KeyboardButton
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


async def bread_test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # список вопросов и вариантов ответа
    questions = [
        {
            "question": "1. Твоё любимое время года?",
            "options": ["Зима", "Лето", "Осень", "Весна"]
        },
        {
            "question": "2. Выбери, что больше всего тебя описывает?",
            "options": ["экстраверт (общительный)", "интроверт (стеснительный)",
                        "амбиверт (среднее между первым и вторым)", "омниверт (зависит от настроения)"]
        },
        {
            "question": "3. Какой у тебя тип темперамента?",
            "options": ["сангвиник (экстраверты, активные)",
                        "холерик (экстраверты, лидеры, холодные)",
                        "меланхолик (интроверты, ранимые)",
                        "флегматик (интроверты, терпеливые, надёжные)"]
        },
        {
            "question": "4. Какие шутки вам нравятся?",
            "options": ["про колобка/русалку", "про евреев",
                        "про маты", "жестокие"]
        },
        {
            "question": "5. Какой вид науки наиболее близок вам?",
            "options": ["естественные", "технические",
                        "социальные", "гуманитарные"]
        },
        {
            "question": "6. Какие цвета вас больше всего привлекают?",
            "options": ["холодные", "тёплые", "нейтральные (чб)", "всё и сразу"]
        },
        {
            "question": "7. Какой фильм из предложенных вам нраится больше всего?",
            "options": ["1+1", "Хатико", "Шерлок Холмс", "Голодные игры"]
        },
        {
            "question": "8. Какой жанр музыки вам больше всего нравится?",
            "options": ["поп", "рок", "хип-хоп", "классическая"]
        },
        {
            "question": "9. Какое ваше любимое времяпровождение?",
            "options": ["чтение книг", "просмотр сериалов",
                        "спорт и активные игры", "прогулки"]
        },
        {
            "question": "10. Какой ваш любимый напиток?",
            "options": ["газировка", "кофе", "чай", "сок"]
        }
    ]

    # функция отправки вопроса
    async def send_question(index: int) -> None:
        if index < len(questions):
            question = questions[index]
            # Создаем клавиатуру с кнопками в две строки
            keyboard = [
                [KeyboardButton(option) for option in question["options"][:2]],  # Первая строка
                [KeyboardButton(option) for option in question["options"][2:]]   # Вторая строка
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text(question["question"], reply_markup=reply_markup)
        else:
            await update.message.reply_text("Тест завершен! Спасибо за участие.")

    # начало теста от первого вопроса
    await send_question(0)

    # ответ пользователя
    async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_answer = update.message.text
        question_index = len(context.user_data)  # Определяем индекс вопроса по количеству ответов

        if question_index < len(questions):
            context.user_data[f"answer_{question_index}"] = user_answer
            # отправка следующего вопроса
            await send_question(question_index + 1)

    # добавление обработчика ответов
    context.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))


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
