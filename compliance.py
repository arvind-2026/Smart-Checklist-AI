"""Functions for tracking checklist compliance during one session."""


def create_compliance_state(checklist):
    """Create a state dictionary with every checklist item set to False."""
    return {item: False for item in checklist}


def update_detected_items(compliance_state, detected_items):
    """Mark checklist items as detected and ignore unrelated objects."""
    for item in detected_items:
        if item in compliance_state:
            compliance_state[item] = True


def find_missing_items(compliance_state):
    """Return checklist items that have not been detected."""
    return [
        item
        for item, was_detected in compliance_state.items()
        if not was_detected
    ]


def calculate_compliance_percentage(compliance_state):
    """Return the detected percentage, or zero for an empty checklist."""
    total_items = len(compliance_state)

    if total_items == 0:
        return 0.0

    detected_items = sum(compliance_state.values())
    percentage = detected_items / total_items * 100
    return round(percentage, 2)
