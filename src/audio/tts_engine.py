"""
Text-to-Speech Engine Module
Handles voice notifications and audio feedback
"""
import time
import threading
from typing import List
from PyQt6.QtCore import QThread
import pyttsx3


class TTSEngine(QThread):
    """Text-to-Speech engine for voice notifications"""
    
    def __init__(self, parent=None):
        """Initialize TTS engine"""
        super().__init__(parent)
        self.engine = pyttsx3.init()
        self.message_queue: List[str] = []
        self.mutex = threading.Lock()
        self.running = True
        
        # Default voice settings
        self.set_voice_properties(rate=150, volume=0.9)
        
    def set_voice_properties(self, rate: int = 150, volume: float = 0.9):
        """
        Configure voice properties
        
        Args:
            rate: Speech rate (words per minute)
            volume: Volume level (0.0 to 1.0)
        """
        try:
            self.engine.setProperty('rate', rate)
            self.engine.setProperty('volume', volume)
        except Exception as e:
            print(f"Warning: Could not set voice properties: {e}")
    
    def speak(self, message: str, immediate: bool = False):
        """
        Add message to speech queue
        
        Args:
            message: Text to speak
            immediate: If True, clear queue and speak immediately
        """
        with self.mutex:
            if immediate:
                self.message_queue.clear()
            self.message_queue.append(message)
    
    def add_message(self, message: str):
        """
        Add message to queue (alias for speak)
        
        Args:
            message: Text to speak
        """
        self.speak(message)
    
    def clear_queue(self):
        """Clear all pending messages"""
        with self.mutex:
            self.message_queue.clear()
    
    def get_queue_size(self) -> int:
        """Get number of pending messages"""
        with self.mutex:
            return len(self.message_queue)
    
    def run(self):
        """Main thread loop - processes message queue"""
        while self.running:
            message = None
            
            # Get next message from queue
            with self.mutex:
                if self.message_queue:
                    message = self.message_queue.pop(0)
            
            # Speak the message
            if message:
                try:
                    self.engine.say(message)
                    self.engine.runAndWait()
                except Exception as e:
                    print(f"TTS Error: {e}")
            
            # Small delay to prevent CPU hogging
            time.sleep(0.1)
    
    def stop(self):
        """Stop the TTS engine thread"""
        self.running = False
        self.clear_queue()
        
        try:
            self.engine.stop()
        except:
            pass
        
        self.wait(1000)  # Wait up to 1 second
        
        if self.isRunning():
            self.terminate()
            self.wait()
    
    def is_speaking(self) -> bool:
        """Check if engine is currently speaking"""
        return self.get_queue_size() > 0
    
    def get_available_voices(self) -> List[str]:
        """
        Get list of available voices
        
        Returns:
            List of voice names
        """
        try:
            voices = self.engine.getProperty('voices')
            return [voice.name for voice in voices]
        except:
            return []
    
    def set_voice(self, voice_id: int = 0):
        """
        Set voice by index
        
        Args:
            voice_id: Index of voice to use
        """
        try:
            voices = self.engine.getProperty('voices')
            if 0 <= voice_id < len(voices):
                self.engine.setProperty('voice', voices[voice_id].id)
        except Exception as e:
            print(f"Could not set voice: {e}")


class VoiceNotificationManager:
    """Manages voice notifications with cooldown and deduplication"""
    
    def __init__(self, tts_engine: TTSEngine, cooldown: float = 5.0):
        """
        Initialize notification manager
        
        Args:
            tts_engine: TTS engine instance
            cooldown: Seconds before repeating same object
        """
        self.tts_engine = tts_engine
        self.cooldown = cooldown
        self.last_spoken_time = {}
        self.spoken_objects = set()
        
    def announce_detection(self, class_name: str, zone: str, 
                          include_zone: bool = True, count: int = 1):
        """
        Announce an object detection
        
        Args:
            class_name: Name of detected object
            zone: Zone where object was detected
            include_zone: Whether to include zone in announcement
            count: Number of objects detected
        """
        current_time = time.time()
        object_zone_id = f"{class_name}_{zone}"
        
        # Check if we should announce (cooldown check)
        if (object_zone_id in self.last_spoken_time and
            current_time - self.last_spoken_time[object_zone_id] < self.cooldown):
            return
        
        # Build message
        if count > 1:
            message = f"{count} {class_name}"
        else:
            message = class_name
        
        if include_zone:
            message += f" à {zone}"
        
        # Speak and update tracking
        self.tts_engine.speak(message)
        self.last_spoken_time[object_zone_id] = current_time
        self.spoken_objects.add(object_zone_id)
    
    def announce_no_detection(self):
        """Announce when no objects are detected"""
        current_time = time.time()
        no_detection_id = "no_detection"
        
        # Only announce once per cooldown period
        if (no_detection_id not in self.last_spoken_time or
            current_time - self.last_spoken_time[no_detection_id] > self.cooldown):
            
            self.tts_engine.speak("Aucun objet détecté")
            self.last_spoken_time[no_detection_id] = current_time
            self.spoken_objects.clear()  # Reset for new detections
    
    def cleanup_old_objects(self, current_objects: set):
        """
        Remove objects no longer being detected from tracking
        
        Args:
            current_objects: Set of currently detected object-zone IDs
        """
        keys_to_remove = [
            key for key in self.last_spoken_time.keys()
            if key != "no_detection" and key not in current_objects
        ]
        
        for key in keys_to_remove:
            del self.last_spoken_time[key]
    
    def reset(self):
        """Reset all tracking"""
        self.last_spoken_time.clear()
        self.spoken_objects.clear()