# Telegram Content Moderation Bot

This project is a Telegram bot built using the [Telethon](https://github.com/LonamiWebs/Telethon) library to monitor and manage messages from specific channels or groups. The bot provides functionality for moderating content, using AI to improve text readability, and allowing human approval or disapproval of the messages. It integrates with the OpenAI API for text enhancement and includes a system for handling callback queries, editing messages, and processing new messages from designated channels.

## Features

- **Content Moderation**: Automatically fetches messages from specific channels/groups for review.
- **AI Integration**: Uses OpenAI's GPT models to improve message text readability upon request.
- **Approval System**: Human moderators can approve, disapprove, or edit messages before they are posted to the target channel.
- **Callback Query Handling**: Manages various actions such as approval, disapproval, and message editing using inline buttons.
- **Message Editing**: Allows admins to edit pending messages and resubmit them for approval.
- **Media Support**: Handles different types of media including images, videos, and documents.
- **Timeouts**: Pending approval requests are automatically deleted after a set timeout.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/telegram-moderation-bot.git
   cd telegram-moderation-bot

2. **Install the dependencies:**


Use pip to install the required libraries from requirements.txt:
```bash
pip install -r requirements.txt
