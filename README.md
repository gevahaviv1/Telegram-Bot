# Telegram Bot

This project is a **Telegram bot** built with Python using the Telethon library. It listens to multiple channels, processes messages, and sends them for approval. The bot also integrates with OpenAI for AI-powered message improvements.

## Features

- Listen to specified channels and groups for new messages.
- Approve, disapprove, or edit messages before sending them to the target channel.
- AI processing for improving message content.
- Admin interface for approving or rejecting messages via inline buttons.

## Requirements

Before running the bot, make sure you have the following installed:

- **Python 3.7+**
- **Telethon**: A Python library for interacting with Telegram's API.  
  Install via:  
  ```bash
  pip install telethon
