"""
Video Recorder Module
Handles recording of annotated video streams
"""
import os
import time
import cv2
from typing import Optional, Tuple
from pathlib import Path


class VideoRecorder:
    """Manages video recording with annotations"""
    
    def __init__(self, output_dir: str = None):
        """
        Initialize video recorder
        
        Args:
            output_dir: Directory to save recordings (default: ~/Navigation_Assistant_Recordings)
        """
        if output_dir is None:
            output_dir = os.path.join(os.path.expanduser("~"), "Navigation_Assistant_Recordings")
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.writer: Optional[cv2.VideoWriter] = None
        self.output_path: Optional[str] = None
        self.is_recording_flag = False
        self.frame_count = 0
        self.start_time = None
        
    def start_recording(self, frame_width: int, frame_height: int, 
                       fps: float = 20.0, codec: str = 'mp4v') -> str:
        """
        Start recording video
        
        Args:
            frame_width: Width of video frames
            frame_height: Height of video frames
            fps: Frames per second
            codec: Video codec (default: mp4v)
            
        Returns:
            Path to output file
        """
        if self.is_recording_flag:
            print("Recording already in progress")
            return self.output_path
        
        # Generate unique filename with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.mp4"
        self.output_path = str(self.output_dir / filename)
        
        # Initialize video writer
        fourcc = cv2.VideoWriter_fourcc(*codec)
        self.writer = cv2.VideoWriter(
            self.output_path,
            fourcc,
            fps,
            (frame_width, frame_height)
        )
        
        if not self.writer.isOpened():
            raise RuntimeError(f"Failed to open video writer for {self.output_path}")
        
        self.is_recording_flag = True
        self.frame_count = 0
        self.start_time = time.time()
        
        print(f"Recording started: {self.output_path}")
        return self.output_path
    
    def write_frame(self, frame) -> bool:
        """
        Write a frame to the video
        
        Args:
            frame: Frame to write
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_recording_flag or self.writer is None:
            return False
        
        try:
            self.writer.write(frame)
            self.frame_count += 1
            return True
        except Exception as e:
            print(f"Error writing frame: {e}")
            return False
    
    def stop_recording(self) -> Tuple[str, int, float]:
        """
        Stop recording and release resources
        
        Returns:
            Tuple of (output_path, frame_count, duration)
        """
        if not self.is_recording_flag:
            print("No recording in progress")
            return None, 0, 0.0
        
        # Calculate duration
        duration = time.time() - self.start_time if self.start_time else 0.0
        
        # Release writer
        if self.writer is not None:
            self.writer.release()
            self.writer = None
        
        output_path = self.output_path
        frame_count = self.frame_count
        
        self.is_recording_flag = False
        self.output_path = None
        self.frame_count = 0
        self.start_time = None
        
        print(f"Recording stopped: {output_path}")
        print(f"  Frames: {frame_count}, Duration: {duration:.2f}s")
        
        return output_path, frame_count, duration
    
    def is_recording(self) -> bool:
        """Check if currently recording"""
        return self.is_recording_flag
    
    def get_recording_info(self) -> dict:
        """
        Get information about current recording
        
        Returns:
            Dictionary with recording info
        """
        if not self.is_recording_flag:
            return {
                "is_recording": False,
                "output_path": None,
                "frame_count": 0,
                "duration": 0.0
            }
        
        duration = time.time() - self.start_time if self.start_time else 0.0
        
        return {
            "is_recording": True,
            "output_path": self.output_path,
            "frame_count": self.frame_count,
            "duration": duration
        }
    
    def get_recordings_list(self) -> list:
        """
        Get list of all recorded videos
        
        Returns:
            List of recording file paths
        """
        recordings = []
        
        if self.output_dir.exists():
            recordings = sorted(
                [str(f) for f in self.output_dir.glob("recording_*.mp4")],
                reverse=True
            )
        
        return recordings
    
    def cleanup_old_recordings(self, keep_count: int = 10):
        """
        Remove old recordings, keeping only the most recent ones
        
        Args:
            keep_count: Number of recordings to keep
        """
        recordings = self.get_recordings_list()
        
        if len(recordings) > keep_count:
            for old_recording in recordings[keep_count:]:
                try:
                    os.remove(old_recording)
                    print(f"Removed old recording: {old_recording}")
                except Exception as e:
                    print(f"Could not remove {old_recording}: {e}")