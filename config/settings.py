"""
Configuration Settings
Centralized configuration for the Navigation Assistant
"""
import os
from pathlib import Path

# ============================================================================
# Application Settings
# ============================================================================
APP_NAME = "Navigation Assistant"
APP_VERSION = "1.0.0"
APP_COPYRIGHT = "© 2025 - Système d'aide à la navigation"

# ============================================================================
# Model Settings
# ============================================================================
DEFAULT_MODEL = "yolov8n"
AVAILABLE_MODELS = [
    "yolov8n",
    "yolo11n",
    "yolo8_personnalisé",
    "yolo11_personnalisé"
]

MODEL_FILES = {
    "yolov8n": "yolov8n.pt",
    "yolo11n": "yolo11n.pt",
    "yolo8_personnalisé": "best8.pt",
    "yolo11_personnalisé": "best11.pt"
}

# Detection settings
DEFAULT_CONF_THRESHOLD = 0.25
MIN_CONF_THRESHOLD = 0.01
MAX_CONF_THRESHOLD = 1.0

# Tracking settings
TRACKER_CONFIG = "bytetrack.yaml"

# ============================================================================
# Video Settings
# ============================================================================
DEFAULT_CAMERA_INDEX = 0  # Internal webcam
EXTERNAL_CAMERA_INDEX = 1  # External camera

# Camera IDs for different sources
SOURCE_TYPES = {
    "webcam": 0,
    "external_camera": 1,
    "file": None
}

# Video recording
RECORDING_CODEC = 'mp4v'
DEFAULT_FPS = 20.0
RECORDING_FOLDER = os.path.join(os.path.expanduser("~"), "Navigation_Assistant_Recordings")

# Frame processing
DEFAULT_FRAME_WIDTH = 640
DEFAULT_FRAME_HEIGHT = 480

# ============================================================================
# Zone Detection Settings
# ============================================================================
ZONE_DIVISIONS = 3  # Left, Center, Right
ZONE_NAMES = ["gauche", "milieu", "droite"]

# Zone colors (BGR format for OpenCV)
ZONE_COLORS = {
    "gauche": (70, 70, 200),   # Red
    "milieu": (70, 200, 70),   # Green
    "droite": (200, 70, 70)    # Blue
}

ZONE_ALPHA = 0.3  # Transparency for zone overlays

# ============================================================================
# Audio/TTS Settings
# ============================================================================
TTS_RATE = 150  # Words per minute
TTS_VOLUME = 0.9  # Volume level (0.0 - 1.0)
SPOKEN_TIMEOUT = 5.0  # Seconds before repeating same object announcement
ENABLE_VOICE_BY_DEFAULT = True
ENABLE_ZONE_ANNOUNCEMENT_BY_DEFAULT = True

# ============================================================================
# GUI Settings
# ============================================================================
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800
WINDOW_TITLE = f"{APP_NAME} - Interface de Détection"

# Update intervals (milliseconds)
UI_UPDATE_INTERVAL = 100
FPS_UPDATE_INTERVAL = 100

# Splitter sizes
LEFT_PANEL_WIDTH = 700
RIGHT_PANEL_WIDTH = 500

# Video display
VIDEO_MIN_WIDTH = 640
VIDEO_MIN_HEIGHT = 480

# Detection text
MAX_DETECTIONS_DISPLAY_HEIGHT = 150

# ============================================================================
# Styling
# ============================================================================
# Color scheme
PRIMARY_COLOR = "#3498db"
SECONDARY_COLOR = "#2980b9"
ACCENT_COLOR = "#1c6ea4"
DANGER_COLOR = "#e74c3c"
DANGER_HOVER = "#c0392b"
SUCCESS_COLOR = "#2ecc71"

BACKGROUND_DARK = "#353535"
BACKGROUND_DARKER = "#191919"
BACKGROUND_LIGHT = "#2a2a2a"
TEXT_COLOR = "#ffffff"
BORDER_COLOR = "#3a3a3a"

# Font settings
TITLE_FONT_SIZE = 18
TITLE_FONT_WEIGHT = "bold"
GROUP_FONT_SIZE = 14
NORMAL_FONT_SIZE = 12

# ============================================================================
# File Paths
# ============================================================================
PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / "models"
ASSETS_DIR = PROJECT_ROOT / "assets"
SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"
DOCS_DIR = PROJECT_ROOT / "docs"

# Ensure directories exist
MODELS_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)
os.makedirs(RECORDING_FOLDER, exist_ok=True)

# ============================================================================
# Logging
# ============================================================================
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ============================================================================
# Performance
# ============================================================================
MAX_QUEUE_SIZE = 10  # Maximum number of frames in processing queue
THREAD_WAIT_TIMEOUT = 1000  # Milliseconds to wait for thread termination

# ============================================================================
# Supported File Formats
# ============================================================================
VIDEO_FILE_EXTENSIONS = [
    "*.mp4",
    "*.avi",
    "*.mov",
    "*.mkv",
    "*.wmv",
    "*.flv"
]

VIDEO_FILE_FILTER = "Fichiers vidéo (*.mp4 *.avi *.mov *.mkv *.wmv *.flv)"

# ============================================================================
# Help Text
# ============================================================================
HELP_TEXT = """
<p style="color: {primary_color};"><b>Guide rapide:</b></p>
<ul>
    <li>Sélectionnez une source vidéo (webcam interne, caméra externe ou fichier)</li>
    <li>Ajustez le seuil de confiance selon vos besoins</li>
    <li>L'écran est divisé en 3 zones: gauche, milieu et droite</li>
    <li>Les objets sont signalés vocalement avec leur position</li>
    <li>Utilisez la case à cocher "Effet miroir" pour activer/désactiver l'effet miroir</li>
</ul>
""".format(primary_color=PRIMARY_COLOR)

# ============================================================================
# Debug Settings
# ============================================================================
DEBUG_MODE = False
VERBOSE_LOGGING = False
SHOW_FPS = True
SHOW_CONFIDENCE = True