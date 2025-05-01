import logging
import sqlite3
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Constants
DB_PATH = 'finalproject.db'

# Register conversation states
ASK_PASSWORD, ASK_GENDER, ASK_BIRTHDAY = range(3)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start registration or notify if already registered."""
    user_id = update.effective_user.id
    if await _user_exists(user_id):
        await update.message.reply_text("You are already registered.")
        return ConversationHandler.END

    await update.message.reply_text("Welcome! Please choose a password:")
    return ASK_PASSWORD


async def ask_gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Save password and prompt for gender selection."""
    context.user_data['password'] = update.message.text.strip()
    buttons = [
        [InlineKeyboardButton("Male", callback_data="Male")],
        [InlineKeyboardButton("Female", callback_data="Female")],
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
    gender = query.data
    context.user_data['gender'] = gender
    await query.edit_message_text(f"Gender selected: {gender}")

    await query.message.reply_text(
        "Now enter your birthday in YYYY-MM-DD format:"
    )
    return ASK_BIRTHDAY


async def ask_birthday(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Validate birthday, save user data, and complete registration."""
    text = update.message.text.strip()
    try:
        bday = datetime.strptime(text, "%Y-%m-%d")
    except ValueError:
        await update.message.reply_text(
            "Invalid format. Please enter your birthday as YYYY-MM-DD."
        )
        return ASK_BIRTHDAY

    context.user_data['birthday'] = bday
    user_id = update.effective_user.id
    pwd = context.user_data['password']
    gender = context.user_data['gender']

    await _add_user(user_id, pwd, gender, bday)
    await update.message.reply_text(
        f"Registration complete! 🎉\n"
        f"User: {user_id}\n"
        f"Gender: {gender}\n"
        f"Birthday: {bday.date()}"
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle user cancellation."""
    await update.message.reply_text("Registration canceled.")
    return ConversationHandler.END


async def _user_exists(user_id: int) -> bool:
    """Check if the user is already in the database."""
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            'SELECT 1 FROM logining WHERE login = ?',
            (user_id,)
        )
        return cur.fetchone() is not None


async def _add_user(user_id: int, password: str, gender: str, birthday: datetime) -> None:
    """Insert new user into the database."""
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
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


reg = ConversationHandler(
    entry_points=[CommandHandler('start', start_registration)],
    states={
        ASK_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_gender)],
        ASK_GENDER: [CallbackQueryHandler(get_gender, pattern='^(Male|Female)$')],
        ASK_BIRTHDAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_birthday)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)
