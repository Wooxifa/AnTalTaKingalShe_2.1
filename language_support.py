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
import re

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
    # First try to load from translations directory
    translation_paths = [
        os.path.join(TRANSLATIONS_DIR, f"{language_code}.json"),  # Standard path
        f"{language_code}.json"  # Root directory fallback
    ]

    for file_path in translation_paths:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                logger.error(f"Error loading translation file {file_path}: {e}")

    # If we get here, no valid translation file was found
    if language_code != DEFAULT_LANGUAGE:
        logger.warning(f"No translation file found for {language_code}, falling back to {DEFAULT_LANGUAGE}")
        return load_translation_file(DEFAULT_LANGUAGE)
    else:
        logger.error(f"Default language file {DEFAULT_LANGUAGE}.json not found!")
        return {}


def translate_string(text: str, language_code: str) -> str:
    """
    Translate a string to the target language.

    This checks for the string in the translation files.
    If translation fails, returns the original text.

    Args:
        text: Text to translate
        language_code: Target language code

    Returns:
        Translated text or original if translation failed
    """
    # If requested language is English or same as default, return original
    if language_code == DEFAULT_LANGUAGE:
        return text

    # Look up in translation files
    translations = load_translation_file(language_code)

    # If we have a direct translation, use it
    if text in translations:
        return translations[text]

    # Format strings with placeholders won't be exact matches
    # Let's try to find partial matches for format strings
    if '{' in text and '}' in text:
        for original, translated in translations.items():
            if ('{' in original and '}' in original and
                    len(original.split()) == len(text.split())):
                # Replace placeholders with regex patterns
                pattern = re.escape(original).replace('\\{.*?\\}', '(.*?)')
                match = re.match(pattern, text)
                if match:
                    # Extract values and format the translated string
                    values = match.groups()
                    result = translated
                    for i, value in enumerate(values):
                        placeholder = f"{{{i}}}"
                        result = result.replace(placeholder, value)
                    return result

    # Return original text if translation fails
    logger.debug(f"No translation found for '{text}' in {language_code}")
    return text


# === Utility Functions ===

import langid


def detect_language(text: str) -> str:
    """
    Detect the language of a given text string, returning the language code.

    Uses langid for speed with a fallback to langdetect for higher confidence when needed.

    Args:
        text: Input text to detect

    Returns:
        Language code string
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
        return DEFAULT_LANGUAGE

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
