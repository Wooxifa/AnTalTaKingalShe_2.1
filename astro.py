import sqlite3
import os
import random
import pycountry

man_lexicon = {
    1: 1,
    2: 2,
    3: 3,
    4: 4,
    5: 5,
    6: 6,
    7: 7,
    8: 8,
    9: 9,
    10: 10,
    11: 11,
    12: 12
}
woman_lexicon = {
    1: 13,
    2: 14,
    3: 15,
    4: 16,
    5: 17,
    6: 18,
    7: 19,
    8: 20,
    9: 21,
    10: 22,
    11: 23,
    12: 24
}
cat_lexicon = {
    1: 25,
    2: 26,
    3: 27,
    4: 28,
    5: 29,
    6: 30,
    7: 31,
    8: 32,
    9: 33,
    10: 34,
    11: 35,
    12: 36
}
list_lexicon = [man_lexicon, woman_lexicon, cat_lexicon]
db_name = 'finalproject.db'
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), db_name)
if not os.path.exists(db_path):
    print(f"База данных не найдена: {db_path}.")
else:
    try:
        con = sqlite3.connect(db_path)
        print(f"Подключено к базе данных: {db_path}.")
        cur = con.cursor()
    except sqlite3.Error as e:
        print(f"Ошибка при подключении к базе данных: {e}.")


async def zodiac_detect(update, context):
    #назначается знак зодиака
    gender_sql = """SELECT gender FROM logining WHERE login = ?"""
    gender, = cur.execute(gender_sql, ((context.user_data['login']),)).fetchone()
    day_sql = """SELECT day FROM logining WHERE login = ?"""
    day, = cur.execute(day_sql, ((context.user_data['login']),)).fetchone()
    month_sql = """SELECT month FROM logining WHERE login = ?"""
    month, = cur.execute(month_sql, ((context.user_data['login']),)).fetchone()
    zodiac_sql = """UPDATE logining SET znak_zodiac_id = ? WHERE login = ?"""
    if gender == 'man':
        list_id = 0
    elif gender == 'woman':
        list_id = 1
    elif gender == 'bread':
        list_id = 2
    if (day >= 22 and month == 12) or (day <= 20 and month == 1):
        list_id_zodiac = 1
    elif (day >= 21 and month == 1) or (day <= 18 and month == 2):
        list_id_zodiac = 2
    elif (day >= 19 and month == 2) or (day <= 20 and month == 3):
        list_id_zodiac = 3
    elif (day >= 21 and month == 3) or (day <= 19 and month == 4):
        list_id_zodiac = 4
    elif (day >= 20 and month == 4) or (day <= 20 and month == 5):
        list_id_zodiac = 5
    elif (day >= 21 and month == 5) or (day <= 21 and month == 6):
        list_id_zodiac = 6
    elif (day >= 22 and month == 6) or (day <= 22 and month == 7):
        list_id_zodiac = 7
    elif (day >= 23 and month == 7) or (day <= 22 and month == 22):
        list_id_zodiac = 8
    elif (day >= 23 and month == 8) or (day <= 22 and month == 9):
        list_id_zodiac = 9
    elif (day >= 23 and month == 9) or (day <= 23 and month == 10):
        list_id_zodiac = 10
    elif (day >= 24 and month == 10) or (day <= 22 and month == 11):
        list_id_zodiac = 11
    elif (day >= 23 and month == 11) or (day <= 21 and month == 12):
        list_id_zodiac = 12
    zodiac_id = list_lexicon[list_id][list_id_zodiac]
    cur.execute(zodiac_sql, (zodiac_id, context.user_data['login']))
    con.commit()


async def astro_descr(update, context):
    # определяем знак зодиака и гендер
    # по ни ищется файл и выводится из него текст и из другого файла картинка
    gender_sql = """SELECT gender FROM logining WHERE login = ?"""
    gender, = cur.execute(gender_sql, ((context.user_data['login']),)).fetchone()
    zodiac_sql = '''
                SELECT zodiac_idshnik.zodiac_name
                FROM logining
                JOIN zodiac ON logining.znak_zodiac_id = zodiac.znak_zodiac_id
                JOIN zodiac_idshnik ON zodiac.zodiac_id = zodiac_idshnik.zodiac_id
                WHERE logining.login = ?
                '''
    zodiac, = cur.execute(zodiac_sql, ((context.user_data['login']),)).fetchone()
    text_file = os.path.join("astro_descr", f"{zodiac}", f"{gender}.txt")
    photo_file = os.path.join("astra_photo", f"{zodiac}_{gender}.jpg")
    try:
        with open(text_file, "r", encoding="utf-8") as f:
            text_content = f.read()
    except Exception as e:
        await update.message.reply_text(f"Ошибка при чтении текстового файла: {e}")
        return
    await update.message.reply_text(text_content)

    try:
        with open(photo_file, "rb") as photo:
            await update.message.reply_photo(photo)
    except Exception as e:
        await update.message.reply_text(f"Ошибка при отправке изображения: {e}")


async def choose_random_country(update, context):
    countries = list(pycountry.countries)
    random_country = random.choice(countries)
    # Сохраняем данные о случайной стране
    random_country_data = random_country.name
    context.user_data["country"] = random_country_data
    await update.message.reply_text(f"Ваша случайная страна - {random_country_data}")


async def echo_country(update, context):
    context.user_data["country"] = update.message.text
    await update.message.reply_text(f"Ваша введённая страна - {update.message.text}")


async def print_astro(update, context):
    # выводит знак зодиака пользователя
    zodiac_sql = '''
                    SELECT zodiac_idshnik.zodiac_name
                    FROM logining
                    JOIN zodiac ON logining.znak_zodiac_id = zodiac.znak_zodiac_id
                    JOIN zodiac_idshnik ON zodiac.zodiac_id = zodiac_idshnik.zodiac_id
                    WHERE logining.login = ?
                    '''
    zodiac, = cur.execute(zodiac_sql, ((context.user_data['login']),)).fetchone()
    await update.message.reply_text(f"Ваш знак зодиака - {znak_zodiaka}")


con.close()
