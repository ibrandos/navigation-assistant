"""
Navigation Assistant - Main Entry Point
Real-time navigation assistant for the visually impaired
"""
import sys
from PyQt6.QtWidgets import QApplication
from src.gui.main_window import NavigationAssistantGUI
from config import settings


def main():
    """Main application entry point"""
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName(settings.APP_NAME)
    app.setApplicationVersion(settings.APP_VERSION)
    
    # Create and show main window
    window = NavigationAssistantGUI()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)