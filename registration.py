#!/usr/bin/env python3
"""
User registration module for the Telegram Travel Bot.
Handles user registration flow and database operations.
"""

import logging
import sqlite3
from datetime import datetime
from typing import Optional, Tuple

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters, Application,
)

from language_support import _

# === Constants ===
DB_PATH = 'finalproject.db'

# Registration conversation states
ASK_PASSWORD, ASK_GENDER, ASK_BIRTHDAY = range(3)

# === Configure Logging ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# === Database Helper Functions ===

async def _user_exists(user_id: int) -> bool:
    """Check if the user is already in the database."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT 1 FROM logining WHERE login = ?',
                (user_id,)
            )
            return cursor.fetchone() is not None
    except sqlite3.Error as e:
        logger.error(f"Database error checking user existence: {e}")
        return False


async def _add_user(user_id: int, password: str, gender: str, birthday: datetime) -> bool:
    """
    Insert new user into the database.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO logining
                   (login, password, gender, day, month, year)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (
                    user_id,
                    password,
                    gender,
                    birthday.day,
                    birthday.month,
                    birthday.year
                )
            )
            conn.commit()
            return True
    except sqlite3.Error as e:
        logger.error(f"Database error adding user: {e}")
        return False


# === Conversation Handlers ===

async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start registration or notify if already registered."""
    user_id = update.effective_user.id

    # Check if user already exists
    if await _user_exists(user_id):
        await update.message.reply_text(await _("You are already registered.", update))
        return ConversationHandler.END

    # Begin registration process
    await update.message.reply_text("Welcome! Please choose a password:")
    return ASK_PASSWORD


async def ask_gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Save password and prompt for gender selection."""
    # Store password in user data
    context.user_data['password'] = update.message.text.strip()

    # Create gender selection buttons
    buttons = [
        [InlineKeyboardButton("Male", callback_data="man")],
        [InlineKeyboardButton("Female", callback_data="woman")],
        [InlineKeyboardButton("Female", callback_data="bread")]
    ]
    markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(
        "Select your gender:",
        reply_markup=markup
    )
    return ASK_GENDER


async def get_gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle gender callback and ask for birthday."""
    query = update.callback_query
    await query.answer()

    # Store gender selection
    gender = query.data
    context.user_data['gender'] = gender

    await query.edit_message_text(f"Gender selected: {gender}")
    await query.message.reply_text(
        "Now enter your birthday in YYYY-MM-DD format:"
    )

    return ASK_BIRTHDAY


async def ask_birthday(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Validate birthday, save user data, and complete registration."""
    birthday_text = update.message.text.strip()

    # Validate birthday format
    try:
        birthday = datetime.strptime(birthday_text, "%Y-%m-%d")
    except ValueError:
        await update.message.reply_text(
            "Invalid format. Please enter your birthday as YYYY-MM-DD."
        )
        return ASK_BIRTHDAY

    # Get user data
    user_id = update.effective_user.id
    password = context.user_data.get('password', '')
    gender = context.user_data.get('gender', '')

    # Save user in database
    context.user_data['birthday'] = birthday
    success = await _add_user(user_id, password, gender, birthday)

    if success:
        await update.message.reply_text(
            f"Registration complete! 🎉\n"
            f"User ID: {user_id}\n"
            f"Gender: {gender}\n"
            f"Birthday: {birthday.date()}"
        )
    else:
        await update.message.reply_text(
            "There was an error completing your registration. Please try again later."
        )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle user cancellation."""
    await update.message.reply_text("Registration canceled.")
    context.user_data.clear()  # Clear any stored data
    return ConversationHandler.END


# === Registration Conversation Handler Setup ===

reg = ConversationHandler(
    entry_points=[CommandHandler('registration', start_registration)],
    states={
        ASK_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_gender)],
        ASK_GENDER: [CallbackQueryHandler(get_gender, pattern='^(Male|Female)$')],
        ASK_BIRTHDAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_birthday)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)