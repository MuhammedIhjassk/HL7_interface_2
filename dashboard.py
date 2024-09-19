from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class DashboardTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        # Engine status
        self.status_label = QLabel("HL7 Engine Status: Checking...")
        
        # Status indicator (could be a simple label or icon)
        self.status_indicator = QLabel()
        self.update_status("Checking")  # Initial status

        layout.addWidget(self.status_label)
        layout.addWidget(self.status_indicator)

        self.setLayout(layout)

    def update_status(self, status):
        # Update the status label
        self.status_label.setText(f"HL7 Engine Status: {status}")


        