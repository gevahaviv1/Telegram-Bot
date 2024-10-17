import logging
import asyncio
from clients import user_client, bot_client
from config import PHONE_NUMBER, LOGGING_LEVEL, BOT_TOKEN
from telethon.errors import SessionPasswordNeededError
from handlers.new_message_handler import new_message_listener
from handlers.callback_query_handler import callback_query_handler
from handlers.edit_message_handler import edit_message_handler

# Set up logging
logging.basicConfig(level=LOGGING_LEVEL)
logger = logging.getLogger(__name__)

async def main():
    # Start the user client
    await user_client.start(phone=PHONE_NUMBER)

    # If 2FA is enabled, handle it properly
    if not await user_client.is_user_authorized():
        try:
            await user_client.sign_in(PHONE_NUMBER)
        except SessionPasswordNeededError:
            password = input("Enter your password for two-step verification: ")
            await user_client.sign_in(password=password)
        logger.info("User client signed in.")

    # Start the bot client
    await bot_client.start(bot_token=BOT_TOKEN)
    logger.info("Bot client started and running.")

    # Run both clients until disconnected
    await asyncio.gather(
        user_client.run_until_disconnected(),
        bot_client.run_until_disconnected()
    )

if __name__ == '__main__':
    asyncio.run(main())

