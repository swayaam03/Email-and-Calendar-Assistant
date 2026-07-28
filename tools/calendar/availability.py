from langchain_core.tools import tool
from services.local_calendar_service import calendar_service


@tool
def check_availability_tool(date: str, duration_minutes: int = 30) -> str:
    """
    Find available time slots on a given date during working hours (09:00-17:00).
    Returns free slots that do not conflict with existing calendar events.

    Args:
        date: Date in YYYY-MM-DD format to check availability.
        duration_minutes: Desired meeting duration in minutes (default 30).
    """
    slots = calendar_service.find_available_slots(date, duration_minutes)

    if not slots:
        return f"No available {duration_minutes}-minute slots on {date}."

    lines = [f"Available {duration_minutes}-min slots on {date}:"]
    for i, slot in enumerate(slots, 1):
        lines.append(f"  [{i}] {slot['start_time']} - {slot['end_time']}")
    return "\n".join(lines)
