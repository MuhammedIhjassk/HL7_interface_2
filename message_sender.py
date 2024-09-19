import json
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QTextEdit, QMessageBox
from hl7_server import HL7hie # Assuming you have HL7hie implemented

class MessageSenderTab(QWidget):
    def __init__(self, server, parent=None):
        super().__init__(parent)
        self.server = server

        layout = QVBoxLayout()

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Enter HL7 Message")
        self.send_button = QPushButton("Send Message")
        self.response_display = QTextEdit()
        self.response_display.setReadOnly(True)

        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Enter Server IP")
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Enter Port")

        # Save button
        self.save_button = QPushButton("Save Settings")

        layout.addWidget(self.message_input)
        layout.addWidget(self.send_button)
        layout.addWidget(self.response_display)
        layout.addWidget(self.ip_input)
        layout.addWidget(self.port_input)
        layout.addWidget(self.save_button)

      
        self.setLayout(layout)

        self.send_button.clicked.connect(self.send_message)
        self.save_button.clicked.connect(self.save_settings)

    def validate_ip(self, ip):
        parts = ip.split(".")
        return len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)

    def validate_port(self, port):
        return port.isdigit() and 0 <= int(port) <= 65535

    def save_settings(self):
        ip = self.ip_input.text()
        port = self.port_input.text()

        if not self.validate_ip(ip):
            QMessageBox.warning(self, "Invalid IP", "Please enter a valid IP address.")
            return

        if not self.validate_port(port):
            QMessageBox.warning(self, "Invalid Port", "Please enter a valid port number (0-65535).")
            return

        settings = {"ip": ip, "port": port}
        with open("settings.json", "w") as file:
            json.dump(settings, file)

        QMessageBox.information(self, "Settings Saved", "IP and Port settings have been saved.")

    def load_settings(self):
        try:
            with open("settings.json", "r") as file:
                settings = json.load(file)
                self.ip_input.setText(settings.get("ip", ""))
                self.port_input.setText(settings.get("port", ""))
        except FileNotFoundError:
            pass    

    def get_server_info(self):
        try:
            with open("settings.json", "r") as file:
                settings = json.load(file)
                return settings.get("ip"), settings.get("port")
        except FileNotFoundError:
            QMessageBox.warning(self, "Settings Not Found", "Please configure the settings first.")
            return None, None

    def send_message(self):
        # ip, port = self.get_server()
        # if ip is None or port is None:
        #     return

        # message = self.message_input.text()
        # if not message:
        #     QMessageBox.warning(self, "Empty Message", "Please enter an HL7 message to send.")
        #     return

        # server = HL7hie(ip, int(port))
        # response = server.send_message(message)
        # self.response_display.setText(f"Response:\n{response}")
        pass # remove the pass when uncommenting the functions
