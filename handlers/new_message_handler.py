from telethon import events, Button, types
from clients import user_client, bot_client
from config import SOURCE_CHANNELS, ADMIN_CHAT_ID
from PIL import Image
import logging
import io
import mimetypes

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
            'media_type': None
        }

        if message.media:
            media_bytes = await message.download_media(file=io.BytesIO())
            media_bytes.seek(0)

            media_file = media_bytes
            filename = 'file'

            # Determine media type
            if message.photo:
                # It's a photo
                is_photo = True
                media_file.name = 'image.jpg'
                message_info['media_type'] = 'photo'
            elif message.video:
                # It's a video
                is_photo = False
                filename = 'video.mp4'
                media_file.name = filename
                message_info['media_type'] = 'video'
            else:
                # Other media types (documents, audio, etc.)
                is_photo = False
                # Try to get the original filename
                if message.document:
                    for attr in message.document.attributes:
                        if isinstance(attr, types.DocumentAttributeFilename):
                            filename = attr.file_name
                            break
                    else:
                        # Use mime type to guess extension
                        mime_type = message.document.mime_type or ''
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
            message_info['media'] = None

        pending_messages[unique_id] = message_info

        buttons = [
            [
                Button.inline("✅ Approve", data=f"approve_{unique_id}"),
                Button.inline("❌ Disapprove", data=f"disapprove_{unique_id}"),
                Button.inline("✏️ Edit", data=f"edit_{unique_id}")
            ]
        ]

        if message_info['media']:
            if message_info['media']['is_photo']:
                # Send photo without attributes
                await bot_client.send_file(
                    entity=ADMIN_CHAT_ID,
                    file=message_info['media']['file'],
                    caption=f"New message from **{chat_title}**:\n\n{message_info['text'] or ''}",
                    buttons=buttons,
                    parse_mode='markdown'
                )
            else:
                # Send other media types with attributes if necessary
                attributes = []
                if message_info['media_type'] == 'document':
                    attributes.append(types.DocumentAttributeFilename(file_name=message_info['media']['filename']))

                await bot_client.send_file(
                    entity=ADMIN_CHAT_ID,
                    file=message_info['media']['file'],
                    caption=f"New message from **{chat_title}**:\n\n{message_info['text'] or ''}",
                    attributes=attributes,
                    buttons=buttons,
                    parse_mode='markdown'
                )
        else:
            await bot_client.send_message(
                entity=ADMIN_CHAT_ID,
                message=f"New message from **{chat_title}**:\n\n{message_info['text']}",
                buttons=buttons,
                parse_mode='markdown'
            )

        logger.info(f"Approval request sent for message ID: {unique_id}")
    except Exception as e:
        logger.error(f"An error occurred in new_message_listener: {e}")

