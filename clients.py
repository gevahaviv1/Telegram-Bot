import os
from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Load sensitive data from environment variables for security
USER_API_ID = os.getenv('USER_API_ID')
USER_API_HASH = os.getenv('USER_API_HASH')

# Initialize the user client with a user session
user_client = TelegramClient('user_session', USER_API_ID, USER_API_HASH)

# Initialize the bot client with an in-memory session
bot_client = TelegramClient(StringSession(), USER_API_ID, USER_API_HASH)

