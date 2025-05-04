#!/usr/bin/env python3
"""
Language support module for the Telegram Travel Bot.
Handles user language preferences, translation of bot responses,
and localization management.
"""

import json
import logging
import os
import sqlite3
from typing import Dict, Optional, Tuple

import requests
from telegram import Update
import langid
from langdetect import detect_langs

# === Configure Logging ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# === Constants ===
DB_PATH = 'finalproject.db'
TRANSLATIONS_DIR = 'translations'

# Default language if not set
DEFAULT_LANGUAGE = 'en'

# Supported languages with their display names
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'es': 'Español',
    'fr': 'Français',
    'de': 'Deutsch',
    'ru': 'Русский',
    'zh': '中文',
    'ar': 'العربية',
    'ja': '日本語',
    'pt': 'Português',
    'it': 'Italiano'
}

DETECTION_CONFIDENCE_THRESHOLD = 0.80



# === Database Functions ===

def setup_language_table():
    """Create language preferences table if it doesn't exist."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_language (
                    user_id INTEGER PRIMARY KEY,
                    language_code TEXT NOT NULL DEFAULT 'en'
                )
            ''')
            conn.commit()
            logger.info("Language table setup complete")
    except sqlite3.Error as e:
        logger.error(f"Database error setting up language table: {e}")


async def get_user_language(user_id: int) -> str:
    """
    Get user's preferred language code.

    Args:
        user_id: Telegram user ID

    Returns:
        Language code (e.g., 'en', 'es')
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT language_code FROM user_language WHERE user_id = ?',
                (user_id,)
            )
            result = cursor.fetchone()

            if result:
                return result[0]
            else:
                # If user doesn't have a language set, add default
                cursor.execute(
                    'INSERT INTO user_language (user_id, language_code) VALUES (?, ?)',
                    (user_id, DEFAULT_LANGUAGE)
                )
                conn.commit()
                return DEFAULT_LANGUAGE

    except sqlite3.Error as e:
        logger.error(f"Database error getting user language: {e}")
        return DEFAULT_LANGUAGE


async def set_user_language(user_id: int, language_code: str) -> bool:
    """
    Set user's preferred language.

    Args:
        user_id: Telegram user ID
        language_code: Language code to set

    Returns:
        Success status
    """
    if language_code not in SUPPORTED_LANGUAGES:
        return False

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO user_language (user_id, language_code) 
                   VALUES (?, ?)
                   ON CONFLICT(user_id) 
                   DO UPDATE SET language_code = ?''',
                (user_id, language_code, language_code)
            )
            conn.commit()
            return True
    except sqlite3.Error as e:
        logger.error(f"Database error setting user language: {e}")
        return False


# === Translation Functions ===

def load_translation_file(language_code: str) -> Dict:
    """
    Load translation strings from file.

    Args:
        language_code: Language code to load

    Returns:
        Dictionary of translated strings
    """
    # Make sure translations directory exists
    if not os.path.exists(TRANSLATIONS_DIR):
        os.makedirs(TRANSLATIONS_DIR)

    file_path = os.path.join(TRANSLATIONS_DIR, f"{language_code}.json")

    # If translation file doesn't exist, create an empty one
    if not os.path.exists(file_path):
        if language_code != DEFAULT_LANGUAGE:
            # Copy strings from default language as a starting point
            strings = load_translation_file(DEFAULT_LANGUAGE)
        else:
            strings = {}

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(strings, f, ensure_ascii=False, indent=2)

        return strings

    # Load existing translation file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Error loading translation file {file_path}: {e}")
        return {}


def translate_string(text: str, language_code: str, translate_api_key: str = None,
                     translate_url: str = None) -> str:
    """
    Translate a string to the target language.

    This first checks for the string in the translation files.
    If not found and API keys are provided, it uses the translation API.

    Args:
        text: Text to translate
        language_code: Target language code
        translate_api_key: Optional API key for translation service
        translate_url: Optional URL for translation service

    Returns:
        Translated text or original if translation failed
    """
    # If requested language is English or same as default, return original
    if language_code == DEFAULT_LANGUAGE:
        return text

    # Look up in translation files
    translations = load_translation_file(language_code)
    if text in translations:
        return translations[text]

    # If we have API keys, try to translate
    if translate_api_key and translate_url:
        try:
            params = {
                'key': translate_api_key,
                'text': text,
                'lang': f"{DEFAULT_LANGUAGE}-{language_code}"
            }
            response = requests.get(translate_url, params=params, timeout=5)

            if response.status_code == 200:
                data = response.json()
                translation = ' '.join(data.get('text', []))

                if translation:
                    # Store translation for future use
                    translations[text] = translation

                    file_path = os.path.join(TRANSLATIONS_DIR, f"{language_code}.json")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(translations, f, ensure_ascii=False, indent=2)

                    return translation

        except Exception as e:
            logger.error(f"Translation API error: {e}")

    # Return original text if translation fails
    return text


# === Utility Functions ===

import langid


def detect_language(text: str) -> Tuple[str, float]:
    """
    Detect the language of a given text string, returning the top language code and confidence.

    Uses langid for speed with a fallback to langdetect for higher confidence when needed.

    Args:
        text: Input text to detect

    Returns:
        Tuple of (language_code, confidence)
    """
    # Primary detection via langid
    langid.set_languages(list(SUPPORTED_LANGUAGES.keys()))
    language, confidence = langid.classify(text)

    # If confidence is low, fallback to langdetect for ensemble
    if confidence < DETECTION_CONFIDENCE_THRESHOLD:
        try:
            # detect_langs returns list of Language objects with prob
            results = detect_langs(text)
            if results:
                top = results[0]
                language = top.lang
                confidence = top.prob
                logger.debug(f"Fallback detection: {language} with confidence {confidence}")
        except Exception as e:
            logger.warning(f"Fallback langdetect error: {e}")

    # Normalize Chinese codes
    if language.lower() in ('zh-cn', 'zh-tw'):
        language = 'zh'

    # Ensure supported
    if language not in SUPPORTED_LANGUAGES:
        logger.info(f"Detected unsupported language '{language}', defaulting to {DEFAULT_LANGUAGE}")
        return DEFAULT_LANGUAGE, 1.0

    return language

# Initialize language support when module is loaded
setup_language_table()


async def _(text: str, update: Update) -> str:
    """
    Shorthand function to translate text based on user's language preference.

    Args:
        text: Text to translate
        update: Telegram update object to get user ID

    Returns:
        Translated text
    """
    user_id = update.effective_user.id
    lang_code = await get_user_language(user_id)
    return translate_string(
        text,
        lang_code
    )
