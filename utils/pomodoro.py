import time


def format_seconds(total: int) -> str:
    minutes, seconds = divmod(max(total, 0), 60)
    return f"{minutes:02d}:{seconds:02d}"


def run_countdown(seconds: int, placeholder) -> None:
    """Ցուցադրում է հաշվարկը placeholder-ում (blocking)։"""
    for remaining in range(seconds, -1, -1):
        placeholder.metric("Մնացել է", format_seconds(remaining))
        if remaining > 0:
            time.sleep(1)
