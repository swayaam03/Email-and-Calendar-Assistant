from langchain_core.tools import tool
from services.local_calendar_service import calendar_service


@tool
def get_schedule_tool(date: str = "") -> str:
    """
    Retrieve calendar events for a specific date or all upcoming events.

    Args:
        date: Date in YYYY-MM-DD format. Leave empty for all upcoming events.
    """
    date_str = date if date else None
    events = calendar_service.get_events(date_str)

    if not events:
        label = f"on {date}" if date else "upcoming"
        return f"No {label} events found."

    lines = []
    for i, event in enumerate(events, 1):
        attendee_str = ", ".join(event["attendees"])
        lines.append(
            f"[{i}] {event['title']}\n"
            f"    Date: {event['date']}  |  {event['start_time']} - {event['end_time']}\n"
            f"    Attendees: {attendee_str}\n"
            f"    Description: {event['description']}"
        )
    return "\n\n".join(lines)
