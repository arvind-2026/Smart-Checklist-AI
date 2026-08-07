"""Simple Streamlit interface for Smart Checklist AI."""

import matplotlib.pyplot as plt
import streamlit as st

from alerts import create_alert_messages, format_item_name
from analytics import plot_compliance_over_time
from checklist import add_environmental_items
from compliance import (
    calculate_compliance_percentage,
    create_compliance_state,
    find_missing_items,
    update_detected_items,
)
from config import (
    DETECTION_CONFIDENCE_THRESHOLD,
    PROJECT_NAME,
    PROJECT_SUBTITLE,
    ROUTINE_MODES,
    SAMPLE_IMAGE_RELATIVE_PATHS,
    WEATHER_FORECAST_HOURS,
    WEBCAM_SCAN_DURATION_SECONDS,
)
from detector import (
    PROJECT_DIRECTORY,
    detect_objects_from_webcam_timed,
    detect_objects_in_image,
    map_yolo_classes,
)
from history import DEFAULT_HISTORY_FILE, create_session_record, load_history, save_session_record
from weather_service import get_automatic_weather


SAMPLE_IMAGE_PATHS = tuple(
    PROJECT_DIRECTORY / relative_path for relative_path in SAMPLE_IMAGE_RELATIVE_PATHS
)


def detect_webcam_or_sample():
    """Run a timed webcam scan, using the sample only on failure."""
    live_frame = st.empty()
    progress_text = st.empty()
    confidence_percent = round(DETECTION_CONFIDENCE_THRESHOLD * 100)
    progress_text.info(
        f"Scanning webcam for {WEBCAM_SCAN_DURATION_SECONDS} seconds at "
        f"{confidence_percent}% confidence..."
    )

    def show_frame(frame):
        live_frame.image(frame, channels="BGR", width="stretch")

    class_names = detect_objects_from_webcam_timed(
        duration_seconds=WEBCAM_SCAN_DURATION_SECONDS,
        confidence_threshold=DETECTION_CONFIDENCE_THRESHOLD,
        on_frame=show_frame,
    )
    progress_text.empty()

    if class_names is None:
        live_frame.empty()
        st.warning("Webcam detection could not start. Using the sample image.")
        detected_classes = set()
        for sample_image_path in SAMPLE_IMAGE_PATHS:
            detected_classes.update(detect_objects_in_image(sample_image_path))
        detected_items = map_yolo_classes(detected_classes)
        return "Sample image fallback", detected_items

    return (
        f"{WEBCAM_SCAN_DURATION_SECONDS}-second webcam scan",
        map_yolo_classes(class_names),
    )


def show_result(mode):
    """Run one automatic weather and visual checklist check."""
    with st.spinner(f"Checking the next {WEATHER_FORECAST_HOURS} hours of weather..."):
        weather_source, location, weather = get_automatic_weather()
    with st.spinner("Detecting checklist items..."):
        detection_source, detected_items = detect_webcam_or_sample()

    checklist = add_environmental_items(ROUTINE_MODES[mode], weather)
    state = create_compliance_state(checklist)
    update_detected_items(state, detected_items)
    missing_items = find_missing_items(state)
    score = calculate_compliance_percentage(state)
    alerts = create_alert_messages(missing_items)

    st.subheader("Your routine result")
    score_column, ready_column, missing_column = st.columns(3)
    score_column.metric("Compliance", f"{score:.0f}%")
    ready_column.metric("Ready", sum(state.values()))
    missing_column.metric("Missing", len(missing_items))
    st.progress(score / 100)

    left_column, right_column = st.columns(2)
    with left_column:
        st.markdown("#### Checklist")
        for item, was_detected in state.items():
            icon = "✅" if was_detected else "❌"
            st.write(f"{icon} {format_item_name(item)}")
        st.caption(f"Detection: {detection_source}")
    with right_column:
        st.markdown(f"#### Next {WEATHER_FORECAST_HOURS} hours")
        st.write(f"**Location:** {location}")
        st.write(f"**Source:** {weather_source}")
        st.write(f"🌧️ Highest rain chance: {weather['rain_probability']}%")

    if alerts:
        for message in alerts:
            st.warning(message)
    else:
        st.success("All required items are visually present.")

    save_session_record(create_session_record(mode, state), DEFAULT_HISTORY_FILE)
    st.caption("Session saved to your compliance history.")


def show_history_chart():
    """Display the single compliance progress chart."""
    history = load_history(DEFAULT_HISTORY_FILE)
    st.subheader("Compliance over time")
    if history.empty:
        st.info("Complete your first routine check to see progress here.")
        return

    figure = plot_compliance_over_time(history)
    st.pyplot(figure, width="stretch")
    plt.close(figure)


def main():
    """Render the simplified interface."""
    st.set_page_config(page_title=PROJECT_NAME, page_icon="✅", layout="wide")
    st.title(f"✅ {PROJECT_NAME}")
    st.caption(PROJECT_SUBTITLE)
    st.info(
        f"Choose your routine and start one automatic "
        f"{WEBCAM_SCAN_DURATION_SECONDS}-second webcam scan. "
        "Weather and fallbacks are automatic. "
        "Detection confirms only visual presence, not whether an item was used."
    )

    mode = st.selectbox("Routine mode", list(ROUTINE_MODES), format_func=format_item_name)
    st.write("Hold your checklist items where the webcam can see them, then start the scan.")
    if st.button(
        f"Start {WEBCAM_SCAN_DURATION_SECONDS}-second scan",
        type="primary",
        width="stretch",
    ):
        show_result(mode)

    st.divider()
    show_history_chart()


if __name__ == "__main__":
    main()
