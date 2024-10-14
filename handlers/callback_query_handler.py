from telethon import events
from clients import user_client, bot_client
from config import TARGET_CHANNEL, ADMIN_CHAT_ID
from handlers.new_message_handler import pending_messages, editing_messages
import logging
from telethon.errors import MessageNotModifiedError

logger = logging.getLogger(__name__)

@bot_client.on(events.CallbackQuery)
async def callback_query_handler(event):
    try:
        data = event.data.decode('utf-8')
        user_id = event.sender_id

        if data.startswith("approve_") or data.startswith("disapprove_") or data.startswith("edit_"):
            action, unique_id = data.split("_", 1)

            # Retrieve the original message
            message = pending_messages.get(unique_id)

            if not message:
                await event.answer("Message not found or already processed.", alert=True)
                return

            # Fetch the approval message
            approval_msg = await event.get_message()

            if action == "approve":
                # Forward the message to the target channel using the user client
                await user_client.send_message(entity=TARGET_CHANNEL, message=message)
                await approval_msg.edit(f"✅ **Message Approved and Forwarded**\n\n{message.text}", buttons=None)
                logger.info(f"Message ID {unique_id} approved and forwarded to {TARGET_CHANNEL}.")

                # Remove the message from pending_messages
                del pending_messages[unique_id]

            elif action == "disapprove":
                await approval_msg.edit("❌ **Message Disapproved**", buttons=None)
                logger.info(f"Message ID {unique_id} disapproved and not forwarded.")

                # Remove the message from pending_messages
                del pending_messages[unique_id]

            elif action == "edit":
                await approval_msg.edit("✏️ **Please send the edited message text.**", buttons=None)
                logger.info(f"Message ID {unique_id} is being edited by user {user_id}.")

                # Store the state that the user is editing this message
                editing_messages[ADMIN_CHAT_ID] = {
                    'unique_id': unique_id,
                    'approval_msg_id': approval_msg.id  # To update the same message later
                }

    except MessageNotModifiedError:
        # Ignore the error if the content hasn't changed
        logger.warning("Attempted to edit message but content was not modified.")
    except Exception as e:
        logger.error(f"An error occurred in callback_query_handler: {e}")

