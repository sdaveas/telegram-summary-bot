# Telegram Summary Bot

This Telegram bot is designed to store messages from chats and provide AI-powered summaries on demand. It uses the Anthropic API for generating summaries and can handle various time-based summary requests.

## Features

- Store messages from Telegram chats in a SQLite database
- Generate AI-powered summaries of chat discussions
- Flexible summary requests (by minutes, hours, or days)
- Clean up old messages from the database
- Ask general questions to the AI

## Prerequisites

- Python 3.7+
- A Telegram Bot Token
- An Anthropic API Key

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/sdaveas/telegram-summary-bot
   cd telegram-summary-bot
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root and add your API keys:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

## Usage

To start the bot, run:

```
python bot.py
```

### Available Commands

- `/help`: Display usage information
- `/summary [days] [hours] [minutes]`: Generate a summary of recent messages
  - Examples:
    - `/summary 10` (last 10 minutes)
    - `/summary 2 30` (last 2 hours and 30 minutes)
    - `/summary 1 6 30` (last 1 day, 6 hours, and 30 minutes)
- `/ask <question>`: Ask a general question to the AI
- `/clean`: Delete messages older than 1 day from the database

## Database

The bot uses a SQLite database (`messages.db`) to store messages. The database is automatically created when you first run the bot.

## Security Notes

- Keep your `.env` file secret and never commit it to version control.
- Ensure you have the necessary rights and comply with privacy regulations when storing and processing chat messages.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Specify your license here]

## Disclaimer

This bot stores message data. Ensure you have the right to store and process this data, and that you comply with all relevant data protection regulations.