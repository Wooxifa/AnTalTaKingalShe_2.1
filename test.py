#!/usr/bin/env python3
"""
Telegram Travel Bot with Geocode, Weather, Flight Search, Currency Conversion,
Translation, and Multilingual Support
"""

import configparser
import io
import aiohttp
import logging
from typing import Optional, Tuple

import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler,
    MessageHandler, filters
)

from registration import reg
from language_support import (
    get_user_language, set_user_language, translate_string,
    SUPPORTED_LANGUAGES, detect_language, _
)
from weather_images import create_weather_image

# === Configure Logging ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,filename='log%(asctime)s'
)
logger = logging.getLogger(__name__)


# === Load Configuration ===
def load_config(config_path: str = 'config.ini') -> configparser.ConfigParser:
    """Load configuration from file."""
    config = configparser.ConfigParser()
    config.read(config_path)
    return config


config = load_config()

# === API Configuration ===
TELEGRAM_TOKEN = config['telegram']['token']
YANDEX_API_KEY = config['yandex']['geocoder_api_key']
OPENWEATHER_API_KEY = config['openweather']['OPENWEATHER_API_KEY']
SKYSCANNER_API_KEY = config['skyscanner']['api_key']
EXCHANGE_API_KEY = config['exchange']['api_key']
AMADEUS_CLIENT_ID = "K9PjoxlKXgA5jlrORsC1gIfVYm8j2Ck4"
AMADEUS_CLIENT_SECRET = "Srwi47S3JMPJcpSf"

# === API Endpoints ===
YANDEX_GEOCODER_URL = config['yandex']['geocoder_url']
OPENWEATHER_URL = config['openweather']['OPENWEATHER_URL']
SKYSCANNER_URL = config['skyscanner']['url']
EXCHANGE_URL = config['exchange']['url']
AMADEUS_AUTH_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
AMADEUS_FLIGHT_URL = "https://test.api.amadeus.com/v2/shopping/flight-offers"
# === API Helper Functions ===

