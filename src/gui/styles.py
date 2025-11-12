"""
GUI Styles Module
Centralized styling for the application interface
"""
from PyQt6.QtWidgets import QApplication, QStyleFactory
from PyQt6.QtGui import QPalette, QColor
from config import settings


def apply_app_style(app: QApplication = None):
    """
    Apply dark theme to application
    
    Args:
        app: QApplication instance (if None, uses current instance)
    """
    if app is None:
        app = QApplication.instance()
        
    # Set Fusion style
    QApplication.setStyle(QStyleFactory.create("Fusion"))
    
    # Create dark palette
    palette = create_dark_palette()
    app.setPalette(palette)
    
    # Apply stylesheet
    app.setStyleSheet(get_main_stylesheet())


def create_dark_palette() -> QPalette:
    """
    Create dark color palette
    
    Returns:
        QPalette with dark theme colors
    """
    palette = QPalette()
    
    # Base colors
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
    
    return palette


def get_main_stylesheet() -> str:
    """
    Get main application stylesheet
    
    Returns:
        CSS stylesheet string
    """
    return f"""
        /* Buttons */
        QPushButton {{
            background-color: {settings.PRIMARY_COLOR};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {settings.SECONDARY_COLOR};
        }}
        QPushButton:pressed {{
            background-color: {settings.ACCENT_COLOR};
        }}
        QPushButton:disabled {{
            background-color: #cccccc;
            color: #666666;
        }}
        
        /* GroupBox */
        QGroupBox {{
            border: 1px solid {settings.PRIMARY_COLOR};
            border-radius: 5px;
            margin-top: 20px;
            font-weight: bold;
            color: {settings.PRIMARY_COLOR};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 5px;
            color: {settings.PRIMARY_COLOR};
        }}
        
        /* Sliders */
        QSlider::groove:horizontal {{
            border: 1px solid #999999;
            height: 8px;
            background: #3A3A3A;
            margin: 2px 0;
            border-radius: 4px;
        }}
        QSlider::handle:horizontal {{
            background: {settings.PRIMARY_COLOR};
            border: 1px solid {settings.PRIMARY_COLOR};
            width: 18px;
            height: 18px;
            margin: -8px 0;
            border-radius: 9px;
        }}
        
        /* ComboBox */
        QComboBox {{
            border: 1px solid {settings.PRIMARY_COLOR};
            border-radius: 3px;
            padding: 5px;
            min-width: 6em;
        }}
        QComboBox:hover {{
            border: 1px solid {settings.SECONDARY_COLOR};
        }}
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 15px;
            border-left-width: 1px;
            border-left-color: {settings.PRIMARY_COLOR};
            border-left-style: solid;
            border-top-right-radius: 3px;
            border-bottom-right-radius: 3px;
        }}
    """


def get_danger_button_style() -> str:
    """
    Get style for danger/exit buttons
    
    Returns:
        CSS for danger buttons
    """
    return f"""
        QPushButton {{
            background-color: {settings.DANGER_COLOR};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {settings.DANGER_HOVER};
        }}
        QPushButton:pressed {{
            background-color: #a93226;
        }}
    """


def get_success_button_style() -> str:
    """
    Get style for success buttons
    
    Returns:
        CSS for success buttons
    """
    return f"""
        QPushButton {{
            background-color: {settings.SUCCESS_COLOR};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: #27ae60;
        }}
        QPushButton:pressed {{
            background-color: #229954;
        }}
    """


def get_video_frame_style() -> str:
    """
    Get style for video display frame
    
    Returns:
        CSS for video frame
    """
    return f"""
        QFrame {{
            background-color: #1e1e1e;
            border: 2px solid {settings.PRIMARY_COLOR};
            border-radius: 8px;
        }}
        QLabel {{
            border: none;
            background-color: #1e1e1e;
        }}
    """


def get_text_edit_style() -> str:
    """
    Get style for text edit widgets
    
    Returns:
        CSS for text edits
    """
    return f"""
        QTextEdit {{
            background-color: {settings.BACKGROUND_LIGHT};
            border: 1px solid {settings.BORDER_COLOR};
            border-radius: 5px;
            color: {settings.TEXT_COLOR};
        }}
    """


def get_status_frame_style() -> str:
    """
    Get style for status bar frame
    
    Returns:
        CSS for status frame
    """
    return f"""
        QFrame {{
            background-color: {settings.BACKGROUND_LIGHT};
            border-radius: 5px;
            padding: 5px;
        }}
    """


def get_title_style() -> str:
    """
    Get style for title labels
    
    Returns:
        CSS for titles
    """
    return f"""
        QLabel {{
            color: {settings.PRIMARY_COLOR};
            font-size: {settings.TITLE_FONT_SIZE}px;
            font-weight: {settings.TITLE_FONT_WEIGHT};
            margin: 10px 0;
        }}
    """


def get_footer_style() -> str:
    """
    Get style for footer labels
    
    Returns:
        CSS for footer
    """
    return """
        QLabel {
            color: #999;
            font-size: 11px;
            padding: 5px;
        }
    """


def get_help_text_style() -> str:
    """
    Get formatted help text with styling
    
    Returns:
        HTML formatted help text
    """
    return f"""
        <p style="color: {settings.PRIMARY_COLOR};"><b>Guide rapide:</b></p>
        <ul>
            <li>Sélectionnez une source vidéo (webcam interne, caméra externe ou fichier)</li>
            <li>Ajustez le seuil de confiance selon vos besoins</li>
            <li>L'écran est divisé en 3 zones: gauche, milieu et droite</li>
            <li>Les objets sont signalés vocalement avec leur position</li>
            <li>Utilisez la case à cocher "Effet miroir" pour activer/désactiver l'effet miroir</li>
        </ul>
    """


def get_recording_button_active_style() -> str:
    """
    Get style for active recording button
    
    Returns:
        CSS for active recording button
    """
    return f"""
        QPushButton {{
            background-color: {settings.DANGER_COLOR};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }}
    """