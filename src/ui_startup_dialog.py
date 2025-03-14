import os
import logging

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QDialog
from PySide6.QtGui import Qt, QPixmap

# Get a logger for this module
logger = logging.getLogger(__name__)

class StartupDialog(QDialog):
    """
    Manages the different UI components of the application.
    """
    
    # Signals to interact with other parts of the application
    start_app_signal = Signal()
    quit_app_signal = Signal()
    
    def __init__(self, parent=None):
        """
        Initialize the WindowManager.

        Parameters:
        app (QApplication): The main application instance.
        """
        
        # Initialize the dialog with the parent widget
        super().__init__(parent)
        
        # Initialize the UI components
        self.init_ui()
        
    def init_ui(self):
        """
        Initialize the UI components of the application.
        """
        
        # Set window properties
        self.setWindowTitle("Welcome to WebScrapper")
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setModal(True)  # Block interaction with the main window until this dialog is handled
        
        icon_path = self.get_icon_path()

        # Set up the layout for the dialog
        layout = QVBoxLayout()

        # Create the header layout
        header_layout = self.create_header_layout(icon_path)
        layout.addLayout(header_layout)
        
        # Create buttons
        start_button = self.create_start_button()
        close_button = self.create_close_button()
        
        buttons = [start_button, close_button]
         
        for button in buttons:
            layout.addWidget(button)
            
        # Set the main layout for the dialog
        self.setLayout(layout)
        self.set_tab_order(buttons)

    def set_tab_order(self, buttons):
        """
        Set the tab order for the given list of buttons.

        Parameters:
        buttons (list): List of QPushButton objects whose tab order needs to be set.
        """
        for i in range(len(buttons) - 1):
            self.setTabOrder(buttons[i], buttons[i + 1])

    @staticmethod
    def create_button(text, click_handler):
        """
        Create a QPushButton with the given text and connect it to the specified click handler.

        Parameters:
        text (str): The label for the button.
        click_handler (callable): The function to be called when the button is clicked.

        Returns:
        QPushButton: A QPushButton object.
        """
        button = QPushButton(text)
        button.clicked.connect(click_handler)
        button.setFocusPolicy(Qt.NoFocus)
        return button
    
    def create_start_button(self):
        """
        Create the "Start" button to initiate the main application.

        Returns:
        QPushButton: A QPushButton object for starting the application.
        """
        button = self.create_button("Start HotKey Helper", lambda: self.emit_start_app_signal())
        button.setDefault(True)
        return button
    
    def create_close_button(self):
        """
        Create the "Quit" button to close the application.

        Returns:
        QPushButton: A QPushButton object for quitting the application.
        """
        button = self.create_button("Quit", lambda: self.emit_quit_app_signal())
        return button
    
    def emit_start_app_signal(self):
        """
        Emit the signal to start the main application.
        """
        if not self.is_action_in_progress:
            self.is_action_in_progress = True
            self.start_app_signal.emit()
            
    def emit_quit_app_signal(self):
        """
        Emit the signal to quit the application.
        """
        self.quit_app_signal.emit()
    
    @staticmethod
    def get_icon_path():
        """
        Get the path to the icon file used in the header layout.

        Returns:
        str: The full path to the icon file.
        """
        return os.path.join(os.path.dirname(__file__), "data/icon.png")
    
    @staticmethod
    def create_header_layout(icon_path):
        """
        Create the header layout containing the icon and welcome text.

        Parameters:
        icon_path (str): Path to the icon image file.

        Returns:
        QHBoxLayout: A layout containing the icon and welcome text.
        """
        
        # Create a horizontal layout
        horizontal_layout = QHBoxLayout()

        # Load the icon
        icon_pixmap = QPixmap(icon_path)
        if icon_pixmap.isNull():
            icon_pixmap = QPixmap(32, 32)  # Create a blank pixmap as a placeholder
            icon_pixmap.fill(Qt.gray)  # Optional: Add color for a placeholder
            welcome_label = QLabel("Welcome! (Icon missing)")
        else:
            icon_pixmap = icon_pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label = QLabel()
            icon_label.setPixmap(icon_pixmap)
            icon_label.setFixedSize(32, 32)
            horizontal_layout.addWidget(icon_label)

        # Welcome label
        if 'welcome_label' not in locals():
            welcome_label = QLabel("WebScrapper!\nSetup your search and press Enter to start:")

        # Add the welcome label to the layout
        horizontal_layout.addWidget(welcome_label)
        horizontal_layout.setAlignment(Qt.AlignVCenter)
        horizontal_layout.addSpacing(10)

        return horizontal_layout