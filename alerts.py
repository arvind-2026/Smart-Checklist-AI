"""Printed alert messages for missing checklist items."""

from config import ENVIRONMENTAL_ALERT_MESSAGES


def format_item_name(item):
    """Convert an internal item name into a display label."""
    return item.replace("_", " ").title()


def create_alert_messages(missing_items):
    """Create alert messages for missing items."""
    messages = []

    for item in missing_items:
        default_message = f"Missing required item: {format_item_name(item)}."
        messages.append(ENVIRONMENTAL_ALERT_MESSAGES.get(item, default_message))

    return messages
