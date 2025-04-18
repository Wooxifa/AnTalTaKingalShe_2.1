--
-- Файл сгенерирован с помощью SQLiteStudio v3.4.4 в Пт апр 18 14:59:12 2025
--
-- Использованная кодировка текста: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Таблица: logining
CREATE TABLE IF NOT EXISTS logining (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, login TEXT UNIQUE, password, day INTEGER, month INTEGER, year INTEGER, gender TEXT, zodiac INTEGER REFERENCES zodiac (id));

-- Таблица: name_zodiac
CREATE TABLE IF NOT EXISTS name_zodiac (idnamez INTEGER PRIMARY KEY AUTOINCREMENT, name_z TEXT);
INSERT INTO name_zodiac (idnamez, name_z) VALUES (1, 'Capricorn');
INSERT INTO name_zodiac (idnamez, name_z) VALUES (2, 'Aquarius');
INSERT INTO name_zodiac (idnamez, name_z) VALUES (3, 'Pisces');
INSERT INTO name_zodiac (idnamez, name_z) VALUES (4, 'Aries');
INSERT INTO name_zodiac (idnamez, name_z) VALUES (5, 'Taurus');
INSERT INTO name_zodiac (idnamez, name_z) VALUES (6, 'Gemini');
INSERT INTO name_zodiac (idnamez, name_z) VALUES (7, 'Cancer');
INSERT INTO name_zodiac (idnamez, name_z) VALUES (8, 'Leo');
INSERT INTO name_zodiac (idnamez, name_z) VALUES (9, 'Virgo');
INSERT INTO name_zodiac (idnamez, name_z) VALUES (10, 'Libra');
INSERT INTO name_zodiac (idnamez, name_z) VALUES (11, 'Scorpio');
INSERT INTO name_zodiac (idnamez, name_z) VALUES (12, 'Sagittarius');

-- Таблица: zodiac
CREATE TABLE IF NOT EXISTS zodiac (zodiacID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, zodiac_znak INTEGER REFERENCES name_zodiac (idnamez), cat_photo TEXT);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (1, 1, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (2, 2, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (3, 3, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (4, 4, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (5, 5, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (6, 6, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (7, 7, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (8, 8, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (9, 9, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (10, 10, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (11, 11, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (12, 12, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (13, 1, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (14, 2, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (15, 3, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (16, 4, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (17, 5, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (18, 6, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (19, 7, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (20, 8, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (21, 9, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (22, 10, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (23, 11, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (24, 12, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (25, 1, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (26, 2, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (27, 3, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (28, 4, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (29, 5, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (30, 6, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (31, 7, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (32, 8, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (33, 9, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (34, 10, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (35, 11, NULL);
INSERT INTO zodiac (zodiacID, zodiac_znak, cat_photo) VALUES (36, 12, NULL);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
