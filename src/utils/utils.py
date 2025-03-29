import datetime

def time_expression_to_seconds(expression) -> int:
    total_seconds = 0
    current_number = ''
    
    for char in expression:
        if char.isdigit():
            current_number += char
        else:
            if current_number:
                value = int(current_number)
                if char == 'm':
                    total_seconds += value * 60
                elif char == 'h':
                    total_seconds += value * 3600
                elif char == 'd':
                    total_seconds += value * 86400
                current_number = ''
    
    return total_seconds


def seconds_to_timestamp(seconds) -> int:
    delta = datetime.timedelta(seconds=seconds)
    return int((datetime.datetime.now() - delta).timestamp())


def one_day_ago() -> int:
    return int((datetime.datetime.now() - datetime.timedelta(days=1)).timestamp())


def help_message(default) -> str:
    return f"""Available Commands:
    /summary - Get a summary of the last {default}.
    /summary <time> - Get a summary for a specific time range. Examples:
        - /summary 1m (last 1 minute)
        - /summary 1h30m (last 1 hour and 30 minutes)
        - /summary 1d (last 1 day)
    /question <time> <question> - Ask a question based on the discussion in the specified time range. Examples:
        - /question 1h What was discussed about the project?
    /ask <question> - Ask the bot a general question. Example:
        - /ask What is the capital of France?
    /clean - Delete messages older than 1 day.
    /credits - View project credits.
    /help - Show this help message.
    """