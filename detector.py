"""Focused YOLO detection for a timed webcam scan and image fallback."""

import importlib
import time
from pathlib import Path

from config import DETECTION_CONFIDENCE_THRESHOLD, WEBCAM_SCAN_DURATION_SECONDS


PROJECT_DIRECTORY = Path(__file__).resolve().parent
DEFAULT_MODEL_PATH = PROJECT_DIRECTORY / "models" / "yolo26s.pt"

YOLO_CLASS_MAP = {
    "book": "book",
    "bottle": "water_bottle",
    "cell phone": "phone",
    "laptop": "laptop",
    "suitcase": "suitcase",
    "umbrella": "umbrella",
}


def map_yolo_classes(class_names):
    """Map supported YOLO classes to unique checklist item names."""
    checklist_items = []
    for class_name in class_names:
        checklist_item = YOLO_CLASS_MAP.get(class_name.lower())
        if checklist_item and checklist_item not in checklist_items:
            checklist_items.append(checklist_item)
    return checklist_items


def extract_detected_class_names(results):
    """Extract unique class names from Ultralytics results."""
    class_names = []
    for result in results:
        if result.boxes is None:
            continue
        for class_id in result.boxes.cls.tolist():
            class_name = result.names[int(class_id)]
            if class_name not in class_names:
                class_names.append(class_name)
    return class_names


def load_yolo_model(model_path=DEFAULT_MODEL_PATH):
    """Load the local YOLO model, returning None on failure."""
    model_path = Path(model_path)
    if not model_path.is_file():
        print(f"YOLO model file was not found: {model_path}")
        return None

    try:
        ultralytics = importlib.import_module("ultralytics")
        return ultralytics.YOLO(str(model_path))
    except ImportError:
        print("Ultralytics is not installed. Install requirements.txt first.")
    except (OSError, RuntimeError, ValueError) as error:
        print(f"YOLO model could not be loaded: {error}")
    return None


def detect_objects_in_image(image_path, model_path=DEFAULT_MODEL_PATH):
    """Detect class names in one local fallback image."""
    image_path = Path(image_path)
    if not image_path.is_file():
        print(f"Image file was not found: {image_path}")
        return []

    model = load_yolo_model(model_path)
    if model is None:
        return []

    try:
        results = model.predict(
            source=str(image_path),
            device="cpu",
            conf=DETECTION_CONFIDENCE_THRESHOLD,
            verbose=False,
        )
        return extract_detected_class_names(results)
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Image detection failed: {error}")
        return []


def open_camera(cv2):
    """Open the default webcam, returning None when unavailable."""
    video_capture = cv2.VideoCapture(0)
    if video_capture.isOpened():
        return video_capture
    video_capture.release()
    print("The default webcam is unavailable.")
    return None


def detect_objects_from_webcam_timed(
    duration_seconds=WEBCAM_SCAN_DURATION_SECONDS,
    confidence_threshold=DETECTION_CONFIDENCE_THRESHOLD,
    model_path=DEFAULT_MODEL_PATH,
    on_frame=None,
):
    """Scan webcam frames for a fixed time and return strong detections."""
    try:
        cv2 = importlib.import_module("cv2")
    except ImportError:
        print("OpenCV is not installed. Install requirements.txt first.")
        return None

    model = load_yolo_model(model_path)
    if model is None:
        return None

    video_capture = open_camera(cv2)
    if video_capture is None:
        return None

    detected_class_names = []
    started_at = time.monotonic()
    try:
        while time.monotonic() - started_at < duration_seconds:
            frame_was_read, frame = video_capture.read()
            if not frame_was_read:
                print("The camera stopped providing frames.")
                return None

            results = model.predict(
                source=frame,
                device="cpu",
                conf=confidence_threshold,
                verbose=False,
            )
            for class_name in extract_detected_class_names(results):
                if class_name not in detected_class_names:
                    detected_class_names.append(class_name)
            if on_frame is not None and results:
                on_frame(results[0].plot())
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Timed webcam detection failed: {error}")
        return None
    finally:
        video_capture.release()

    return detected_class_names
