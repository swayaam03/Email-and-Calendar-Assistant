from datetime import datetime, timedelta
from langchain_core.tools import tool


# Map day names to Python weekday integers (Monday=0 ... Sunday=6)
_DAY_MAP = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6,
}

# Map time-of-day keywords to (hour, minute) defaults
_TIME_OF_DAY = {
    "morning": (9, 0),
    "noon": (12, 0),
    "afternoon": (14, 0),
    "evening": (17, 0),
}


@tool
def get_current_datetime_tool() -> str:
    """
    Get the current date and time. Useful for the LLM to know "today",
    calculate relative references, and resolve scheduling queries.
    Returns date in YYYY-MM-DD and day-of-week.
    """
    now = datetime.now()
    return (
        f"Current Date: {now.strftime('%Y-%m-%d')} ({now.strftime('%A')})\n"
        f"Current Time: {now.strftime('%H:%M')}"
    )


@tool
def resolve_relative_date_tool(expression: str) -> str:
    """
    Resolve a natural-language relative date expression into a concrete
    YYYY-MM-DD date and suggested time slot.

    Supported expressions (case-insensitive):
      - "today", "tomorrow"
      - "next monday", "next tuesday", ..., "next sunday"
      - Append time-of-day: "next tuesday afternoon", "tomorrow morning"

    Args:
        expression: A relative date phrase like "next tuesday afternoon".
    """
    now = datetime.now()
    parts = expression.lower().strip().split()

    resolved_date = now
    time_label = ""

    # ---- Resolve the date component ----
    if "today" in parts:
        resolved_date = now
    elif "tomorrow" in parts:
        resolved_date = now + timedelta(days=1)
    else:
        # Look for a day name (optionally preceded by "next" or "this")
        for part in parts:
            if part in _DAY_MAP:
                target_weekday = _DAY_MAP[part]
                days_ahead = (target_weekday - now.weekday() + 7) % 7
                if days_ahead == 0:
                    days_ahead = 7  # "next X" means the coming one, not today
                resolved_date = now + timedelta(days=days_ahead)
                break

    # ---- Resolve the time-of-day component ----
    for part in parts:
        if part in _TIME_OF_DAY:
            hour, minute = _TIME_OF_DAY[part]
            time_label = f"Suggested time: {hour:02d}:{minute:02d}"
            break

    result = f"Resolved date: {resolved_date.strftime('%Y-%m-%d')} ({resolved_date.strftime('%A')})"
    if time_label:
        result += f"\n{time_label}"
    return result
