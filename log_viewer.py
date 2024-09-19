from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QComboBox
from PyQt5.QtGui import QColor

class LogViewerTab(QWidget):
    def __init__(self):
        super().__init__()

        # Create layout
        layout = QVBoxLayout(self)

        # Create search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search logs...")
        layout.addWidget(self.search_bar)

        # Create log level filter
        self.log_level_filter = QComboBox()
        self.log_level_filter.addItems(["All", "INFO", "WARNING", "ERROR"])
        layout.addWidget(self.log_level_filter)

        # Create log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        layout.addWidget(self.log_display)

        # Create clear logs button
        self.clear_button = QPushButton("Clear Logs")
        self.clear_button.clicked.connect(self.clear_logs)
        layout.addWidget(self.clear_button)

        # Connect search bar and log level filter to update logs
        self.search_bar.textChanged.connect(self.filter_logs)
        self.log_level_filter.currentTextChanged.connect(self.filter_logs)

        # Store all logs
        self.logs = self.get_all_logs()

    def append_log(self, level, message):
        # Add log with level and message
        color = {
            "INFO": QColor("blue"),
            "WARNING": QColor("orange"),
            "ERROR": QColor("red")
        }.get(level, QColor("black"))
        formatted_message = f"[{level}] {message}"
        self.logs.append({"level": level, "message": message})
        self.display_logs()

    def filter_logs(self):
        # Display filtered logs
        self.display_logs()

    def display_logs(self):
        # Clear current display
        self.log_display.clear()

        # Implement filtering based on search and log level
        search_text = self.search_bar.text().lower()
        log_level = self.log_level_filter.currentText()

        # Filter and display logs
        for log in self.logs:
            if (search_text in log['message'].lower()) and (log_level == "All" or log['level'] == log_level):
                color = {
                    "INFO": QColor("blue"),
                    "WARNING": QColor("orange"),
                    "ERROR": QColor("red")
                }.get(log['level'], QColor("black"))
                formatted_message = f"[{log['level']}] {log['message']}"
                self.log_display.append(f'<font color="{color.name()}">{formatted_message}</font>')

    def clear_logs(self):
        # Clear the log display and logs list
        self.log_display.clear()
        self.logs = []

    def get_all_logs(self):
        # Placeholder function to return all logs
        # You should replace this with the actual method to retrieve logs
        return [
            {"level": "INFO", "message": "Server started"},
            {"level": "ERROR", "message": "Failed to connect"}
        ]
