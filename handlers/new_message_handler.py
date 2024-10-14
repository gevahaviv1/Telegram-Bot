# handlers/new_message_handler.py

from telethon import events, Button
from clients import user_client, bot_client
from config import SOURCE_CHANNEL, ADMIN_CHAT_ID
import logging

# Dictionaries to store pending and editing messages
pending_messages = {}
editing_messages = {}

logger = logging.getLogger(__name__)

@user_client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def new_message_listener(event):
    try:
        message = event.message

        # Log the received message
        logger.info(f"New message from {SOURCE_CHANNEL}: {message.text}")

        # Generate a unique ID for tracking
        unique_id = f"{message.chat_id}_{message.id}"

        # Store the message content for later reference
        pending_messages[unique_id] = message

        # Create approval buttons with the new "Edit" button
        buttons = [
            [
                Button.inline("✅ Approve", data=f"approve_{unique_id}"),
                Button.inline("❌ Disapprove", data=f"disapprove_{unique_id}"),
                Button.inline("✏️ Edit", data=f"edit_{unique_id}")
            ]
        ]

        # Send the message to the admin chat for approval using the bot
        approval_msg = await bot_client.send_message(
            entity=ADMIN_CHAT_ID,
            message=f"New message from **{SOURCE_CHANNEL}**:\n\n{message.text}",
            buttons=buttons,
            parse_mode='markdown'
        )

        logger.info(f"Approval request sent for message ID: {unique_id} (Message to admin: {approval_msg.id})")

    except Exception as e:
        logger.error(f"An error occurred in new_message_listener: {e}")

