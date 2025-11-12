"""
YOLO Detector Module
Handles model loading and object detection
"""
import os
from typing import Dict, Optional, List
from ultralytics import YOLO
import numpy as np


class YOLODetector:
    """Manages YOLO models and performs object detection"""
    
    def __init__(self, default_model: str = "yolov8n"):
        """
        Initialize the YOLO detector
        
        Args:
            default_model: Name of the default model to load
        """
        self.models: Dict[str, Optional[YOLO]] = {}
        self.current_model_name = default_model
        self.current_model: Optional[YOLO] = None
        self.load_all_models()
        
    def load_all_models(self):
        """Load all available YOLO models"""
        model_configs = {
            "yolov8n": "yolov8n.pt",
            "yolo11n": "yolo11n.pt",
            "yolo8_personnalisé": "best8.pt",
            "yolo11_personnalisé": "best11.pt"
        }
        
        for model_name, model_file in model_configs.items():
            try:
                if os.path.exists(model_file) or model_name in ["yolov8n", "yolo11n"]:
                    self.models[model_name] = YOLO(model_file)
                    print(f"✓ {model_name} loaded successfully")
                else:
                    self.models[model_name] = None
                    print(f"✗ {model_name} not available ({model_file} not found)")
            except Exception as e:
                print(f"✗ Error loading {model_name}: {e}")
                self.models[model_name] = None
        
        # Set current model
        self.current_model = self.models.get(self.current_model_name)
        
    def switch_model(self, model_name: str) -> bool:
        """
        Switch to a different model
        
        Args:
            model_name: Name of the model to switch to
            
        Returns:
            True if successful, False otherwise
        """
        if model_name not in self.models:
            print(f"Model {model_name} not found")
            return False
            
        if self.models[model_name] is None:
            print(f"Model {model_name} not loaded")
            return False
            
        self.current_model_name = model_name
        self.current_model = self.models[model_name]
        print(f"Switched to {model_name}")
        return True
    
    def detect(self, frame: np.ndarray, conf_threshold: float = 0.25) -> List[Dict]:
        """
        Perform object detection on a frame
        
        Args:
            frame: Input image frame
            conf_threshold: Confidence threshold for detections
            
        Returns:
            List of detections with bounding boxes, confidence, and class names
        """
        if self.current_model is None:
            return []
        
        results = self.current_model(frame, conf=conf_threshold, verbose=False)
        
        detections = []
        for result in results:
            boxes = result.boxes
            for i, box in enumerate(boxes.xyxy.cpu().numpy()):
                x1, y1, x2, y2 = box.astype(int)
                conf = float(boxes.conf[i].item())
                cls = int(boxes.cls[i].item())
                class_name = result.names[cls]
                
                detections.append({
                    "bbox": (x1, y1, x2, y2),
                    "confidence": conf,
                    "class": class_name,
                    "class_id": cls
                })
        
        return detections
    
    def get_available_models(self) -> List[str]:
        """Get list of available model names"""
        return [name for name, model in self.models.items() if model is not None]
    
    def is_model_loaded(self, model_name: str) -> bool:
        """Check if a specific model is loaded"""
        return model_name in self.models and self.models[model_name] is not None