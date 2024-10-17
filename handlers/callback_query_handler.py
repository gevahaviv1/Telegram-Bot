# callback_query_handler.py

from clients import user_client, bot_client
from config import TARGET_CHANNEL, ADMIN_CHAT_ID, OPENAI_API_KEY
from handlers.new_message_handler import pending_messages, editing_messages
from telethon.errors import MessageNotModifiedError
from telethon import events, Button, types
import openai
import io
import logging
import asyncio
from langdetect import detect  # Import the language detection module

logger = logging.getLogger(__name__)

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

print('callback')
@bot_client.on(events.CallbackQuery)
async def callback_query_handler(event):
    try:
        data = event.data.decode('utf-8')
        chat_id = event.chat_id
        logger.info(f"Callback triggered: {data}")

        # Initialize action and unique_id
        action = None
        unique_id = None

        # Updated action parsing to include 'approve', 'disapprove', and 'edit' actions
        if data.startswith("approve_ai_"):
            action = "approve_ai"
            unique_id = data[len("approve_ai_"):]
        elif data.startswith("disapprove_ai_"):
            action = "disapprove_ai"
            unique_id = data[len("disapprove_ai_"):]
        elif data.startswith("edit_ai_"):
            action = "edit_ai"
            unique_id = data[len("edit_ai_"):]
        elif data.startswith("ai_"):
            action = "ai"
            unique_id = data[len("ai_"):]
        elif data.startswith("approve_"):
            action = "approve"
            unique_id = data[len("approve_"):]
        elif data.startswith("disapprove_"):
            action = "disapprove"
            unique_id = data[len("disapprove_"):]
        elif data.startswith("edit_"):
            action = "edit"
            unique_id = data[len("edit_"):]
        else:
            logger.error(f"Unknown action in data: {data}")
            await event.answer("Unknown action.", alert=True)
            return

        # Check if action and unique_id are properly set
        if action is None or unique_id is None:
            logger.error(f"Action or unique_id not set. Data: {data}")
            await event.answer("Invalid action.", alert=True)
            return

        logger.info(f"Action: {action} | Unique ID: {unique_id}")

        # Retrieve message details
        message_info = pending_messages.get(unique_id)

        if not message_info:
            logger.error(f"Message ID {unique_id} not found in pending_messages")
            await event.answer("Message not found or already processed.", alert=True)
            return

        approval_msg = await event.get_message()

        if action == "approve":
            # Handle approval of original message
            try:
                text = message_info['text']
                media = message_info['media']
                if media:
                    # Reset file pointer to the beginning
                    media['file'].seek(0)

                    if media['is_photo']:
                        await user_client.send_file(
                            TARGET_CHANNEL,
                            file=media['file'],
                            caption=text
                        )
                    else:
                        await user_client.send_file(
                            TARGET_CHANNEL,
                            file=media['file'],
                            caption=text,
                            attributes=[types.DocumentAttributeFilename(file_name=media['filename'])]
                        )
                else:
                    await user_client.send_message(TARGET_CHANNEL, text)

                await approval_msg.edit(f"✅ **Message Approved**\n\n{text}", buttons=None)
                logger.info(f"Message approved for ID: {unique_id}")

                # Remove from pending_messages after successful approval
                del pending_messages[unique_id]

            except Exception as e:
                logger.error(f"Error approving message: {e}")
                await event.answer("Failed to approve the message.", alert=True)

        elif action == "disapprove":
            try:
                await approval_msg.edit("❌ **Message Disapproved**", buttons=None)
                logger.info(f"Message disapproved for ID: {unique_id}")

                # Remove from pending_messages after successful disapproval
                del pending_messages[unique_id]

            except Exception as e:
                logger.error(f"Error disapproving message: {e}")
                await event.answer("Failed to disapprove the message.", alert=True)

        elif action == "edit":
            message_info['editing'] = True  # Indicate that the message is being edited
            editing_messages[chat_id] = {'unique_id': unique_id, 'approval_msg_id': approval_msg.id}
            await approval_msg.edit("✏️ **Send the edited message.**", buttons=None)

        elif action == "ai":
            original_text = message_info['text'] or ""
            if not original_text.strip():
                await event.answer("No text available to process with AI.", alert=True)
                return

            logger.info(f"Sending message to OpenAI for AI processing for message ID {unique_id}")

            # Detect language
            try:
                detected_language = detect(original_text)
            except Exception as e:
                detected_language = 'en'
                logger.error(f"Language detection failed: {e}, defaulting to English.")

            # Updated prompt
            prompt = (
                f"Please improve readability and maintain meaning of the following text. "
                f"Provide only the improved text without any additional explanations or notes. "
                f"The text is in {detected_language}."
            )

            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a helpful assistant that only outputs the improved text "
                                "without any additional explanations or notes."
                            )
                        },
                        {
                            "role": "user",
                            "content": f"{prompt}\n\nOriginal Text:\n{original_text}"
                        }
                    ],
                    max_tokens=1000,
                    temperature=0.7,
                )

                ai_text = response.choices[0].message['content'].strip()
                message_info['ai_text'] = ai_text

                # Update the buttons with Approve and Disapprove options
                ai_buttons = [
                    [Button.inline("✅ Approve AI", data=f"approve_ai_{unique_id}"),
                     Button.inline("❌ Disapprove AI", data=f"disapprove_ai_{unique_id}")],
                    [Button.inline("✏️ Edit AI", data=f"edit_ai_{unique_id}")]
                ]

                await approval_msg.edit(f"🤖 **AI-Processed Message**:\n\n{ai_text}", buttons=ai_buttons)

            except Exception as e:
                logger.error(f"Error communicating with OpenAI: {e}")
                await event.answer("Failed to process AI message.", alert=True)

        elif action == "approve_ai":
            ai_text = message_info.get('ai_text', '')
            if not ai_text:
                logger.error(f"No AI-processed text found for {unique_id}")
                await event.answer("No AI text available.", alert=True)
                return

            try:
                media = message_info['media']
                if media:
                    # Reset file pointer to the beginning
                    media['file'].seek(0)

                    if media['is_photo']:
                        await user_client.send_file(
                            TARGET_CHANNEL,
                            file=media['file'],
                            caption=ai_text
                        )
                    else:
                        await user_client.send_file(
                            TARGET_CHANNEL,
                            file=media['file'],
                            caption=ai_text,
                            attributes=[types.DocumentAttributeFilename(file_name=media['filename'])]
                        )
                else:
                    await user_client.send_message(TARGET_CHANNEL, ai_text)

                await approval_msg.edit(f"✅ **AI-Processed Message Approved**", buttons=None)
                logger.info(f"AI-Processed message approved for ID: {unique_id}")

                # Remove from pending_messages after successful approval
                del pending_messages[unique_id]

            except Exception as e:
                logger.error(f"Error approving AI-processed message: {e}")
                await event.answer("Failed to approve the message.", alert=True)

        elif action == "disapprove_ai":
            try:
                await approval_msg.edit("❌ **AI-Processed Message Disapproved**", buttons=None)
                logger.info(f"AI-Processed message disapproved for ID: {unique_id}")

                # Remove from pending_messages after successful disapproval
                del pending_messages[unique_id]

            except Exception as e:
                logger.error(f"Error disapproving AI-processed message: {e}")
                await event.answer("Failed to disapprove the message.", alert=True)

        elif action == "edit_ai":
            message_info['editing'] = True  # Indicate that the message is being edited
            editing_messages[chat_id] = {'unique_id': unique_id, 'approval_msg_id': approval_msg.id, 'is_ai': True}
            await approval_msg.edit("✏️ **Send the edited message.**", buttons=None)

    except Exception as e:
        logger.error(f"An error occurred in callback_query_handler: {e}")

