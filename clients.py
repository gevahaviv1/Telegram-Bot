# clients.py

from telethon import TelegramClient
from telethon.sessions import StringSession
from config import USER_API_ID, USER_API_HASH, PHONE_NUMBER, BOT_TOKEN

# Initialize the user client
user_client = TelegramClient('user_session', USER_API_ID, USER_API_HASH)

# Initialize the bot client with an in-memory session
bot_client = TelegramClient(StringSession(), USER_API_ID, USER_API_HASH)

