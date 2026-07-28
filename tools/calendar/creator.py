from langchain_core.tools import tool
from services.local_calendar_service import calendar_service

@tool
def create_event_tool(
    title: str,
    date: str,
    start_time: str,
    end_time: str,
    attendees: str,
    description: str = "",
) -> str:
    """
    Create a new calendar event. THIS IS A MUTATING ACTION.
    Only call this tool AFTER the user has approved the proposed meeting details.

    Args:
        title: Event title (e.g. "Sync with Rahul").
        date: Date in YYYY-MM-DD format.
        start_time: Start time in HH:MM 24-hour format.
        end_time: End time in HH:MM 24-hour format.
        attendees: Comma-separated attendee email addresses.
        description: Optional event description.
    """
    attendee_list = [a.strip() for a in attendees.split(",") if a.strip()]
    event = calendar_service.create_event(
        title=title,
        date_str=date,
        start_time=start_time,
        end_time=end_time,
        attendees=attendee_list,
        description=description,
    )
    attendee_str = ", ".join(event["attendees"])
    gcal_sync = event.get("gcal_link", "")
    
    return (
        f"Calendar event created successfully.\n"
        f"  Event ID: {event['id']}\n"
        f"  Title: {event['title']}\n"
        f"  Date: {event['date']}  |  {event['start_time']} - {event['end_time']}\n"
        f"  Attendees: {attendee_str}\n"
        f"  Sync to Google Calendar: {gcal_sync}"
    )
