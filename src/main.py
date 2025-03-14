import os
import sys
import logging
import sentry_sdk

from PySide6.QtWidgets import QApplication
from ui_window_manager import WindowManager
from bug_reporting import exception_hook

# Initialize Sentry once in your application's entry point
sentry_sdk.init(dsn="https://cf091345c1c0562686b5b85b3c64cb31@o4508930992439296.ingest.de.sentry.io/4508930996699216", traces_sample_rate=1.0)

# Ensure the 'data' directory exists
log_dir = "data"
log_file = os.path.join(log_dir, "application.log")

if not os.path.exists(log_dir):
    os.makedirs(log_dir)  # Create the directory if it does not exist

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename=log_file,  # Single log file for all modules
    filemode="a",  # Append mode
)

logger = logging.getLogger(__name__)

logger.info("Logging is configured successfully.")
        
def main():
    """
    Initialize and run the application.

    This function sets up the core event loop by creating an instance of `QApplication`.
    It initializes the `WindowManager` to manage the different application windows 
    and then starts the main event loop to handle GUI events.
    """
               
    # Create the QApplication instance - necessary for managing all GUI components.
    app = QApplication(sys.argv)
    
    # Set the exception hook to handle uncaught exceptions and display a bug report dialog.
    sys.excepthook = exception_hook
    
    # Create the main window manager instance that handles all application windows and signals.
    window_manager = WindowManager(app)

    # Begin running the window manager to show and manage the app's windows.
    window_manager.run()

    # Execute the main Qt event loop, which processes user inputs and updates the GUI.
    sys.exit(app.exec())

if __name__ == "__main__":
    # Entry point of the application.
    main()
