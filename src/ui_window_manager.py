import webbrowser
import logging
import os
import platform

from PySide6.QtCore import QCoreApplication, QTimer
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ui_startup_dialog import StartupDialog

# Get a logger for this module
logger = logging.getLogger(__name__)

class WindowManager:
    """
    Manages the different UI components of the application, including the startup dialog,
    settings window, and shortcut display. It handles initialization, signal connections,
    and transitions between these components.
    """
    def __init__(self, app):
        """
        Initialize the WindowManager.

        Parameters:
        app (QApplication): The main application instance.
        """
        self.app = app
        
        # Load stylesheet
        stylesheet = self.load_stylesheet("data/light.qss")
        self.app.setStyleSheet(stylesheet)
        
        # Initialize window components as None; they will be lazily created
        self.startup_dialog = None
        
        # Set the application icon based on the operating system
        self.base_dir = os.path.dirname(__file__)
        self.app.setWindowIcon(QIcon(self.setup_icon_path(self.base_dir)))
    
    def setup_icon_path(self, base_dir):
        """
        Configures the appropriate icon path based on the operating system.

        Parameters:
        - base_dir (str): Base directory containing icon files.
        """
        # Set the icon path based on the operating system
        self.icon_path_win = os.path.join(base_dir, "data/icon.ico")
        self.icon_path_mac = os.path.join(base_dir, "data/icon.icns")
        self.icon_path_linux = os.path.join(base_dir, "data/icon.png")

        # Return the appropriate icon path based on the operating system
        self.icon_path = (
            self.icon_path_win if platform.system() == "Windows"
            else self.icon_path_mac if platform.system() == "Darwin"
            else self.icon_path_linux
        )
        
    def initialize_startup_dialog(self):
        """
        Lazily initialize the startup dialog if it has not been created yet.
        """
        if self.startup_dialog is None:
            self.startup_dialog = StartupDialog()
        self.connect_signals_startup_dialog()
        
    def disconnect_startup_dialog(self):
        """
        Disconnect all signals connected to the startup dialog.
        """
        self.startup_dialog.start_app_signal.disconnect()
        self.startup_dialog.quit_app_signal.disconnect()
        self.startup_dialog = None
        
    def run(self):
        """
        Start the application by checking if a database update is needed and initializing
        the appropriate window components.
        """
        self.start_app()

    def connect_signals_startup_dialog(self):
        """
        Connect the signals emitted by the startup dialog to their respective handlers.
        """
        self.startup_dialog.start_app_signal.connect(self.start_app)
        self.startup_dialog.quit_app_signal.connect(self.quit_app)

    def load_stylesheet(self, file_path):
        """
        Load the QSS stylesheet from the given file path.

        Parameters:
        file_path (str): The path to the QSS file.

        Returns:
        str: The contents of the stylesheet file.
        """
        # Attempt to load the stylesheet from the file path
        try:
            with open(file_path, "r") as file:
                return file.read()
        except Exception as e:
            logger.error(f"Failed to load stylesheet: {e}")
            return ""

    def quit_app(self):
        """
        Quit the application.
        """
        
        # Close the StartupDialog if it exists
        if self.startup_dialog:
            self.startup_dialog.close()
            self.disconnect_startup_dialog()
        QApplication.quit()

    def start_app(self):
        """
        Show the StartupDialog, closing other windows if necessary.
        """
        # Initialize the StartupDialog and show it
        self.initialize_startup_dialog()
        self.startup_dialog.show()