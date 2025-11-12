"""
Video Processor Module
Handles video capture, processing, and frame emission
"""
import time
import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal
from typing import Optional, List, Dict

from src.core.detector import YOLODetector
from src.core.tracker import ObjectTracker
from src.utils.zone_detector import ZoneDetector
from config import settings


class VideoProcessorThread(QThread):
    """Thread for processing video frames with object detection and tracking"""
    
    # Signals
    frame_ready = pyqtSignal(np.ndarray, list)  # frame, detections
    camera_error = pyqtSignal(str)  # error message
    fps_update = pyqtSignal(float)  # current FPS
    
    def __init__(self, detector: YOLODetector, parent=None):
        """
        Initialize video processor thread
        
        Args:
            detector: YOLO detector instance
            parent: Parent QObject
        """
        super().__init__(parent)
        
        # Core components
        self.detector = detector
        self.tracker: Optional[ObjectTracker] = None
        self.zone_detector: Optional[ZoneDetector] = None
        
        # Video source settings
        self.source = settings.DEFAULT_CAMERA_INDEX
        self.source_type = "webcam"
        self.file_path = ""
        
        # Processing settings
        self.conf_threshold = settings.DEFAULT_CONF_THRESHOLD
        self.flip_frame = True  # Mirror effect for webcam
        
        # State
        self.running = False
        self.paused = False
        
        # Performance tracking
        self.frame_rate = 0.0
        self.last_time = time.time()
        self.frame_count = 0
        
        # Frame dimensions
        self.current_frame_width = settings.DEFAULT_FRAME_WIDTH
        self.current_frame_height = settings.DEFAULT_FRAME_HEIGHT
        
    def set_source(self, source_type: str, file_path: str = ""):
        """
        Set video source
        
        Args:
            source_type: Type of source ("webcam", "external_camera", "file")
            file_path: Path to video file (for "file" type)
        """
        self.source_type = source_type
        
        if source_type == "webcam":
            self.source = settings.DEFAULT_CAMERA_INDEX
            self.flip_frame = True
        elif source_type == "external_camera":
            self.source = settings.EXTERNAL_CAMERA_INDEX
            self.flip_frame = False
        else:  # file
            self.source = file_path
            self.file_path = file_path
            self.flip_frame = False
            
    def set_flip_mode(self, flip: bool):
        """Enable or disable mirror effect"""
        self.flip_frame = flip
        
    def set_conf_threshold(self, threshold: float):
        """Set confidence threshold for detections"""
        self.conf_threshold = max(settings.MIN_CONF_THRESHOLD, 
                                 min(threshold, settings.MAX_CONF_THRESHOLD))
        
    def set_model(self, model_name: str):
        """
        Switch detection model
        
        Args:
            model_name: Name of model to use
        """
        if self.detector.switch_model(model_name):
            # Update tracker with new model
            if self.tracker:
                self.tracker = ObjectTracker(self.detector.current_model)
                
    def pause(self):
        """Pause video processing"""
        self.paused = True
        
    def resume(self):
        """Resume video processing"""
        self.paused = False
        
    def run(self):
        """Main thread execution - process video frames"""
        cap = None
        
        try:
            # Open video source
            cap = self._open_video_source()
            if cap is None:
                return
            
            # Get frame dimensions
            self.current_frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.current_frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Initialize tracker and zone detector
            self.tracker = ObjectTracker(self.detector.current_model)
            self.zone_detector = ZoneDetector(self.current_frame_width)
            
            # Processing loop
            self.running = True
            while self.running:
                if self.paused:
                    time.sleep(0.1)
                    continue
                
                # Read frame
                ret, frame = cap.read()
                
                if not ret:
                    if self.source_type == "file":
                        # Loop video file
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        continue
                    else:
                        break
                
                # Process frame
                processed_frame, detections = self._process_frame(frame)
                
                # Calculate FPS
                self._update_fps()
                
                # Emit results
                self.frame_ready.emit(processed_frame, detections)
                
        except Exception as e:
            error_msg = f"Error in video processing: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            self.camera_error.emit(error_msg)
            
        finally:
            if cap is not None:
                cap.release()
            self.running = False
            
    def _open_video_source(self) -> Optional[cv2.VideoCapture]:
        """
        Open video capture source
        
        Returns:
            VideoCapture object or None on failure
        """
        try:
            cap = cv2.VideoCapture(self.source)
            
            if not cap.isOpened():
                error_msg = f"Cannot open video source: {self.source_type}"
                print(error_msg)
                self.camera_error.emit(error_msg)
                return None
                
            return cap
            
        except Exception as e:
            error_msg = f"Error opening video source: {str(e)}"
            print(error_msg)
            self.camera_error.emit(error_msg)
            return None
            
    def _process_frame(self, frame: np.ndarray) -> tuple:
        """
        Process a single frame
        
        Args:
            frame: Input frame
            
        Returns:
            Tuple of (processed_frame, detections_list)
        """
        # Apply mirror effect if needed
        if self.flip_frame:
            frame = cv2.flip(frame, 1)
        
        # Draw zone divisions
        frame = self.zone_detector.draw_zones(frame)
        
        # Perform tracking
        detections = []
        if self.tracker and self.detector.current_model:
            tracked_objects = self.tracker.track(frame, self.conf_threshold)
            
            # Add zone information to each detection
            for obj in tracked_objects:
                zone = self.zone_detector.get_zone(bbox=obj["bbox"])
                obj["zone"] = zone
                
                # Draw detection with zone color
                frame = self.zone_detector.draw_detection_with_zone(frame, obj)
                
                detections.append(obj)
        
        # Add FPS and mirror status overlay
        self._draw_overlays(frame)
        
        return frame, detections
        
    def _draw_overlays(self, frame: np.ndarray):
        """
        Draw FPS and status overlays on frame
        
        Args:
            frame: Frame to draw on (modified in place)
        """
        height, width = frame.shape[:2]
        
        # FPS display
        if settings.SHOW_FPS:
            cv2.putText(frame, f"FPS: {self.frame_rate:.2f}", 
                       (width - 150, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Mirror status
        mirror_status = "Miroir: ON" if self.flip_frame else "Miroir: OFF"
        cv2.putText(frame, mirror_status, 
                   (width - 150, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
    def _update_fps(self):
        """Update FPS calculation"""
        current_time = time.time()
        if current_time - self.last_time > 0:
            self.frame_rate = 1.0 / (current_time - self.last_time)
            self.fps_update.emit(self.frame_rate)
        self.last_time = current_time
        self.frame_count += 1
        
    def stop(self):
        """Stop the video processor thread"""
        self.running = False
        self.wait(settings.THREAD_WAIT_TIMEOUT)
        
        if self.isRunning():
            self.terminate()
            self.wait()
            
    def get_frame_dimensions(self) -> tuple:
        """
        Get current frame dimensions
        
        Returns:
            Tuple of (width, height)
        """
        return (self.current_frame_width, self.current_frame_height)
        
    def get_stats(self) -> Dict:
        """
        Get processing statistics
        
        Returns:
            Dictionary with stats
        """
        return {
            "fps": self.frame_rate,
            "frame_count": self.frame_count,
            "source_type": self.source_type,
            "running": self.running,
            "paused": self.paused
        }