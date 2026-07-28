from langchain_core.tools import tool


# Simple in-memory contact directory.
# In production, this would query a contacts database or LDAP.
_CONTACTS = {
    "rahul": {"name": "Rahul Sharma", "email": "rahul.sharma@techcorp.com"},
    "sarah": {"name": "Sarah Jenkins", "email": "sarah.jenkins@designstudio.io"},
    "john": {"name": "John Doe", "email": "john.doe@company.org"},
}


@tool
def contact_lookup_tool(name: str) -> str:
    """
    Look up a contact's full name and email address by first name or keyword.
    Useful for resolving "Reply to John" or "Schedule with Rahul".

    Args:
        name: The person's name or partial name to search for.
    """
    query = name.lower().strip()
    matches = []
    for key, contact in _CONTACTS.items():
        if query in key or query in contact["name"].lower():
            matches.append(contact)

    if not matches:
        return f"No contact found for '{name}'."

    lines = []
    for c in matches:
        lines.append(f"  Name: {c['name']}\n  Email: {c['email']}")
    return "\n".join(lines)
