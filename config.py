import os
from dotenv import load_dotenv

# Define the path to the .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Telegram API credentials
USER_API_ID = os.getenv('USER_API_ID')
USER_API_HASH = os.getenv('USER_API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')

# Bot token (from @BotFather)
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Channels and groups
SOURCE_CHANNELS = os.getenv('SOURCE_CHANNELS').split(',')
TARGET_CHANNEL = os.getenv('TARGET_CHANNEL')
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID'))

# Other configurations
LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'INFO')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


