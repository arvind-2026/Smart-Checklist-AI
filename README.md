# Smart Checklist AI

## A Weather-Aware Visual Readiness Assistant

Smart Checklist AI is a Python application that helps users check whether they
have essential items ready before starting their daily routine.

Users select an Office, College, or Travel routine. Every checklist item maps to
a class supported by the bundled YOLO26 model: laptop, book, suitcase, cell
phone, bottle, and umbrella. The application automatically retrieves the
weather forecast for the next eight hours using the user's approximate location.
If automatic location fails, it uses New Delhi as the fallback city. If live
weather is unavailable, it safely switches to an extreme offline profile for
New Delhi.

The application adds an umbrella to the selected checklist when rain is
expected.

After the user starts a scan, the webcam analyzes live video for thirty seconds
using YOLO object detection. Only detections meeting the configured confidence
threshold are accepted. If the webcam or detection model fails, the application
uses a prepared fallback image.

The final interface displays:

- Detected checklist items
- Missing items
- Compliance percentage
- Weather-based recommendations
- Compliance history
- A compliance-over-time chart

The project uses Python 3.11, Streamlit, Ultralytics YOLO, WeatherAPI, Pandas,
and Matplotlib. Important settings—including scan duration, confidence
threshold, forecast period, fallback city, and sample-image path—are maintained
in `config.py`.

Smart Checklist AI detects only whether supported objects are visually present.
It cannot confirm that water was drunk or protective equipment was worn.

## Challenges Faced

### Reliable object detection

Webcam availability, lighting, camera angle, object overlap, and low-confidence
predictions can affect detection. The general YOLO model also recognizes only
specific object classes.

### Automatic location and weather failures

Approximate IP location can be inaccurate or unavailable. Weather requests can
also fail because of an invalid API key, network problems, request limits, or
an incomplete API response.

### Converting forecasts into useful checklist rules

Raw hourly forecasts contain many values. The application needs one reliable
weather summary that can decide whether to add an umbrella to the checklist.

### Protecting configuration and generated data

The WeatherAPI key must remain private, while compliance-history files are
generated during normal use and should not be treated as source code.

## How the Challenges Were Solved

- The webcam scans automatically for a fixed duration and accepts detections
  only above the confidence threshold defined in `config.py`.
- A prepared checklist image is used if the webcam or detection model cannot
  start.
- Weather lookup follows a clear fallback chain: automatic approximate
  location, New Delhi, and finally an Extreme offline New Delhi profile.
- The application examines the configured number of upcoming forecast hours
  and uses the highest rain probability for checklist decisions.
- Runtime values such as scan duration, confidence threshold, forecast window,
  request timeout, fallback city, and fallback image path are centralized in
  `config.py` instead of being hard-coded throughout the project.
- The interface uses one routine selector and one scan button.
- The API key is stored in an ignored `.env` file, and generated CSV history is
  excluded through `.gitignore`.

## Future Upgrades

- Train a custom YOLO model if unsupported checklist items are added later.
- Combine detections across multiple frames using confidence voting and object
  tracking for more stable results.
- Add optional notifications when important weather-dependent items are
  missing.
- Add a mask when AQI is high, sunscreen when the UV index is high, and
  temperature-based suggestions for extreme heat or cold. Reliable visual
  confirmation of unsupported items would require custom YOLO training.
- Add live traffic and public-transit routing that compares car and Metro travel
  times, then recommends the better option with a clear reason. This would use
  precise origin and destination data, saved destinations, and a routing API;
  unavailable traffic data would produce a warning instead of a fabricated
  recommendation.
- Store history in a database with user accounts and multiple-device support.

## macOS setup

Python 3.11 must be installed before setup.

1. Open Terminal and enter the project directory.
2. Make the scripts executable if needed:

   ```text
   chmod +x setup_macos.sh run_macos.sh
   ```

3. Create the virtual environment and install dependencies:

   ```text
   ./setup_macos.sh
   ```

4. Start the application:

   ```text
   ./run_macos.sh
   ```

## Windows setup

Install Python 3.11 with the Python Launcher before setup.

1. Open Command Prompt and enter the project directory.
2. Create a Windows-specific virtual environment and install dependencies:

   ```text
   setup_windows.bat
   ```

3. Start the application:

   ```text
   run_windows.bat
   ```

Never copy `.venv` between macOS and Windows. Run the appropriate setup script
on each computer.

## Optional live weather

Offline weather works without configuration. To enable live weather:

1. Obtain a WeatherAPI key.
2. Copy `.env.example` to a new file named `.env`.
3. Replace the placeholder with your key:

   ```text
   WEATHER_API_KEY=your_real_key
   ```

The `.env` file is ignored by Git. If the key, internet or API is unavailable,
the program returns to offline weather mode.

Automatic location is approximate IP-based geolocation. If it fails, the app
tries New Delhi. If that live request also fails, it uses an Extreme offline
weather profile and continues to display New Delhi as the location.
The checklist uses the highest rain chance across the next eight hourly entries.

## Application workflow

The run scripts open a Streamlit interface in your browser. The workflow is:

1. Select Office, College, or Travel.
2. Hold checklist items where the webcam can see them.
3. Select **Start 30-second scan**.

Weather is selected automatically. The webcam scans live video for thirty seconds,
keeps unique detections at 60% confidence or higher, closes automatically and
saves one final result. If the webcam or model cannot start, the app checks
`test_media/checklist_items.png` instead.
The single compliance-over-time chart appears beneath the result.

History is saved at `data/compliance_history.csv`. Exactly one row is appended
after each completed routine check.

## Sample-image fallback

The application automatically uses `test_media/checklist_items.png` only when webcam
detection cannot start.

## Main project files

- `streamlit_app.py`: main graphical interface
- `config.py`: routine modes, thresholds, fallbacks and messages
- `weather_service.py`: automatic live weather and fallbacks
- `detector.py`: timed webcam and sample-image detection
- `compliance.py`: detection state and score calculations
- `alerts.py`: on-screen alert messages
- `history.py`: CSV and Pandas storage
- `analytics.py`: compliance-over-time Matplotlib chart
- `models/yolo26s.pt`: latest-generation Small detection model

## Common problems

- Python 3.11 not found: install it and rerun the platform setup script.
- Camera unavailable: continue without a photo; the sample image is automatic.
- Live weather unavailable: check `.env` and internet access. New Delhi live
  and Extreme offline New Delhi fallbacks are automatic.
- Slow detection: CPU inference is intentionally the default.
