# handlers/__init__.py

# Import handlers to ensure they are registered
from .new_message_handler import new_message_listener
from .callback_query_handler import callback_query_handler
from .edit_message_handler import edit_message_handler

