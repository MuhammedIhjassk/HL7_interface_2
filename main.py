import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QPushButton, QTextEdit
from dashboard import DashboardTab
from message_sender import MessageSenderTab
from message_receiver import MessageReceiverTab
from log_viewer import LogViewerTab
from settings import SettingsTab
from tcp_server import HL7Server

class HL7IntegrationGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HL7 Integration System")
        self.setGeometry(200, 200, 800, 600)

        # Create a central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a vertical layout for the central widget
        layout = QVBoxLayout(central_widget)

        # Initialize HL7 server
        self.server = HL7Server()

        # integrate tcp listenner with main application to pass messages to message_receiver tab
        self.server.message_received.connect(self.received_message_display)
        self.server.status_changed.connect(self.update_status)

        # Create a tab widget and add it to the layout
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Create the individual tabs
        self.create_dashboard_tab()
        self.create_message_sender_tab()
        self.create_message_receiver_tab()
        self.create_log_viewer_tab()
        self.create_settings_tab()
        
      
    def create_dashboard_tab(self):
        self.dashboard_tab = DashboardTab()
        self.tabs.addTab(self.dashboard_tab, "Dashboard")

    def create_message_sender_tab(self):
        self.message_sender_tab = MessageSenderTab(self.server)
        self.tabs.addTab(self.message_sender_tab, "Send Message")

    def create_message_receiver_tab(self):
        self.message_receiver_tab = MessageReceiverTab()
        self.tabs.addTab(self.message_receiver_tab, "Received Messages")

    def create_log_viewer_tab(self):
        self.log_viewer_tab = LogViewerTab()
        self.tabs.addTab(self.log_viewer_tab, "Logs")

    def create_settings_tab(self):
        self.settings_tab = SettingsTab(self.server)
        self.tabs.addTab(self.settings_tab, "Settings")
 

    def update_status(self, status_message):
        self.dashboard_tab.update_status(status_message)

    def received_message_display(self, message):
        self.message_receiver_tab.add_message(message)

    def add_log_entry(self, entry):
        self.log_viewer_tab.add_log_entry(entry)  

    def closeEvent(self, event):
        if self.server.is_listening():
            self.server.stop_server()
        event.accept()    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HL7IntegrationGUI()
    window.show()
    sys.exit(app.exec_())   
