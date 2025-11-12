"""
Zone Detector Module
Determines spatial zones (left, center, right) for objects
"""
import cv2
import numpy as np
from typing import Tuple, Dict


class ZoneDetector:
    """Divides frame into zones and determines object positions"""
    
    # Zone colors (BGR format)
    ZONE_COLORS = {
        "gauche": (70, 70, 200),   # Red
        "milieu": (70, 200, 70),   # Green
        "droite": (200, 70, 70)    # Blue
    }
    
    def __init__(self, frame_width: int, divisions: int = 3):
        """
        Initialize zone detector
        
        Args:
            frame_width: Width of the video frame
            divisions: Number of zones (default: 3 for left/center/right)
        """
        self.frame_width = frame_width
        self.divisions = divisions
        self.update_boundaries(frame_width)
        
    def update_boundaries(self, frame_width: int):
        """
        Update zone boundaries based on frame width
        
        Args:
            frame_width: New frame width
        """
        self.frame_width = frame_width
        self.left_boundary = frame_width // 3
        self.right_boundary = 2 * frame_width // 3
        
    def get_zone(self, bbox: Tuple[int, int, int, int] = None, 
                 center_x: int = None) -> str:
        """
        Determine which zone an object is in
        
        Args:
            bbox: Bounding box (x1, y1, x2, y2) - optional
            center_x: X coordinate of object center - optional
            
        Returns:
            Zone name: "gauche", "milieu", or "droite"
        """
        if center_x is None and bbox is not None:
            x1, _, x2, _ = bbox
            center_x = (x1 + x2) // 2
        
        if center_x is None:
            return "milieu"  # Default
        
        if center_x < self.left_boundary:
            return "gauche"
        elif center_x > self.right_boundary:
            return "droite"
        else:
            return "milieu"
    
    def get_zone_color(self, zone: str) -> Tuple[int, int, int]:
        """
        Get color for a specific zone
        
        Args:
            zone: Zone name
            
        Returns:
            BGR color tuple
        """
        return self.ZONE_COLORS.get(zone, (255, 255, 255))
    
    def draw_zones(self, frame: np.ndarray, alpha: float = 0.3) -> np.ndarray:
        """
        Draw zone divisions and labels on frame
        
        Args:
            frame: Input frame
            alpha: Transparency level for overlays
            
        Returns:
            Frame with zone markings
        """
        height, width = frame.shape[:2]
        
        # Update boundaries if frame size changed
        if width != self.frame_width:
            self.update_boundaries(width)
        
        # Draw vertical dividing lines
        cv2.line(frame, (self.left_boundary, 0), 
                (self.left_boundary, height), (255, 255, 255), 1)
        cv2.line(frame, (self.right_boundary, 0), 
                (self.right_boundary, height), (255, 255, 255), 1)
        
        # Create transparent overlay for labels
        overlay = frame.copy()
        
        # Left zone label
        cv2.rectangle(overlay, (10, 10), (self.left_boundary - 10, 40),
                     self.ZONE_COLORS["gauche"], -1)
        cv2.putText(overlay, "GAUCHE", (20, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Center zone label
        cv2.rectangle(overlay, (self.left_boundary + 10, 10),
                     (self.right_boundary - 10, 40),
                     self.ZONE_COLORS["milieu"], -1)
        cv2.putText(overlay, "MILIEU", (self.left_boundary + 50, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Right zone label
        cv2.rectangle(overlay, (self.right_boundary + 10, 10),
                     (width - 10, 40), self.ZONE_COLORS["droite"], -1)
        cv2.putText(overlay, "DROITE", (self.right_boundary + 50, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Apply transparent overlay
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        return frame
    
    def get_boundaries(self) -> Dict[str, int]:
        """
        Get zone boundary coordinates
        
        Returns:
            Dictionary with boundary positions
        """
        return {
            "left_boundary": self.left_boundary,
            "right_boundary": self.right_boundary,
            "frame_width": self.frame_width
        }
    
    def draw_detection_with_zone(self, frame: np.ndarray, detection: Dict) -> np.ndarray:
        """
        Draw a single detection with zone-based coloring
        
        Args:
            frame: Input frame
            detection: Detection dictionary with bbox, class, confidence, zone
            
        Returns:
            Frame with drawn detection
        """
        x1, y1, x2, y2 = detection["bbox"]
        zone = detection.get("zone", "milieu")
        color = self.get_zone_color(zone)
        
        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        # Draw label
        label = f"{detection['class']}"
        if "id" in detection:
            label += f" #{detection['id']}"
        if "confidence" in detection:
            label += f" {detection['confidence']:.2f}"
        
        cv2.putText(frame, label, (x1, y1 - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return frame