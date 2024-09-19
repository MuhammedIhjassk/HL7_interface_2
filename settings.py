from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import QTimer

class SettingsTab(QWidget):
    def __init__(self, server, parent=None):
        super().__init__(parent)
        self.server = server
        
        layout = QVBoxLayout()

        # Input fields for IP and Port
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Enter Server IP")
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Enter Port")
        
        # Save button
        self.save_button = QPushButton("Save Settings")

        # Start and Stop buttons
        self.start_button = QPushButton("Start Server")
        self.stop_button = QPushButton("Stop Server")


        # Add widgets to layout
      
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)

        # Connect buttons to their respective methods

        self.start_button.clicked.connect(self.start_server)
        self.stop_button.clicked.connect(self.stop_server)


        self.timer = QTimer()
        self.timer.setSingleShot(True)  # Run the timer only once
        self.timer.timeout.connect(self.start_server)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.timer.start(3000)  # 3000 milliseconds = 3 seconds

    def start_server(self):
        """Start the HL7 server."""
        self.server.start_server()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)


    def stop_server(self):
        """Stop the HL7 server."""
        self.server.stop_server()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
