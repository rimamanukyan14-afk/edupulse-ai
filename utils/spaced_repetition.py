from datetime import datetime, timedelta

DIFFICULTY_LABELS = {
    "hard": "Դժվար",
    "medium": "Միջին",
    "easy": "Հեշտ",
}


def next_review(card: dict, rating: str) -> dict:
    """
    Հաշվում է քարտի հաջորդ ցուցադրման ժամանակը՝ SM-2-ի պարզեցված տարբերակով։
    rating: 'hard' | 'medium' | 'easy'
    """
    now = datetime.now()
    interval = card.get("interval_minutes", 0)
    ease = card.get("ease", 2.5)

    if rating == "hard":
        # Դժվար քարտը ցուցադրվում է ամեն 2 րոպե
        interval = 2
        ease = max(1.3, ease - 0.2)
    elif rating == "medium":
        interval = max(10, int(interval * 1.2)) if interval else 10
    else:  # easy
        base = interval if interval else 1440
        interval = int(base * ease * 1.5)
        ease = min(3.0, ease + 0.1)

    card["interval_minutes"] = interval
    card["ease"] = round(ease, 2)
    card["due_at"] = now + timedelta(minutes=interval)
    card["last_rating"] = rating
    return card


def is_due(card: dict) -> bool:
    due = card.get("due_at")
    return due is None or datetime.now() >= due
