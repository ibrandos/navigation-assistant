"""
Object Tracker Module
Implements ByteTrack for persistent object tracking
"""
import numpy as np
from typing import List, Dict, Optional
from ultralytics import YOLO


class ObjectTracker:
    """Handles object tracking across frames using ByteTrack"""
    
    def __init__(self, model: YOLO):
        """
        Initialize the object tracker
        
        Args:
            model: YOLO model to use for tracking
        """
        self.model = model
        self.tracked_objects: Dict[int, Dict] = {}
        
    def track(self, frame: np.ndarray, conf_threshold: float = 0.25) -> List[Dict]:
        """
        Track objects in a frame
        
        Args:
            frame: Input image frame
            conf_threshold: Confidence threshold for detections
            
        Returns:
            List of tracked objects with IDs, bounding boxes, and class info
        """
        if self.model is None:
            return []
        
        # Use ByteTrack for tracking
        results = self.model.track(
            source=frame,
            conf=conf_threshold,
            show=False,
            tracker="bytetrack.yaml",
            stream=False,
            verbose=False
        )
        
        tracked_detections = []
        
        for result in results:
            boxes = result.boxes
            
            # Get tracking IDs if available
            track_ids = None
            if hasattr(boxes, 'id') and boxes.id is not None:
                track_ids = boxes.id.int().cpu().tolist()
            
            # Process each detection
            for i, box in enumerate(boxes.xyxy.cpu().numpy()):
                x1, y1, x2, y2 = box.astype(int)
                conf = float(boxes.conf[i].item())
                cls = int(boxes.cls[i].item())
                class_name = result.names[cls]
                
                # Get tracking ID
                track_id = i  # Default ID
                if track_ids is not None and i < len(track_ids):
                    track_id = int(track_ids[i])
                
                # Calculate center point
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                
                detection = {
                    "id": track_id,
                    "bbox": (x1, y1, x2, y2),
                    "center": (center_x, center_y),
                    "confidence": conf,
                    "class": class_name,
                    "class_id": cls
                }
                
                tracked_detections.append(detection)
                
                # Update tracked objects dictionary
                self.tracked_objects[track_id] = detection
        
        return tracked_detections
    
    def get_object_by_id(self, track_id: int) -> Optional[Dict]:
        """
        Get tracked object by ID
        
        Args:
            track_id: Tracking ID of the object
            
        Returns:
            Object information or None if not found
        """
        return self.tracked_objects.get(track_id)
    
    def clear_tracks(self):
        """Clear all tracked objects"""
        self.tracked_objects.clear()
    
    def get_active_tracks(self) -> List[int]:
        """Get list of active tracking IDs"""
        return list(self.tracked_objects.keys())