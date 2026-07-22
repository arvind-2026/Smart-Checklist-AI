"""Create, save and load routine-check history records."""

from datetime import datetime
from pathlib import Path

import pandas as pd

from compliance import calculate_compliance_percentage, find_missing_items


HISTORY_COLUMNS = [
    "timestamp",
    "mode",
    "total_items",
    "detected_items",
    "missing_items",
    "compliance_percentage",
    "missing_item_names",
]

DEFAULT_HISTORY_FILE = Path(__file__).resolve().parent / "data" / "compliance_history.csv"


def create_session_record(mode, compliance_state, timestamp=None):
    """Create one summary dictionary for a completed routine check."""
    if timestamp is None:
        timestamp = datetime.now()

    missing_items = find_missing_items(compliance_state)
    detected_count = sum(compliance_state.values())

    return {
        "timestamp": timestamp.isoformat(timespec="seconds"),
        "mode": mode,
        "total_items": len(compliance_state),
        "detected_items": detected_count,
        "missing_items": len(missing_items),
        "compliance_percentage": calculate_compliance_percentage(compliance_state),
        "missing_item_names": ";".join(missing_items),
    }


def save_session_record(record, csv_path=DEFAULT_HISTORY_FILE):
    """Append one session summary to a CSV file."""
    csv_path = Path(csv_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    file_already_exists = csv_path.exists() and csv_path.stat().st_size > 0

    record_frame = pd.DataFrame([record], columns=HISTORY_COLUMNS)
    record_frame.to_csv(
        csv_path,
        mode="a",
        header=not file_already_exists,
        index=False,
    )


def load_history(csv_path=DEFAULT_HISTORY_FILE):
    """Load history, or return an empty DataFrame when no CSV exists."""
    csv_path = Path(csv_path)

    if not csv_path.exists() or csv_path.stat().st_size == 0:
        return pd.DataFrame(columns=HISTORY_COLUMNS)

    return pd.read_csv(csv_path)
