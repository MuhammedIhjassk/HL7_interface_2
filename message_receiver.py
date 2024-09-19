from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QComboBox, QLineEdit, QFileDialog

class MessageReceiverTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        # Add filter for message type
        self.filter_box = QComboBox()
        self.filter_box.addItems(["All", "ADT", "ORM", "ORU"])
        self.filter_box.currentIndexChanged.connect(self.filter_messages)

        # Add search bar for content search
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search messages...")
        self.search_bar.textChanged.connect(self.search_messages)

        layout.addWidget(self.filter_box)
        layout.addWidget(self.search_bar)

        # Display for received messages
        self.received_message_display = QTextEdit()
        self.received_message_display.setPlaceholderText("Received HL7 Messages will appear here")
        layout.addWidget(self.received_message_display)

        self.setLayout(layout)

        # Store messages
        self.messages = []

        # Define the path for the auto-save file
        self.auto_save_path = 'HL7_messages.hl7'

        # load and display auto-saved messages
        self.load_auto_saved_messages()

    def add_message(self, message, acknowledgment=None):
        # Store messages and update display
        self.messages.append((message, acknowledgment))
        self.update_display()
        self.auto_save_messages()  # Automatically save messages after adding

    def filter_messages(self):
        self.update_display()

    def search_messages(self):
        self.update_display()

    def update_display(self):
        self.received_message_display.clear()
        filter_type = self.filter_box.currentText()
        search_query = self.search_bar.text().lower()

        for message, acknowledgment in self.messages:
            if filter_type != "All" and filter_type not in message:
                continue
            if search_query and search_query not in message.lower():
                continue
            
            self.received_message_display.append(f"Received HL7 Message:\n{message}\n")
            if acknowledgment:
                self.received_message_display.append(f"Acknowledgment:\n{acknowledgment}\n")
            self.received_message_display.append("\n" + "="*40 + "\n")  # Separator for different messages

    def auto_save_messages(self):
        # Automatically save messages to the defined file path
        try:
            # Get the text from QTextEdit widget
            text_to_save = self.received_message_display.toPlainText()

            # Write the text to the auto-save file
            with open(self.auto_save_path, 'w') as file:
                file.write(text_to_save)
                
            print(f"Messages automatically saved to {self.auto_save_path}")
        except Exception as e:
            print(f"Failed to automatically save messages: {e}")

    # add save as method as needed
    def save_messages_as(self):
        # Allow the user to manually save messages to a chosen file path
        try:
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Messages As", "", "HL7 Files (*.hl7);;All Files (*)", options=options)
            
            if file_path:
                # Get the text from QTextEdit widget
                text_to_save = self.received_message_display.toPlainText()

                # Write the text to the chosen file path
                with open(file_path, 'w') as file:
                    file.write(text_to_save)
                
                print(f"Messages manually saved to {file_path}")
        except Exception as e:
            print(f"Failed to manually save messages: {e}")

    def load_auto_saved_messages(self):
        # Load and display messages from the auto-save file
        try:
            with open(self.auto_save_path, 'r') as file:
                saved_text = file.read()
                self.received_message_display.setPlainText(saved_text)
            
            print(f"Loaded messages from {self.auto_save_path}")
        except FileNotFoundError:
            print(f"No auto-save file found at {self.auto_save_path}")
        except Exception as e:
            print(f"Failed to load messages: {e}")