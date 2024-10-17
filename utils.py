import io
import mimetypes
from telethon import types

async def get_media_info(message):
    """Extracts media info from a message and returns a dictionary with media details."""
    media_bytes = io.BytesIO()
    await message.download_media(file=media_bytes)  # Await this call
    media_bytes.seek(0)

    media_file = media_bytes
    filename = 'file'

    if message.photo:
        is_photo = True
        media_file.name = 'image.jpg'
        media_type = 'photo'
    elif message.video:
        is_photo = False
        filename = 'video.mp4'
        media_file.name = filename
        media_type = 'video'
    else:
        is_photo = False
        if message.document:
            for attr in message.document.attributes:
                if isinstance(attr, types.DocumentAttributeFilename):
                    filename = attr.file_name
                    break
            else:
                mime_type = message.document.mime_type or ''
                extension = mimetypes.guess_extension(mime_type) or ''
                filename = f'file{extension}'
        media_file.name = filename
        media_type = 'document'

    return {
        'file': media_file,
        'is_photo': is_photo,
        'filename': filename,
        'media_type': media_type
    }

