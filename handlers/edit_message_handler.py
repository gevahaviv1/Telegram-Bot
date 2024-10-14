from telethon import events, types, Button
from clients import bot_client
from config import ADMIN_CHAT_ID
from handlers.new_message_handler import pending_messages, editing_messages
import logging

logger = logging.getLogger(__name__)

@bot_client.on(events.NewMessage)
async def edit_message_handler(event):
    chat_id = event.chat_id
    user_id = event.sender_id

    logger.info(f"edited_message_handler triggered by user {user_id} in chat {chat_id}")

    # Check if the user is in the editing state and the message is from the admin chat
    if chat_id in editing_messages:
        edit_info = editing_messages[chat_id]
        unique_id = edit_info['unique_id']
        approval_msg_id = edit_info['approval_msg_id']

        # Get the original message
        original_message = pending_messages.get(unique_id)

        if not original_message:
            await event.reply("Original message not found or already processed.")
            # Clean up the editing state
            del editing_messages[user_id]
            return

        # Update the message text with the edited text
        edited_text = event.message.text
        original_message.text = edited_text

        # Update the approval message with the edited text and approval buttons
        buttons = [
            [
                Button.inline("✅ Approve", data=f"approve_{unique_id}"),
                Button.inline("❌ Disapprove", data=f"disapprove_{unique_id}")
            ]
        ]

        await bot_client.edit_message(
            ADMIN_CHAT_ID,
            approval_msg_id,
            f"**Edited Message:**\n\n{edited_text}",
            buttons=buttons
        )

        logger.info(f"Message ID {unique_id} has been edited by user {user_id}.")

        # Clean up the editing state
        del editing_messages[user_id]
    else:
        logger.info(f"User {chat_id} is not in editing state.")

