from telethon import events, types
from clients import user_client, bot_client
from config import TARGET_CHANNEL, ADMIN_CHAT_ID
from handlers.new_message_handler import pending_messages, editing_messages
from telethon.errors import MessageNotModifiedError
from PIL import Image
import logging
import io

logger = logging.getLogger(__name__)

@bot_client.on(events.CallbackQuery)
async def callback_query_handler(event):
    try:
        data = event.data.decode('utf-8')
        chat_id = event.chat_id

        if data.startswith("approve_") or data.startswith("disapprove_") or data.startswith("edit_"):
            action, unique_id = data.split("_", 1)

            # Retrieve message details
            message_info = pending_messages.get(unique_id)

            if not message_info:
                await event.answer("Message not found or already processed.", alert=True)
                return

            # Get the approval message
            approval_msg = await event.get_message()

            if action == "approve":
                text = message_info['text']
                media = message_info.get('media', None)

                if media:
                    media['file'].seek(0)

                    if media['is_photo']:
                        await user_client.send_file(
                            entity=TARGET_CHANNEL,
                            file=media['file'],
                            caption=text or '',
                        )
                    else:
                        attributes = []
                        if message_info['media_type'] == 'document':
                            attributes.append(types.DocumentAttributeFilename(file_name=media['filename']))

                        await user_client.send_file(
                            entity=TARGET_CHANNEL,
                            file=media['file'],
                            caption=text or '',
                            attributes=attributes,
                        )
                else:
                    await user_client.send_message(
                        entity=TARGET_CHANNEL,
                        message=text
                    )

                await approval_msg.edit(f"✅ **Message Approved and Forwarded**\n\n{text or 'Media message'}", buttons=None)
                logger.info(f"Message ID {unique_id} approved and forwarded to {TARGET_CHANNEL}.")

                # Remove from pending_messages
                del pending_messages[unique_id]

            elif action == "disapprove":
                await approval_msg.edit("❌ **Message Disapproved**", buttons=None)
                logger.info(f"Message ID {unique_id} disapproved.")
                del pending_messages[unique_id]

            elif action == "edit":
                await approval_msg.edit("✏️ **Please send the edited message text or media.**", buttons=None)
                editing_messages[ADMIN_CHAT_ID] = {
                    'unique_id': unique_id,
                    'approval_msg_id': approval_msg.id
                }
    except Exception as e:
        logger.error(f"An error occurred in callback_query_handler: {e}")

