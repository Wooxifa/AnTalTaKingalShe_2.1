import sqlite3
import os
# import logging
# from telegram.ext import Application, MessageHandler, filters


#login = "aaa" проверка
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


async def zodiac_detect():
    gender_sql = """SELECT gender FROM logining WHERE login = ?"""
    gender, = cur.execute(gender_sql, (login,)).fetchone()
    day_sql = """SELECT day FROM logining WHERE login = ?"""
    day, = cur.execute(day_sql, (login,)).fetchone()
    month_sql = """SELECT month FROM logining WHERE login = ?"""
    month, = cur.execute(month_sql, (login,)).fetchone()
    zodiac_sql = """UPDATE logining SET zodiacid = ? WHERE login = ?"""
    if gender == 'man':
        list_id = 0
    elif gender == 'woman':
        list_id = 1
    elif gender == 'cat':
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
    #print(zodiac_id) чисто проверка
    cur.execute(zodiac_sql, (zodiac_id, login))
    con.commit()

con.close()
