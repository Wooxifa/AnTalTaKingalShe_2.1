#!/usr/bin/env python3
"""
Telegram Travel Bot with Geocode, Weather, Flight Search, Currency Conversion, Translation, and Config File Support
"""

import configparser

import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
)

from registration import reg

# === Load Configuration ===
config = configparser.ConfigParser()
config.read('config.ini')

TELEGRAM_TOKEN = config['telegram']['token']
YANDEX_API_KEY = config['yandex']['geocoder_api_key']
OPENWEATHER_API_KEY = config['openweather']['OPENWEATHER_API_KEY']
SKYSCANNER_API_KEY = config['skyscanner']['api_key']
EXCHANGE_API_KEY = config['exchange']['api_key']
YANDEX_TRANSLATE_KEY = config['yandex']['translate_api_key']

# === API Endpoints ===
YANDEX_GEOCODER_URL = config['yandex']['geocoder_url']
OPENWEATHER_URL = config['openweather']['OPENWEATHER_URL']
sky_base_url = config['skyscanner']['url']
exchange_url = config['exchange']['url']
translate_url = config['yandex']['translate_url']


# === Helper Functions ===

def get_coordinates(location_name: str):
    params = {"apikey": YANDEX_API_KEY, "geocode": location_name,
              "format": "json", "lang": "en_US", "results": 1}
    resp = requests.get(YANDEX_GEOCODER_URL, params=params, timeout=10)
    data = resp.json()
    members = data.get("response", {}).get("GeoObjectCollection", {}).get("featureMember", [])
    if not members:
        return None
    lon, lat = members[0]["GeoObject"]["Point"]["pos"].split()
    return float(lat), float(lon)


def get_weather(lat: float, lon: float):
    params = {'lat': lat, 'lon': lon, 'appid': OPENWEATHER_API_KEY, 'units': 'metric'}
    resp = requests.get(OPENWEATHER_URL, params=params, timeout=10)
    if resp.status_code != 200:
        return None
    data = resp.json()
    return data['weather'][0]['description'], data['main']['temp']


def search_flights(origin, dest, date):
    # Example: US/USD/en-US
    url = f"{sky_base_url}US/USD/en-US/{origin}-sky/{dest}-sky/{date}"
    resp = requests.get(url, params={'apiKey': SKYSCANNER_API_KEY})
    if resp.status_code != 200:
        return None
    data = resp.json()
    # Pick first quote
    quotes = data.get('Quotes', [])
    if not quotes:
        return None
    quote = quotes[0]
    return quote.get('MinPrice'), quote.get('Direct')


def convert_currency(amount: float, frm: str, to: str):
    url = f"{exchange_url}{EXCHANGE_API_KEY}/pair/{frm}/{to}/{amount}"
    resp = requests.get(url)
    if resp.status_code != 200:
        return None
    data = resp.json()
    return data.get('conversion_result')


def translate_text(text: str, lang: str):
    params = {'key': YANDEX_TRANSLATE_KEY, 'text': text, 'lang': lang}
    resp = requests.get(translate_url, params=params)
    if resp.status_code != 200:
        return None
    data = resp.json()
    return ' '.join(data.get('text', []))


# === Command Handlers ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton("Geocode", callback_data='btn_geocode'),
         InlineKeyboardButton("Weather", callback_data='btn_weather')],
        [InlineKeyboardButton("Flights", callback_data='btn_flights'),
         InlineKeyboardButton("Currency", callback_data='btn_currency')],
        [InlineKeyboardButton("Translate", callback_data='btn_translate'),
         InlineKeyboardButton("Help", callback_data='btn_help')]
    ]
    reply = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("Welcome! Choose an option:", reply_markup=reply)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "/geocode <location> - Get coordinates\n"
        "/weather <location> - Get current weather\n"
        "/flights <orig> <dest> <YYYY-MM-DD> - Search cheap flight\n"
        "/currency <amount> <from> <to> - Currency conversion\n"
        "/translate <lang> <text> - Translate text"
    )
    await update.message.reply_text(text)


async def geocode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("Usage: /geocode <location>")
    coords = get_coordinates(' '.join(context.args))
    await update.message.reply_text(f"Coordinates: {coords}" if coords else "Not found.")


async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("Usage: /weather <location>")
    coords = get_coordinates(' '.join(context.args))
    if not coords: return await update.message.reply_text("Location not found.")
    w = get_weather(*coords)
    await update.message.reply_text(f"Weather: {w[0]}, {w[1]}°C" if w else "Weather error.")


async def flights_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 3: return await update.message.reply_text("Usage: /flights <orig> <dest> <YYYY-MM-DD>")
    price = search_flights(*context.args)
    await update.message.reply_text(f"Cheapest: ${price[0]}, direct={price[1]}" if price else "No quotes.")


async def currency_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 3: return await update.message.reply_text("Usage: /currency <amount> <from> <to>")
    res = convert_currency(float(context.args[0]), context.args[1], context.args[2])
    await update.message.reply_text(f"Converted: {res}" if res else "Conversion error.")


async def translate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2: return await update.message.reply_text("Usage: /translate <lang> <text>")
    target = context.args[0];
    text = ' '.join(context.args[1:])
    trans = translate_text(text, target)
    await update.message.reply_text(f"Translation: {trans}" if trans else "Translate error.")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data
    await update.callback_query.answer()
    await update.callback_query.message.reply_text({
                                                       'btn_geocode': "Type /geocode <location>",
                                                       'btn_weather': "Type /weather <location>",
                                                       'btn_flights': "Type /flights <orig> <dest> <YYYY-MM-DD>",
                                                       'btn_currency': "Type /currency <amount> <from> <to>",
                                                       'btn_translate': "Type /translate <lang> <text>",
                                                       'btn_help': "Type /help"
                                                   }[data])


async def idr(update: Update, context):
    await update.message.reply_text(str(update.effective_user.id))


# === Main ===

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    # app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("geocode", geocode_command))
    app.add_handler(CommandHandler("weather", weather_command))
    app.add_handler(CommandHandler("flights", flights_command))
    app.add_handler(CommandHandler("currency", currency_command))
    app.add_handler(CommandHandler("translate", translate_command))
    app.add_handler(CommandHandler("id", idr))
    app.add_handler(reg)
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()


if __name__ == "__main__":
    main()

# === config.ini ===
# [telegram]
# token = YOUR_TELEGRAM_BOT_TOKEN
# [yandex]
# geocoder_key = YOUR_YANDEX_API_KEY
# translate_key = YOUR_YANDEX_TRANSLATE_KEY
# [openweather]
# api_key = YOUR_OPENWEATHER_API_KEY
# [skyscanner]
# api_key = YOUR_SKYSCANNER_API_KEY
# [exchange]
# api_key = YOUR_EXCHANGE_API_KEY