def get_coordinates(location_name: str) -> Optional[Tuple[float, float]]:
    """Get geographic coordinates for a location name."""
    try:
        params = {
            "apikey": YANDEX_API_KEY,
            "geocode": location_name,
            "format": "json",
            "lang": "en_US",
            "results": 1
        }
        response = requests.get(YANDEX_GEOCODER_URL, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        members = data.get("response", {}).get("GeoObjectCollection", {}).get("featureMember", [])

        if not members:
            return None

        lon, lat = members[0]["GeoObject"]["Point"]["pos"].split()
        return float(lat), float(lon)
    except (requests.RequestException, KeyError, ValueError) as e:
        logger.error(f"Geocoding error: {e}")
        return None


def get_weather(lat: float, lon: float) -> Optional[Tuple[str, float]]:
    """Get weather description and temperature for coordinates."""
    try:
        params = {
            'lat': lat,
            'lon': lon,
            'appid': OPENWEATHER_API_KEY,
            'units': 'metric'
        }
        response = requests.get(OPENWEATHER_URL, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        return data['weather'][0]['description'], data['main']['temp']
    except (requests.RequestException, KeyError, IndexError) as e:
        logger.error(f"Weather API error: {e}")
        return None


def get_amadeus_token() -> Optional[str]:
    try:
        response = requests.post(AMADEUS_AUTH_URL, data={
            'grant_type': 'client_credentials',
            'client_id': AMADEUS_CLIENT_ID,
            'client_secret': AMADEUS_CLIENT_SECRET,
        })
        response.raise_for_status()
        return response.json()['access_token']
    except requests.RequestException as e:
        logger.error(f"Amadeus auth error: {e}")
        return None


def search_flights(origin: str, dest: str, date: str) -> Optional[Tuple[float, bool]]:
    """Search flight price and directness using Amadeus API."""
    token = get_amadeus_token()
    if not token:
        return None

    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "originLocationCode": origin,
        "destinationLocationCode": dest,
        "departureDate": date,
        "adults": 1,
        "currencyCode": "USD",
        "max": 1
    }

    try:
        response = requests.get(AMADEUS_FLIGHT_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        offers = data.get('data', [])
        if not offers:
            return None

        offer = offers[0]
        price = float(offer['price']['total'])
        segments = offer['itineraries'][0]['segments']
        is_direct = len(segments) == 1

        return price, is_direct
    except (requests.RequestException, KeyError, ValueError) as e:
        logger.error(f"Flight search error: {e}")
        return None


def convert_currency(amount: float, frm: str, to: str) -> Optional[float]:
    """Convert currency from one type to another using FreeCurrencyAPI."""
    if not EXCHANGE_API_KEY:
        logger.warning("FreeCurrency API key not configured")
        return None

    try:
        params = {
            "apikey": EXCHANGE_API_KEY,
            "base_currency": frm,
            "currencies": to
        }
        response = requests.get(EXCHANGE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        rate = data['data'].get(to)
        if rate is None:
            logger.error(f"Conversion rate for {to} not found")
            return None

        return amount * rate
    except (requests.RequestException, KeyError) as e:
        logger.error(f"Currency conversion error: {e}")
        return None


def translate_text(text: str, target_lang: str) -> Optional[str]:
    """Translate text using Google Translate (no API key needed for small usage)."""
    try:
        url = config['translation']['google_translation_url']
        params = {
            "client": "gtx",  # required “client” string
            "sl": "auto",  # auto-detect source language
            "tl": target_lang,  # target language
            "dt": "t",  # return translation
            "ie": "UTF-8",  # input encoding
            "oe": "UTF-8",  # output encoding
            "q": text
        }
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/115.0.0.0 Safari/537.36"
            )
        }

        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code != 200:
            logger.error(
                f"Translation API error: {response.status_code} – {response.text}"
            )
            return None

        result = response.json()
        # result[0] is a list of [ [translatedSegment, originalSegment, …], … ]
        translated = "".join(seg[0] for seg in result[0] if seg[0])
        return translated

    except Exception as e:
        logger.error(f"Translation error: {e}")
        return None


# === Command Handlers ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command with options menu."""
    welcome_msg = await _("Welcome! Choose an option:", update)

    buttons = [
        [InlineKeyboardButton(await _("Geocode", update), callback_data='btn_geocode'),
         InlineKeyboardButton(await _("Weather", update), callback_data='btn_weather')],
        [InlineKeyboardButton(await _("Flights", update), callback_data='btn_flights'),
         InlineKeyboardButton(await _("Currency", update), callback_data='btn_currency')],
        [InlineKeyboardButton(await _("Translate", update), callback_data='btn_translate'),
         InlineKeyboardButton(await _("Language", update), callback_data='btn_language')],
        [InlineKeyboardButton(await _("Help", update), callback_data='btn_help')]
    ]
    reply = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(welcome_msg, reply_markup=reply)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command with usage information."""
    help_text = (
            "/start - " + await _("Show main menu", update) + "\n"
                                                              "/geocode <location> - " + await _("Get coordinates",
                                                                                                 update) + "\n"
                                                                                                           "/weather <location> - " + await _(
        "Get current weather", update) + "\n"
                                         "/flights <orig> <dest> <YYYY-MM-DD> - " + await _("Search cheap flight",
                                                                                            update) + "\n"
                                                                                                      "/currency <amount> <from> <to> - " + await _(
        "Currency conversion", update) + "\n"
                                         "/translate <lang> <text> - " + await _("Translate text", update) + "\n"
                                                                                                             "/language <code> - " + await _(
        "Change bot language", update)
    )
    await update.message.reply_text(help_text)


async def geocode_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /geocode command."""
    if not context.args:
        await update.message.reply_text(await _("Usage: /geocode <location>", update))
        return

    location = ' '.join(context.args)
    coords = get_coordinates(location)

    if coords:
        await update.message.reply_text(
            (await _("Coordinates:", update)) + f" {coords}"
        )
    else:
        await update.message.reply_text(await _("Location not found.", update))


async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(await _("Usage: /weather <location>", update))
        return

    location = ' '.join(context.args)
    coords = get_coordinates(location)

    if not coords:
        await update.message.reply_text(await _("Location not found.", update))
        return

    weather_info = get_weather(*coords)
    if weather_info:
        description, temp = weather_info

        # Create weather image
        image_bio = create_weather_image(location, description, temp)
        image_bio.name = 'weather.png'

        # Send image with translated caption
        await update.message.reply_photo(
            photo=image_bio,
            caption=f"{location}: {await _(description, update)}, {temp}°C"
        )
    else:
        await update.message.reply_text(
            await _("Could not retrieve weather information.", update)
        )

async def flights_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /flights command."""
    if len(context.args) != 3:
        await update.message.reply_text(
            await _("Usage: /flights <orig> <dest> <YYYY-MM-DD>", update)
        )
        return

    origin, destination, date = context.args
    flight_info = search_flights(origin, destination, date)

    if flight_info:
        price, is_direct = flight_info
        direct_text = await _("Yes", update) if is_direct else await _("No", update)
        await update.message.reply_text(
            (await _("Cheapest:", update)) + f" ${price}, " +
            (await _("Direct:", update)) + f" {direct_text}"
        )
    else:
        await update.message.reply_text(await _("No flight quotes available.", update))


async def currency_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /currency command."""
    if len(context.args) != 3:
        await update.message.reply_text(
            await _("Usage: /currency <amount> <from> <to>", update)
        )
        return

    try:
        amount = float(context.args[0])
        from_currency = context.args[1].upper()
        to_currency = context.args[2].upper()

        result = convert_currency(amount, from_currency, to_currency)

        if result is not None:
            await update.message.reply_text(
                (await _("Converted:", update)) +
                f" {amount} {from_currency} = {result} {to_currency}"
            )
        else:
            await update.message.reply_text(await _("Currency conversion failed.", update))
    except ValueError:
        await update.message.reply_text(
            await _("Invalid amount. Please enter a number.", update)
        )


async def translate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /translate command."""
    if len(context.args) < 2:
        await update.message.reply_text(
            await _("Usage: /translate <lang> <text>", update)
        )
        return

    target_lang = context.args[0]
    text = ' '.join(context.args[1:])

    translation = translate_text(text, target_lang)

    if translation:
        await update.message.reply_text(
            (await _("Translation:", update)) + f" {translation}"
        )
    else:
        await update.message.reply_text(await _("Translation failed.", update))


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /language command to change user language preference."""
    user_id = update.effective_user.id

    # If no language code provided, show available options
    if not context.args:
        current_lang = await get_user_language(user_id)
        lang_list = "\n".join([f"{code} - {name}" for code, name in SUPPORTED_LANGUAGES.items()])

        await update.message.reply_text(
            (await _("Your current language is:", update)) +
            f" {SUPPORTED_LANGUAGES.get(current_lang, current_lang)}\n\n" +
            (await _("Available languages:", update)) + f"\n{lang_list}\n\n" +
            (await _("To change, use:", update)) + " /language <code>"
        )
        return

    # Set user language
    lang_code = context.args[0].lower()

    if lang_code in SUPPORTED_LANGUAGES:
        success = await set_user_language(user_id, lang_code)

        if success:
            # Get the language name in the new language
            lang_name = SUPPORTED_LANGUAGES[lang_code]
            await update.message.reply_text(
                (await _("Language changed to:", update)) + f" {lang_name}"
            )
        else:
            await update.message.reply_text(
                await _("Failed to update language preference.", update)
            )
    else:
        available = ", ".join(SUPPORTED_LANGUAGES.keys())
        await update.message.reply_text(
            (await _("Invalid language code. Available options:", update)) +
            f" {available}"
        )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button clicks in the interface."""
    query = update.callback_query
    await query.answer()

    button_responses = {
        'btn_geocode': await _("Type /geocode <location>", update),
        'btn_weather': await _("Type /weather <location>", update),
        'btn_flights': await _("Type /flights <orig> <dest> <YYYY-MM-DD>", update),
        'btn_currency': await _("Type /currency <amount> <from> <to>", update),
        'btn_translate': await _("Type /translate <lang> <text>", update),
        'btn_language': await _("Type /language <code> to change language", update),
        'btn_help': await _("Type /help", update)
    }

    response = button_responses.get(query.data, await _("Command not recognized", update))
    await query.message.reply_text(response)


async def get_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /id command to return user's Telegram ID."""
    user_id = update.effective_user.id
    await update.message.reply_text(
        (await _("Your Telegram ID:", update)) + f" {user_id}"
    )


async def detect_language_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle language detection and auto-switching."""
    if not update.message or not update.message.text:
        return

    text = update.message.text

    # Skip commands
    if text.startswith('/'):
        return

    # Try to detect language
    detected = detect_language(text)
    if not detected:
        return

    user_id = update.effective_user.id
    current_lang = await get_user_language(user_id)

    # If detected language differs from current setting and is supported
    if detected != current_lang and detected in SUPPORTED_LANGUAGES:
        await set_user_language(user_id, detected)
        lang_name = SUPPORTED_LANGUAGES[detected]
        await update.message.reply_text(detected)

        # Use translate_string directly with detected language to ensure message
        # is in the newly detected language
        await update.message.reply_text(
            translate_string(
                f"I've detected you're writing in {lang_name}. I'll respond in this language now.",
                detected
            )
        )