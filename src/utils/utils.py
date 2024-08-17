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
    return f"Usage: \n\
    /summary (defaults to {default})\n\
    /summary 1m\n\
    /summary 1h30m\n\
    /summary 1d\n"