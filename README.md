# Telegram Summary Bot

This Telegram bot is designed to store messages from chats and provide AI-powered summaries on demand. It uses the Anthropic API for generating summaries and can handle various time-based summary requests.

## Features

- Store messages from Telegram chats in a SQLite database
- Generate AI-powered summaries of chat discussions
- Flexible summary requests (by minutes, hours, or days)
- Clean up old messages from the database
- Ask general questions to the AI
- Split bills from receipt photos
- Basic calculator functionality
- Admin broadcast messages
- Question answering based on chat history
- Chat-specific context for better AI responses

## Prerequisites

- Python 3.7+
- A Telegram Bot Token
- An Anthropic API Key
- Docker and Docker Compose (for Docker deployment)
- ngrok

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/sdaveas/telegram-summary-bot
   cd telegram-summary-bot
   ```

2. Install the required dependencies:
   using pipenv
   ```
   pipenv install
   ```

   plain python
   ```
   pip install -r requirements.txt
   ```

3. Create an `.env` file in the project root and add your API keys:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   DATABASE_PATH=./database/messages.db
   ADMIN_USER_ID=your_telegram_user_id_here

   WEBHOOK_HOST=<global host listening to WEBHOOK_PORT> # set by 'ngrok http WEBHOOK_PORT', or whatever cloud service
   WEBHOOK_PORT=<your port>                             # 8443 by default
   ```

## Usage

### Running Locally

To start the bot, run:

```
python src/app.py
```

### Running with Docker Compose

1. Ensure you have Docker and Docker Compose installed on your system.
2. Create an `.env` file as described in the Installation section.
3. Run the following command to start the bot:
   ```
   docker-compose up -d
   ngrok http 8443
   ```
4. To stop the bot:
   ```
   docker-compose down
   ```

### Available Commands

- `/help`: Display usage information
- `/summary <M>m<H>h<D>d`: Generate a summary of recent messages
  - Examples:
    - `/summary 10m` (last 10 minutes)
    - `/summary 2h30m` (last 2 hours and 30 minutes)
    - `/summary 1d6h30m` (last 1 day, 6 hours, and 30 minutes)
- `/question <time_range> <question>`: Ask a question about recent chat history
  - Example: `/question 1h What was the main topic discussed?`
- `/ask <question>`: Ask a general question to the AI
- `/cal <expression>`: Perform basic mathematical calculations
  - Example: `/cal 2+2`
- `/clean`: Delete messages older than 1 day from the database
- `/credits`: Show repo url
- `/broadcast <message>`: (Admin only) Send a message to all chats
- `/set_context <context>`: Set the context for the current chat
  - Example: `/set_context This is a work chat about project X`
- `/get_context`: View the current context for the chat
- `/clear_context`: Remove the context for the current chat
- `split_bill` or `sb` (as photo caption): Split a bill from a receipt photo
  - Example: Send a photo with caption "split_bill Alice: 1 pizza, Bob: 2 beers"

## Context

The bot can maintain context for each chat, which is used to provide better responses to AI queries. The context is automatically included in all AI-powered responses (summaries, questions, and bill splitting). You can:

1. Set the context using `/set_context <context>`
2. View the current context using `/get_context`
3. Remove the context using `/clear_context`

The context helps the AI understand the chat's purpose and provide more relevant responses. For example, setting a context like "This is a work chat about project X" will help the AI provide more focused summaries and answers.

## Database

The bot uses a SQLite database to store messages and context. The database is automatically created when you first run the bot in the path specified by the environment variable `DATABASE_PATH` (e.g. `./database/messages.db`)

## Testing

The bot includes a test suite that can be run using:
```
python src/brain_test.py
```

## Security Notes

- Keep your `.env` file secret and never commit it to version control.
- Ensure you have the necessary rights and comply with privacy regulations when storing and processing chat messages.
- The `/broadcast` command is restricted to the user specified in `ADMIN_USER_ID`.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

All crates licensed under either of:
* Apache License, Version 2.0
* MIT license

at your option.

## Disclaimer

This bot stores message data. Ensure you have the right to store and process this data, and that you comply with all relevant data protection regulations.
