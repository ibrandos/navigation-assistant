"""
Core Detection and Tracking Modules
Contains YOLO detection, object tracking, and video processing
"""
from .detector import YOLODetector
from .tracker import ObjectTracker
from .video_processor import VideoProcessorThread

__all__ = ['YOLODetector', 'ObjectTracker', 'VideoProcessorThread']