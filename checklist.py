"""Functions for building a context-aware checklist."""

from config import ENVIRONMENT_THRESHOLDS


def add_environmental_items(base_checklist, environment_data):
    """Return a checklist updated for the supplied environmental conditions."""
    return base_checklist.copy() + get_environmental_items(environment_data)


def get_environmental_items(environment_data):
    """Return items required by the supplied environmental conditions."""
    environmental_items = []

    if environment_data["rain_probability"] >= ENVIRONMENT_THRESHOLDS["rain_probability"]:
        environmental_items.append("umbrella")

    return environmental_items
