"""Functions for building a context-aware checklist."""

from config import ENVIRONMENT_THRESHOLDS


def add_environmental_items(base_checklist, environment_data):
    """Return a checklist updated for the supplied environmental conditions."""
    checklist = base_checklist.copy()

    if environment_data["rain_probability"] >= ENVIRONMENT_THRESHOLDS["rain_probability"]:
        checklist.append("umbrella")

    return checklist
