from telethon import events, Button, types
from config import ADMIN_CHAT_ID
from clients import bot_client
from handlers.new_message_handler import pending_messages, editing_messages
from PIL import Image
import logging
import io

logger = logging.getLogger(__name__)

@bot_client.on(events.NewMessage(chats=ADMIN_CHAT_ID))
async def edit_message_handler(event):
    chat_id = event.chat_id

    logger.info(f"edit_message_handler triggered in chat {chat_id}")

    if chat_id in editing_messages:
        edit_info = editing_messages[chat_id]
        unique_id = edit_info['unique_id']
        approval_msg_id = edit_info['approval_msg_id']

        # Get original message details
        message_info = pending_messages.get(unique_id)

        if not message_info:
            await event.reply("Original message not found or already processed.")
            del editing_messages[chat_id]
            return

        # Update text
        edited_message = event.message
        new_text = edited_message.text
        if new_text:
            message_info['ai_text'] = new_text  # This will update the AI processed text
            message_info['text'] = new_text  # Also update the original text

        # If new media is provided, update it; otherwise, keep the existing media
        if edited_message.media:
            media_bytes = await edited_message.download_media(file=io.BytesIO())
            media_bytes.seek(0)

            media_file = media_bytes
            filename = 'file'

            # Determine media type
            if edited_message.photo:
                # It's a photo
                is_photo = True
                media_file.name = 'image.jpg'
                message_info['media_type'] = 'photo'
            elif edited_message.video:
                # It's a video
                is_photo = False
                filename = 'video.mp4'
                media_file.name = filename
                message_info['media_type'] = 'video'
            else:
                # Other media types (documents, audio, etc.)
                is_photo = False
                # Try to get the original filename
                if edited_message.document:
                    for attr in edited_message.document.attributes:
                        if isinstance(attr, types.DocumentAttributeFilename):
                            filename = attr.file_name
                            break
                    else:
                        # Use mime type to guess extension
                        mime_type = edited_message.document.mime_type or ''
                        extension = mimetypes.guess_extension(mime_type) or ''
                        filename = f'file{extension}'
                media_file.name = filename
                message_info['media_type'] = 'document'

            message_info['media'] = {
                'file': media_file,
                'is_photo': is_photo,
                'filename': filename
            }
        else:
            # If no new media is provided, retain the original media
            pass  # No action needed; existing media remains

        # Update the approval message
        buttons = [
            [
                Button.inline("✅ Approve", data=f"approve_{unique_id}"),
                Button.inline("❌ Disapprove", data=f"disapprove_{unique_id}"),
                Button.inline("🤖 AI", data=f"ai_{unique_id}")
            ]
        ]

        # Use edit_message to update both text and caption (for media)
        if message_info['media']:
            await bot_client.send_file(
                ADMIN_CHAT_ID,
                file=message_info['media']['file'],
                caption=f"**Edited Message:**\n\n{message_info['text']}",
                buttons=buttons,
                parse_mode='markdown'
            )
            # Delete the old approval message
            await bot_client.delete_messages(ADMIN_CHAT_ID, approval_msg_id)
        else:
            await bot_client.edit_message(
                ADMIN_CHAT_ID,
                approval_msg_id,
                text=f"**Edited Message:**\n\n{message_info['text']}",
                buttons=buttons,
                parse_mode='markdown'
            )

        logger.info(f"Message ID {unique_id} has been edited.")
        del editing_messages[chat_id]
    else:
        logger.info(f"Chat {chat_id} is not in editing state or message is not from admin chat.")

