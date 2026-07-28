# Tools package - Central tool registry
from .email import read_emails_tool, search_emails_tool, create_draft_tool, send_email_tool
from .calendar import get_schedule_tool, check_availability_tool, create_event_tool
from .utils import get_current_datetime_tool, resolve_relative_date_tool, contact_lookup_tool

# All tools available to the LangGraph agent, grouped for easy binding
ALL_TOOLS = [
    # Email tools
    read_emails_tool,
    search_emails_tool,
    create_draft_tool,
    send_email_tool,
    # Calendar tools
    get_schedule_tool,
    check_availability_tool,
    create_event_tool,
    # Utility tools
    get_current_datetime_tool,
    resolve_relative_date_tool,
    contact_lookup_tool,
]

# Tools that MUST require human approval before execution
MUTATING_TOOLS = {"send_email_tool", "create_event_tool"}

__all__ = [
    "ALL_TOOLS",
    "MUTATING_TOOLS",
    "read_emails_tool",
    "search_emails_tool",
    "create_draft_tool",
    "send_email_tool",
    "get_schedule_tool",
    "check_availability_tool",
    "create_event_tool",
    "get_current_datetime_tool",
    "resolve_relative_date_tool",
    "contact_lookup_tool",
]
