"""
Event storage for Dategram.
Edit this file to add, remove, or update events.
Dates are in YYYY-MM-DD format (UTC).
"""

from datetime import date, timedelta

# Recurring and specific events
EVENTS = [
    {
        "name": "New Year's Day",
        "date": "2026-01-01",
        "time": "00:00 UTC",
        "description": "Start of the new year worldwide.",
        "emoji": "🎉",
    },
    {
        "name": "International Women's Day",
        "date": "2026-03-08",
        "time": "All day",
        "description": "Celebrating women's achievements globally.",
        "emoji": "🌸",
    },
    {
        "name": "Earth Day",
        "date": "2026-04-22",
        "time": "All day",
        "description": "Global environmental awareness event.",
        "emoji": "🌍",
    },
    {
        "name": "International Labor Day",
        "date": "2026-05-01",
        "time": "All day",
        "description": "Honoring workers worldwide.",
        "emoji": "🛠️",
    },
    {
        "name": "World Environment Day",
        "date": "2026-06-05",
        "time": "All day",
        "description": "UN initiative for environmental action.",
        "emoji": "🌱",
    },
    {
        "name": "International Peace Day",
        "date": "2026-09-21",
        "time": "All day",
        "description": "Global day of ceasefire and non-violence.",
        "emoji": "🕊️",
    },
    {
        "name": "Halloween",
        "date": "2026-10-31",
        "time": "Evening",
        "description": "Spooky celebration and traditions.",
        "emoji": "🎃",
    },
    {
        "name": "Christmas Day",
        "date": "2026-12-25",
        "time": "All day",
        "description": "Global holiday celebration.",
        "emoji": "🎄",
    },
    {
        "name": "New Year's Eve",
        "date": "2026-12-31",
        "time": "Evening",
        "description": "Countdown to the new year.",
        "emoji": "🎆",
    },
]


def get_upcoming_events(limit: int = 5):
    """Return events sorted by date (from today forward)."""
    today = date.today()
    upcoming = []
    for ev in EVENTS:
        try:
            ev_date = date.fromisoformat(ev["date"])
        except ValueError:
            continue
        if ev_date >= today:
            days_left = (ev_date - today).days
            upcoming.append({**ev, "date_obj": ev_date, "days_left": days_left})
    upcoming.sort(key=lambda x: x["date_obj"])
    return upcoming[:limit]


def get_events_on(day_offset: int = 0):
    """Get events happening today (0), tomorrow (1), etc."""
    target = date.today() + timedelta(days=day_offset)
    result = []
    for ev in EVENTS:
        try:
            ev_date = date.fromisoformat(ev["date"])
        except ValueError:
            continue
        if ev_date == target:
            days_left = (ev_date - date.today()).days
            result.append({**ev, "date_obj": ev_date, "days_left": days_left})
    return result


def get_next_event():
    """Get the very next upcoming event."""
    events = get_upcoming_events(limit=1)
    return events[0] if events else None
