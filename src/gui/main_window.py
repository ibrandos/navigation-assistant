"""
Main Window GUI
Main application window for Navigation Assistant
"""
import os
import time
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QPushButton, QComboBox, QSlider, QFileDialog,
                            QCheckBox, QTextEdit, QGroupBox, QGridLayout,
                            QSplitter, QFrame, QMessageBox, QSizePolicy)
from PyQt6.QtGui import QImage, QPixmap, QFont
from PyQt6.QtCore import Qt, QTimer
import cv2
import numpy as np

from src.core.detector import YOLODetector
from src.core.video_processor import VideoProcessorThread
from src.audio.tts_engine import TTSEngine, VoiceNotificationManager
from src.utils.video_recorder import VideoRecorder
from src.gui import styles
from config import settings


class NavigationAssistantGUI(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Set window properties
        self.setWindowTitle(settings.WINDOW_TITLE)
        self.setGeometry(100, 100, settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
        
        # Initialize modules
        self.init_modules()
        
        # Build UI
        self.init_ui()
        
        # Setup connections
        self.setup_connections()
        
        # Start processing
        self.start_processing()
        
    def init_modules(self):
        """Initialize all processing modules"""
        # Detection and tracking
        self.detector = YOLODetector(default_model=settings.DEFAULT_MODEL)
        
        # Video processor
        self.video_processor = VideoProcessorThread(self.detector, self)
        
        # Audio/TTS
        self.tts_engine = TTSEngine(self)
        self.voice_manager = VoiceNotificationManager(
            self.tts_engine, 
            cooldown=settings.SPOKEN_TIMEOUT
        )
        
        # Video recorder
        self.recorder = VideoRecorder(output_dir=settings.RECORDING_FOLDER)
        
        # State variables
        self.last_detections = []
        self.current_fps = 0.0
        
    def init_ui(self):
        """Build the user interface"""
        # Apply styling
        styles.apply_app_style()
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        self.create_title(main_layout)
        
        # Main content area (splitter with left and right panels)
        splitter = self.create_main_content()
        main_layout.addWidget(splitter)
        
        # Footer
        self.create_footer(main_layout)
        
        # UI update timer
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_ui_elements)
        self.update_timer.start(settings.UI_UPDATE_INTERVAL)
        
    def create_title(self, layout: QVBoxLayout):
        """Create title label"""
        title_label = QLabel(settings.APP_NAME)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", settings.TITLE_FONT_SIZE, QFont.Weight.Bold))
        title_label.setStyleSheet(styles.get_title_style())
        layout.addWidget(title_label)
        
    def create_main_content(self) -> QSplitter:
        """Create main content area with splitter"""
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel (video and detections)
        left_panel = self.create_left_panel()
        
        # Right panel (controls)
        right_panel = self.create_right_panel()
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([settings.LEFT_PANEL_WIDTH, settings.RIGHT_PANEL_WIDTH])
        
        return splitter
        
    def create_left_panel(self) -> QWidget:
        """Create left panel with video display and detection info"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Video display
        video_container = QFrame()
        video_container.setStyleSheet(styles.get_video_frame_style())
        video_layout = QVBoxLayout(video_container)
        
        self.video_label = QLabel()
        self.video_label.setMinimumSize(settings.VIDEO_MIN_WIDTH, settings.VIDEO_MIN_HEIGHT)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        video_layout.addWidget(self.video_label)
        
        layout.addWidget(video_container)
        
        # Detections display
        detections_group = QGroupBox("Objets Détectés")
        detections_layout = QVBoxLayout()
        
        self.detections_text = QTextEdit()
        self.detections_text.setReadOnly(True)
        self.detections_text.setMaximumHeight(settings.MAX_DETECTIONS_DISPLAY_HEIGHT)
        self.detections_text.setStyleSheet(styles.get_text_edit_style())
        detections_layout.addWidget(self.detections_text)
        
        detections_group.setLayout(detections_layout)
        layout.addWidget(detections_group)
        
        # Status bar
        status_frame = QFrame()
        status_frame.setStyleSheet(styles.get_status_frame_style())
        status_layout = QHBoxLayout(status_frame)
        
        self.status_label = QLabel("Initialisation...")
        status_layout.addWidget(self.status_label)
        
        self.fps_label = QLabel("FPS: 0.0")
        self.fps_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        status_layout.addWidget(self.fps_label)
        
        layout.addWidget(status_frame)
        
        return panel
        
    def create_right_panel(self) -> QWidget:
        """Create right panel with controls"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Video source selection
        layout.addWidget(self.create_source_group())
        
        # Display options
        layout.addWidget(self.create_display_options_group())
        
        # Model selection
        layout.addWidget(self.create_model_group())
        
        # Confidence threshold
        layout.addWidget(self.create_confidence_group())
        
        # Notification settings
        layout.addWidget(self.create_notification_group())
        
        # Recording controls
        layout.addWidget(self.create_recording_group())
        
        # Help section
        layout.addWidget(self.create_help_group())
        
        # Exit button
        layout.addWidget(self.create_exit_group())
        
        layout.addStretch()
        
        return panel
        
    def create_source_group(self) -> QGroupBox:
        """Create video source selection group"""
        group = QGroupBox("Source Vidéo")
        layout = QGridLayout()
        
        # Webcam button
        self.webcam_btn = QPushButton("Webcam Interne")
        self.webcam_btn.clicked.connect(self.use_webcam)
        layout.addWidget(self.webcam_btn, 0, 0)
        
        # External camera button
        self.external_cam_btn = QPushButton("Caméra Externe")
        self.external_cam_btn.clicked.connect(self.use_external_camera)
        layout.addWidget(self.external_cam_btn, 0, 1)
        
        # File button
        self.file_btn = QPushButton("Fichier Vidéo")
        self.file_btn.clicked.connect(self.select_video_file)
        layout.addWidget(self.file_btn, 1, 0, 1, 2)
        
        # Current source label
        self.source_label = QLabel("Source: Webcam Interne")
        self.source_label.setStyleSheet(f"font-style: italic; color: {settings.PRIMARY_COLOR};")
        self.source_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.source_label, 2, 0, 1, 2)
        
        group.setLayout(layout)
        return group
        
    def create_display_options_group(self) -> QGroupBox:
        """Create display options group"""
        group = QGroupBox("Options d'affichage")
        layout = QVBoxLayout()
        
        self.mirror_checkbox = QCheckBox("Activer l'effet miroir")
        self.mirror_checkbox.setChecked(True)
        self.mirror_checkbox.toggled.connect(self.toggle_mirror)
        layout.addWidget(self.mirror_checkbox)
        
        group.setLayout(layout)
        return group
        
    def create_model_group(self) -> QGroupBox:
        """Create model selection group"""
        group = QGroupBox("Modèle de Détection")
        layout = QVBoxLayout()
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(self.detector.get_available_models())
        self.model_combo.currentTextChanged.connect(self.change_model)
        layout.addWidget(self.model_combo)
        
        group.setLayout(layout)
        return group
        
    def create_confidence_group(self) -> QGroupBox:
        """Create confidence threshold group"""
        group = QGroupBox("Seuil de Confiance")
        layout = QVBoxLayout()
        
        self.conf_slider = QSlider(Qt.Orientation.Horizontal)
        self.conf_slider.setMinimum(int(settings.MIN_CONF_THRESHOLD * 100))
        self.conf_slider.setMaximum(int(settings.MAX_CONF_THRESHOLD * 100))
        self.conf_slider.setValue(int(settings.DEFAULT_CONF_THRESHOLD * 100))
        self.conf_slider.valueChanged.connect(self.change_conf_threshold)
        layout.addWidget(self.conf_slider)
        
        self.conf_label = QLabel(f"{settings.DEFAULT_CONF_THRESHOLD:.2f}")
        self.conf_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.conf_label)
        
        group.setLayout(layout)
        return group
        
    def create_notification_group(self) -> QGroupBox:
        """Create notification settings group"""
        group = QGroupBox("Notifications")
        layout = QVBoxLayout()
        
        self.voice_checkbox = QCheckBox("Notifications vocales")
        self.voice_checkbox.setChecked(settings.ENABLE_VOICE_BY_DEFAULT)
        layout.addWidget(self.voice_checkbox)
        
        self.zone_checkbox = QCheckBox("Annoncer les zones")
        self.zone_checkbox.setChecked(settings.ENABLE_ZONE_ANNOUNCEMENT_BY_DEFAULT)
        layout.addWidget(self.zone_checkbox)
        
        group.setLayout(layout)
        return group
        
    def create_recording_group(self) -> QGroupBox:
        """Create recording controls group"""
        group = QGroupBox("Enregistrement")
        layout = QVBoxLayout()
        
        self.record_btn = QPushButton("Démarrer Enregistrement")
        self.record_btn.clicked.connect(self.toggle_recording)
        layout.addWidget(self.record_btn)
        
        group.setLayout(layout)
        return group
        
    def create_help_group(self) -> QGroupBox:
        """Create help section group"""
        group = QGroupBox("Aide")
        layout = QVBoxLayout()
        
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setMaximumHeight(120)
        help_text.setStyleSheet(styles.get_text_edit_style())
        help_text.setHtml(styles.get_help_text_style())
        layout.addWidget(help_text)
        
        group.setLayout(layout)
        return group
        
    def create_exit_group(self) -> QGroupBox:
        """Create exit button group"""
        group = QGroupBox("Quitter")
        layout = QVBoxLayout()
        
        self.exit_btn = QPushButton("Quitter l'Application")
        self.exit_btn.setStyleSheet(styles.get_danger_button_style())
        self.exit_btn.clicked.connect(self.safe_exit)
        layout.addWidget(self.exit_btn)
        
        group.setLayout(layout)
        return group
        
    def create_footer(self, layout: QVBoxLayout):
        """Create footer"""
        footer = QLabel(settings.APP_COPYRIGHT)
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet(styles.get_footer_style())
        layout.addWidget(footer)
        
    def setup_connections(self):
        """Setup signal-slot connections"""
        # Video processor signals
        self.video_processor.frame_ready.connect(self.update_frame)
        self.video_processor.camera_error.connect(self.handle_camera_error)
        self.video_processor.fps_update.connect(self.update_fps_display)
        
    def start_processing(self):
        """Start video processing"""
        self.tts_engine.start()
        self.video_processor.start()
        self.status_label.setText("En cours...")
        
    # ========================================================================
    # Event Handlers
    # ========================================================================
    
    def update_frame(self, frame: np.ndarray, detections: list):
        """Update video display and process detections"""
        # Convert to QImage and display
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        
        scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
            self.video_label.width(),
            self.video_label.height(),
            Qt.AspectRatioMode.KeepAspectRatio
        )
        
        self.video_label.setPixmap(scaled_pixmap)
        
        # Process detections
        self.last_detections = detections
        self.update_detections_display(detections)
        self.handle_voice_notifications(detections)
        
        # Record frame if recording
        if self.recorder.is_recording():
            self.recorder.write_frame(frame)
            
    def update_detections_display(self, detections: list):
        """Update detections text display"""
        if not detections:
            self.detections_text.setText("Aucun objet détecté.")
            return
            
        # Group by zone
        zones = {"gauche": [], "milieu": [], "droite": []}
        for det in detections:
            zones[det["zone"]].append(det)
            
        # Build HTML text
        html = "<b>Objets détectés:</b><br>"
        zone_colors = {
            "gauche": "#4682B4",
            "milieu": "#2E8B57",
            "droite": "#CD5C5C"
        }
        
        for zone, zone_dets in zones.items():
            if zone_dets:
                html += f"<b style='color: {zone_colors[zone]}'>{zone.upper()}:</b> "
                objects = [f"{d['class']} ({d['confidence']:.2f})" for d in zone_dets]
                html += ", ".join(objects) + "<br>"
                
        self.detections_text.setHtml(html)
        
    def handle_voice_notifications(self, detections: list):
        """Handle voice notifications for detections"""
        if not self.voice_checkbox.isChecked():
            return
            
        if not detections:
            self.voice_manager.announce_no_detection()
            return
            
        # Group detections by class and zone
        zone_objects = {}
        current_objects = set()
        
        for det in detections:
            key = f"{det['class']}_{det['zone']}"
            current_objects.add(key)
            
            if key not in zone_objects:
                zone_objects[key] = {"class": det['class'], "zone": det['zone'], "count": 0}
            zone_objects[key]["count"] += 1
            
        # Announce each unique object-zone combination
        include_zone = self.zone_checkbox.isChecked()
        for obj_info in zone_objects.values():
            self.voice_manager.announce_detection(
                obj_info["class"],
                obj_info["zone"],
                include_zone=include_zone,
                count=obj_info["count"]
            )
            
        # Cleanup old objects
        self.voice_manager.cleanup_old_objects(current_objects)
        
    def update_fps_display(self, fps: float):
        """Update FPS display"""
        self.current_fps = fps
        self.fps_label.setText(f"FPS: {fps:.2f}")
        
    def handle_camera_error(self, error_msg: str):
        """Handle camera errors"""
        QMessageBox.critical(self, "Erreur de caméra", error_msg)
        self.status_label.setText(f"Erreur: {error_msg}")
        
    # ========================================================================
    # Control Actions
    # ========================================================================
    
    def use_webcam(self):
        """Switch to internal webcam"""
        self.stop_video_processor()
        self.video_processor.set_source("webcam")
        self.source_label.setText("Source: Webcam Interne")
        self.mirror_checkbox.setChecked(True)
        self.video_processor.start()
        
    def use_external_camera(self):
        """Switch to external camera"""
        self.stop_video_processor()
        self.video_processor.set_source("external_camera")
        self.source_label.setText("Source: Caméra Externe")
        self.mirror_checkbox.setChecked(False)
        self.video_processor.start()
        
    def select_video_file(self):
        """Select video file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner une vidéo",
            "",
            settings.VIDEO_FILE_FILTER
        )
        
        if file_path:
            self.stop_video_processor()
            self.video_processor.set_source("file", file_path)
            self.source_label.setText(f"Source: {os.path.basename(file_path)}")
            self.mirror_checkbox.setChecked(False)
            self.video_processor.start()
            
    def toggle_mirror(self, checked: bool):
        """Toggle mirror effect"""
        self.video_processor.set_flip_mode(checked)
        
    def change_model(self, model_name: str):
        """Change detection model"""
        self.video_processor.set_model(model_name)
        self.status_label.setText(f"Modèle: {model_name}")
        
    def change_conf_threshold(self):
        """Change confidence threshold"""
        value = self.conf_slider.value() / 100
        self.conf_label.setText(f"{value:.2f}")
        self.video_processor.set_conf_threshold(value)
        
    def toggle_recording(self):
        """Toggle video recording"""
        if not self.recorder.is_recording():
            # Start recording
            try:
                width, height = self.video_processor.get_frame_dimensions()
                output_path = self.recorder.start_recording(
                    width, height,
                    fps=settings.DEFAULT_FPS
                )
                self.record_btn.setText("Arrêter Enregistrement")
                self.record_btn.setStyleSheet(styles.get_recording_button_active_style())
                self.status_label.setText(f"Enregistrement: {os.path.basename(output_path)}")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de démarrer l'enregistrement: {e}")
        else:
            # Stop recording
            output_path, frames, duration = self.recorder.stop_recording()
            self.record_btn.setText("Démarrer Enregistrement")
            self.record_btn.setStyleSheet("")
            
            if output_path:
                self.status_label.setText(f"Enregistrement sauvegardé")
                QMessageBox.information(
                    self,
                    "Enregistrement terminé",
                    f"Sauvegardé: {output_path}\nFrames: {frames}\nDurée: {duration:.2f}s"
                )
                
    def update_ui_elements(self):
        """Periodic UI updates"""
        pass  # Can be used for periodic updates
        
    # ========================================================================
    # Cleanup
    # ========================================================================
    
    def stop_video_processor(self):
        """Stop video processor"""
        if self.video_processor.isRunning():
            self.video_label.clear()
            self.video_label.setText("Changement de source...")
            self.video_processor.stop()
            
    def safe_exit(self):
        """Safe application exit"""
        reply = QMessageBox.question(
            self,
            'Confirmation',
            'Êtes-vous sûr de vouloir quitter?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.closeEvent(None)
            QTimer.singleShot(500, self.close)
            
    def closeEvent(self, event):
        """Handle window close event"""
        print("Fermeture de l'application...")
        
        # Stop recording if active
        if self.recorder.is_recording():
            self.recorder.stop_recording()
            
        # Stop TTS
        if self.tts_engine:
            self.tts_engine.stop()
            
        # Stop video processor
        if self.video_processor:
            self.video_processor.stop()
            
        # Stop timer
        self.update_timer.stop()
        
        if event:
            event.accept()
            
        print("Fermeture terminée.")