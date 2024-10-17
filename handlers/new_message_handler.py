import io
from telethon import events, Button, types
import mimetypes
import logging
import asyncio
from PIL import Image
from clients import user_client, bot_client
from config import ADMIN_CHAT_ID, SOURCE_CHANNELS
from utils import get_media_info  # Import the utility function

# Dictionaries to store pending and editing messages
pending_messages = {}
editing_messages = {}

logger = logging.getLogger(__name__)

@user_client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def new_message_listener(event):
    try:
        message = event.message
        chat = await event.get_chat()
        chat_title = chat.title or 'Unknown Chat'
        chat_username = chat.username or str(chat.id)
        source_channel = chat_username  # Use this for identification

        logger.info(f"New message from {chat_title}: {message.text or 'Media message'}")

        unique_id = f"{message.chat_id}_{message.id}"

        message_info = {
            'text': message.text,
            'media': None,
            'source_channel': source_channel,
            'media_type': None,
            'approval_msg_id': None  # Add this to store approval message ID
        }

        # Use the utility function to handle media
        if message.media:
            message_info['media'] = get_media_info(message)
        else:
            message_info['media'] = None

        pending_messages[unique_id] = message_info

        # Add the "AI" button alongside existing buttons
        buttons = [
            [
                Button.inline("✅ Approve", data=f"approve_{unique_id}"),
                Button.inline("❌ Disapprove", data=f"disapprove_{unique_id}"),
                Button.inline("✏️ Edit", data=f"edit_{unique_id}"),
                Button.inline("🤖 AI", data=f"ai_{unique_id}")
            ]
        ]

        # Send the approval message and store its message ID
        if message_info['media']:
            if message_info['media']['is_photo']:
                approval_msg = await bot_client.send_file(
                    entity=ADMIN_CHAT_ID,
                    file=message_info['media']['file'],
                    caption=f"New message from **{chat_title}**:\n\n{message_info['text'] or ''}",
                    buttons=buttons,
                    parse_mode='markdown'
                )
            else:
                attributes = []
                if message_info['media_type'] == 'document':
                    attributes.append(types.DocumentAttributeFilename(file_name=message_info['media']['filename']))

                approval_msg = await bot_client.send_file(
                    entity=ADMIN_CHAT_ID,
                    file=message_info['media']['file'],
                    caption=f"New message from **{chat_title}**:\n\n{message_info['text'] or ''}",
                    attributes=attributes,
                    buttons=buttons,
                    parse_mode='markdown'
                )
        else:
            approval_msg = await bot_client.send_message(
                entity=ADMIN_CHAT_ID,
                message=f"New message from **{chat_title}**:\n\n{message_info['text']}",
                buttons=buttons,
                parse_mode='markdown'
            )

        # Store the approval message ID in message_info
        message_info['approval_msg_id'] = approval_msg.id

        logger.info(f"Approval request sent for message ID: {unique_id}")

        # Schedule a deletion task
        asyncio.create_task(schedule_deletion(unique_id, approval_msg.id))

    except Exception as e:
        logger.error(f"An error occurred in new_message_listener: {e}")

async def schedule_deletion(unique_id, approval_msg_id):
    # Wait for the specified timeout duration
    await asyncio.sleep(108000)  # Adjust the timeout as needed (e.g., 20 seconds)

    # Check if the message is still pending
    if unique_id in pending_messages:
        message_info = pending_messages[unique_id]
        if message_info.get('editing', False):
            logger.info(f"Message ID {unique_id} is being edited; skipping deletion.")
            return  # Do not delete if the message is being edited

        try:
            # Delete the approval message from the admin group
            await bot_client.delete_messages(ADMIN_CHAT_ID, approval_msg_id)
            logger.info(f"Approval message for ID {unique_id} deleted after timeout.")

            # Remove the message from pending_messages
            del pending_messages[unique_id]

        except Exception as e:
            logger.error(f"Error deleting approval message for ID {unique_id}: {e}")

