# main.py

import logging
import asyncio
from clients import user_client, bot_client
from config import PHONE_NUMBER, LOGGING_LEVEL
from config import BOT_TOKEN
import handlers  # Ensure handlers are imported
from telethon.errors import SessionPasswordNeededError

# Set up logging
logging.basicConfig(level=LOGGING_LEVEL)
logger = logging.getLogger(__name__)

async def main():
    # Start the user client
    await user_client.start(phone=PHONE_NUMBER)

    # If 2FA is enabled, you might need to enter the password
    if await user_client.is_user_authorized():
        logger.info("User client is authorized.")
    else:
        try:
            await user_client.sign_in(PHONE_NUMBER)
            logger.info("User client signed in.")
        except SessionPasswordNeededError:
            password = input("Two-step verification enabled. Please enter your password: ")
            await user_client.sign_in(password=password)

    # Start the bot client
    await bot_client.start(bot_token=BOT_TOKEN)
    logger.info("Bot client started.")

    print("Bot is running and listening to messages...")
    await asyncio.gather(
        user_client.run_until_disconnected(),
        bot_client.run_until_disconnected()
    )

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())

