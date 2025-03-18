import os
import logging
import json
import requests

from bs4 import BeautifulSoup
from PySide6.QtCore import Signal, QTimer
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
                               QLabel, QLineEdit, QPushButton, QDialog, QFormLayout, QDialogButtonBox,
                               QListWidget, QInputDialog)
from PySide6.QtGui import Qt, QPixmap

# Get a logger for this module
logger = logging.getLogger(__name__)

class AddParameterDialog(QDialog):
    """Dialog for adding a new parameter."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Parameter")
        layout = QFormLayout(self)
        self.name_input = QLineEdit()
        self.value_input = QLineEdit()
        self.options_input = QLineEdit()
        layout.addRow("Parameter Name:", self.name_input)
        layout.addRow("Value (optional):", self.value_input)
        layout.addRow("Options (comma-separated, for dropdown):", self.options_input)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

class EditOptionsDialog(QDialog):
    """Dialog for editing options of a parameter."""
    def __init__(self, parent, parameter_name, current_options):
        super().__init__(parent)
        self.setWindowTitle(f"Edit Options for {parameter_name}")
        self.parameter_name = parameter_name
        self.options = current_options[:]
        layout = QVBoxLayout(self)
        
        self.list_widget = QListWidget()
        self.list_widget.addItems(self.options)
        layout.addWidget(self.list_widget)
        
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add Option")
        add_button.clicked.connect(self.add_option)
        remove_button = QPushButton("Remove Selected")
        remove_button.clicked.connect(self.remove_selected)
        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)
        layout.addLayout(button_layout)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def add_option(self):
        text, ok = QInputDialog.getText(self, "Add Option", "Enter new option:")
        if ok and text.strip():
            self.options.append(text.strip())
            self.list_widget.addItem(text.strip())
    
    def remove_selected(self):
        selected_items = self.list_widget.selectedItems()
        for item in selected_items:
            self.options.remove(item.text())
            self.list_widget.takeItem(self.list_widget.row(item))
    
    def get_options(self):
        return self.options
         
class MainWindow(QMainWindow):
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
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.start_search)
        self.is_searching = False  # Prevents overlapping searches
        
        # UI for timer
        self.interval_input = QLineEdit("60")  # Default: 60 minutes
        self.set_timer_button = QPushButton("Set Timer")
        self.set_timer_button.clicked.connect(self.set_timer_interval)
        
        self.parameters = {}
        # Predefined options for certain parameters
        self.combobox_options = {
            "model": ["VW ID7", "VW ID3", "VW ID4", "Other"],
            "year": ["2019", "2020", "2021", "2022", "2023"]
        }
        
        # Initialize the UI components
        self.init_ui()
        
    def init_ui(self):
        """
        Initialize the UI components of the application.
        """
        
        # Set window properties
        self.setWindowTitle("Welcome to WebScrapper")
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        
        icon_path = self.get_icon_path()

       # Set up central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget) 

        # Create the header layout
        header_layout = self.create_header_layout(icon_path)
        layout.addLayout(header_layout)
        
        # Parameter layout for dynamic rows
        self.parameter_layout = QVBoxLayout()
        layout.addLayout(self.parameter_layout)
        
        # Create buttons
        add_button = self.create_button("Add New Parameter", self.add_parameter)
        start_button = self.create_button("Start Search", self.start_search)
        close_button = self.create_button("Close", self.close)
        
        buttons = [start_button, close_button, add_button]
         
        for button in buttons:
            layout.addWidget(button)
            
        # Set the main layout and tab order
        self.setLayout(layout)  # Note: For QMainWindow, this is handled via central widget
        self.set_tab_order(buttons)

        # Load existing parameters
        self.load_parameters()

    def set_timer_interval(self):
        interval_minutes = int(self.interval_input.text())
        self.timer.setInterval(interval_minutes * 60 * 1000)  # Convert to milliseconds
        self.timer.start()
        print(f"Search scheduled every {interval_minutes} minutes.")

    def stop_timer(self):
        self.timer.stop()
        print("Timer stopped.")
        
    def load_parameters(self):
        """Load parameters from a config file."""
        try:
            with open('data/config.json', 'r') as f:
                config = json.load(f)
                for key, value in config.get('search_params', {}).items():
                    self.add_parameter_row(key, str(value))
        except FileNotFoundError:
            pass  # Start with empty parameters if no config exists

    def add_parameter(self):
        """Open a dialog to add a new parameter."""
        dialog = AddParameterDialog(self)
        if dialog.exec() == QDialog.Accepted:
            name = dialog.name_input.text()
            value = dialog.value_input.text()
            options_str = dialog.options_input.text()
            if name and name not in self.parameters:
                options = [opt.strip() for opt in options_str.split(',') if opt.strip()] if options_str else []
                if options:
                    self.combobox_options[name] = options
                self.add_parameter_row(name, value)

    def add_parameter_row(self, name, value):
        """Add a new parameter row to the parameter_layout."""
        row_layout = QHBoxLayout()
        name_label = QLabel(name)

        if name in self.combobox_options:
            value_widget = QComboBox()
            value_widget.addItems(self.combobox_options[name])
            if value:
                index = value_widget.findText(value)
                if index >= 0:
                    value_widget.setCurrentIndex(index)
                else:
                    value_widget.setCurrentText("Other")
            edit_options_button = self.create_button("Edit Options", lambda: self.edit_options(name))
        else:
            value_widget = QLineEdit(value)
            edit_options_button = None

        remove_button = self.create_button("Remove", lambda: self.remove_parameter(name))

        row_layout.addWidget(name_label)
        row_layout.addWidget(value_widget)
        if edit_options_button:
            row_layout.addWidget(edit_options_button)
        row_layout.addWidget(remove_button)
        self.parameter_layout.addLayout(row_layout)

        self.parameters[name] = (value_widget, row_layout)
    
    def edit_options(self, name):
        """Open a dialog to edit options for the given parameter."""
        if name in self.combobox_options:
            dialog = EditOptionsDialog(self, name, self.combobox_options[name])
            if dialog.exec() == QDialog.Accepted:
                new_options = dialog.get_options()
                self.combobox_options[name] = new_options
                value_widget, _ = self.parameters[name]
                if isinstance(value_widget, QComboBox):
                    current_text = value_widget.currentText()
                    value_widget.clear()
                    value_widget.addItems(new_options)
                    index = value_widget.findText(current_text)
                    if index >= 0:
                        value_widget.setCurrentIndex(index)
                    else:
                        value_widget.setCurrentIndex(0)
    
    def load_parameters(self):
        """Load parameters from a config file."""
        try:
            with open('data/config.json', 'r') as f:
                config = json.load(f)
                self.combobox_options = config.get('combobox_options', self.combobox_options)
                for key, value in config.get('search_params', {}).items():
                    self.add_parameter_row(key, str(value))
        except FileNotFoundError:
            pass  # Start with empty parameters if no config exists
        
    def remove_parameter(self, name):
        """Remove a parameter row from the layout."""
        value_edit, row_layout = self.parameters.pop(name)
        for i in reversed(range(row_layout.count())):
            widget = row_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        self.parameter_layout.removeItem(row_layout)

    def start_search(self):
        if self.is_searching:
            print("Waiting for previous search to finish...")
            return
        self.is_searching = True
        try:
            # Your scraper logic here
            print("Running search...")
        finally:
            self.is_searching = False
            
        # Load the JSON config
        with open('config.json', 'r') as f:
            config = json.load(f)
        search_params = config.get('search_params', {})
        
        # Check if required parameters are present
        required_fields = ['model', 'year']  # Adjust based on your needs
        if not all(field in search_params for field in required_fields):
            print("Error: Missing required search parameters.")
            return
        
        # Construct the search URL
        base_url = "https://www.example.com/search?"
        query = "&".join([f"{key}={value}" for key, value in search_params.items()])
        search_url = base_url + query
        
        # Fetch and scrape the page
        response = requests.get(search_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract listings (adjust selectors to match the website)
        listings = []
        for item in soup.select('.listing-item'):
            title = item.select_one('.title').text
            price = item.select_one('.price').text
            listings.append({'title': title, 'price': price})
        
        print("Scraped listings:", listings)
        # Next: Send these listings to the notification system
        
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