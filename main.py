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
    # инициализация баллов в user_data
    context.user_data['res_score'] = 0

    # список вопросов и вариантов ответа
    questions = [
        {
            "question": "1. Твоё любимое время года?",
            "options": ["зима", "лето", "осень", "весна"],
            "points": [1, 2, 3, 4]  # баллы за каждый вариант
        },
        {
            "question": "2. Выбери, что больше всего тебя описывает?",
            "options": ["экстраверт (общительный)", "интроверт (стеснительный)",
                        "амбиверт (среднее между первым и вторым)", "омниверт (зависит от настроения)"],
            "points": [4, 1, 2, 3]
        },
        {
            "question": "3. Какой у тебя тип темперамента?",
            "options": ["сангвиник (экстраверты, активные)",
                        "холерик (экстраверты, лидеры, холодные)",
                        "меланхолик (интроверты, ранимые)",
                        "флегматик (интроверты, терпеливые, надёжные)"],
            "points": [4, 3, 1, 2]
        },
        {
            "question": "4. Какие шутки вам нравятся?",
            "options": ["про колобка/русалку", "про евреев",
                        "про маты", "жестокие"],
            "points": [1, 2, 3, 4]
        },
        {
            "question": "5. Какой вид науки наиболее близок вам?",
            "options": ["естественные", "технические",
                        "социальные", "гуманитарные"],
            "points": [4, 3, 2, 1]
        },
        {
            "question": "6. Какие цвета вас больше всего привлекают?",
            "options": ["холодные", "тёплые", "нейтральные (чб)", "всё и сразу"],
            "points": [1, 4, 2, 3]
        },
        {
            "question": "7. Какой фильм из предложенных вам нраится больше всего?",
            "options": ["1+1", "Хатико", "Шерлок Холмс", "Голодные игры"],
            "points": [4, 3, 2, 1]
        },
        {
            "question": "8. Какой жанр музыки вам больше всего нравится?",
            "options": ["поп", "рок", "хип-хоп", "классическая"],
            "points": [2, 4, 3, 1]
        },
        {
            "question": "9. Какое ваше любимое времяпровождение?",
            "options": ["чтение книг", "просмотр сериалов",
                        "спорт и активные игры", "прогулки"],
            "points": [1, 2, 4, 3]
        },
        {
            "question": "10. Какой ваш любимый напиток?",
            "options": ["газировка", "кофе", "чай", "сок"],
            "points": [2, 4, 3, 1]
        },
        {
            "question": "11. Что вы предпочитаете?",
            "options": ["путешествия", "просмотр фильма",
                        "вечеринки", "Занятия творчеством"],
            "points": [1, 2, 3, 4]
        },
        {
            "question": "12. Какое качество вы цените в себе больше всего?",
            "options": ["надёжность", "креативность", "общительность", "спокойствие"],
            "points": [4, 1, 2, 3]
        },
        {
            "question": "13. Как вы реагируете на неожиданные изменения в планах?",
            "options": ["спокойно адаптируюсь",
                        "немного расстраиваюсь",
                        "сильно переживаю",
                        "радуюсь новым возможностям"],
            "points": [4, 3, 1, 2]
        },
        {
            "question": "14. Какой напиток вы выберете к завтраку?",
            "options": ["кофе", "чай", "сок", "вода"],
            "points": [1, 2, 3, 4]
        },
        {
            "question": "15. Как вы относитесь к новым знакомствам?",
            "options": ["легко и с энтузиазмом", "с осторожностью",
                        "предпочитаю проверенных друзей", "зависит от настроения"],
            "points": [4, 3, 2, 1]
        },
        {
            "question": "16. Какой стиль одежды вам ближе?",
            "options": ["классический", "спортивный", "кэжуал", "экстравагантный"],
            "points": [1, 4, 2, 3]
        },
        {
            "question": "17. Как вы справляетесь с конфликтными ситуациями?",
            "options": ["компромисс", "борьба до конца", "избегание", "когда как"],
            "points": [4, 3, 2, 1]
        },
        {
            "question": "18. Какую кухню вы предпочитаете?",
            "options": ["итальянскую", "азиатскую", "домашнюю", "экзотическую"],
            "points": [2, 4, 3, 1]
        },
        {
            "question": "19. Как вы относитесь к работе в команде?",
            "options": ["нравится", "нет, я за самостоятельность",
                        "могу и так и так", "когда как"],
            "points": [1, 2, 4, 3]
        },
        {
            "question": "20. Какой жанр фильмов вам нравится больше всего?",
            "options": ["комедия", "драма", "фантастика", "документальный"],
            "points": [2, 4, 3, 1]
        },
        {
            "question": "21. С чем лучше всего есть хлеб?",
            "options": ["ни с чем", "с сыром и вином",
                        "со святой водой", "с голодными собаками"],
            "points": [1, 2, 3, 4]
        },
        {
            "question": "22. Сколько хлеб можно хранить?",
            "options": ["день", "неделю", "испорченный лучше", "вечность"],
            "points": [4, 1, 2, 3]
        },
        {
            "question": "23. Какой ты хлеб в культуре?",
            "options": ["«Булочник» Кустодиева",
                        "«Баллада о хлебе» Кузнецова",
                        "«Евангелие от Иоанна, глава 6",
                        "«Советские хлебы» Ильи Машковой"],
            "points": [4, 3, 1, 2]
        },
        {
            "question": "24. Что вы думаете о еде на ночь?",
            "options": ["да, конечно!", "нет, потолстею", "немного", "религия не позволяет"],
            "points": [1, 2, 3, 4]
        },
        {
            "question": "25. Кто ты на пикнике с шашлыком?",
            "options": ["лаваш", "лепёшка",
                        "корочка", "уксус"],
            "points": [4, 3, 2, 1]
        },
        {
            "question": "26. Какой у тебя любимый бутерброд?",
            "options": ["с майонезом и кетчупом", "с колбасой", "горячий", "тост"],
            "points": [1, 4, 2, 3]
        },
        {
            "question": "27. Какой у тебя любимый соус?",
            "options": ["сырный", "кисло-сладкий", "кетчунез", "тереяки"],
            "points": [4, 3, 2, 1]
        },
        {
            "question": "28. Что без хлеба не едят?",
            "options": ["борщ", "стейк", "ничего", "всё"],
            "points": [2, 4, 3, 1]
        },
        {
            "question": "29. Какие у тебя любимые печенки в виде животных?",
            "options": ["зоологические", "фигурные песочные",
                        "печенье «Забавные зверушки»", "печенье «Зоопарк»"],
            "points": [1, 2, 4, 3]
        },
        {
            "question": "30. Какая самая легендарная сладость?",
            "options": ["тульский пряник", "калужское тесто",
                        "пасхальный кулич", "чесночный хлеб"],
            "points": [2, 4, 3, 1]
        }
    ]

    # функция отправки вопроса
    async def send_question(index: int) -> None:
        if index < len(questions):
            question = questions[index]
            # создаем клавиатуру с кнопками в две строки
            keyboard = [
                [KeyboardButton(option) for option in question["options"][:2]],  # первая строка
                [KeyboardButton(option) for option in question["options"][2:]]   # вторая строка
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text(question["question"], reply_markup=reply_markup)
        else:
            # подсчет баллов
            res_score = context.user_data['res_score']
            await update.message.reply_text(f"Тест завершен! Ваши баллы: {res_score}")

    # ответ пользователя
    async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_answer = update.message.text
        question_index = len(context.user_data.get('answers', []))  # определяем индекс вопроса по количеству ответов

        if question_index < len(questions):
            question = questions[question_index]
            if user_answer in question["options"]:
                answer_index = question["options"].index(user_answer)
                # обновляем баллы
                context.user_data['res_score'] += question["points"][answer_index]
                # сохраняем ответ
                context.user_data.setdefault('answers', []).append(user_answer)
                # отправка следующего вопроса
                await send_question(question_index + 1)
            else:
                await update.message.reply_text("Пожалуйста, выберите один из предложенных вариантов.")

    # добавление обработчика ответов
    context.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))

    # начало теста от первого вопроса
    await send_question(0)


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
