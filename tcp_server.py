import logging
from PyQt5.QtNetwork import QTcpServer, QTcpSocket, QHostAddress
from PyQt5.QtCore import QObject, pyqtSignal

START_BLOCK = b'\x0b'  # MLLP Start Block
END_BLOCK = b'\x1c'    # MLLP End Block
CARRIAGE_RETURN = b'\x0d'  # Carriage return

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class HL7Server(QObject):
    message_received = pyqtSignal(str)
    status_changed = pyqtSignal(str)

    def __init__(self, ip='127.0.0.1', port=5000):
        super().__init__()
        self.server = QTcpServer(self)
        self.server.newConnection.connect(self.handle_new_connection)
        
        self.ip = ip
        self.port = port

    def start_server(self):
        # Convert the IP string to a QHostAddress
        address = QHostAddress(self.ip)
        if self.server.listen(address, self.port):
        
            logging.info(f"Server started at {self.ip}:{self.port}")
            print(f"Server started at {self.ip}:{self.port}")
            self.status_changed.emit("Running")
        else:
            logging.error(f"Server failed to start: {self.server.errorString()}")
            print(f"Server failed to start: {self.server.errorString()}")

    def stop_server(self):
        if self.server.isListening():
            self.server.close()
            
            logging.info("Server stopped")
            print("Server stopped")
            self.status_changed.emit("Down")

    def is_listening(self):
        return self.server.isListening()

    def handle_new_connection(self):
        client_connection = self.server.nextPendingConnection()
        client_connection.readyRead.connect(lambda: self.read_data(client_connection))
        logging.info(f"New connection from {client_connection.peerAddress().toString()}")
    


    def read_data(self, connection):
        while connection.bytesAvailable():
            data = connection.readAll()
            message = self.process_mllp_message(data)
            if message:
                self.message_received.emit(message)  # Emit the signal with the message content
                logging.info(f"HL7 message received: {message}")

                # Send HL7 acknowledgment (ACK) back to the client
                ack_message = self.create_ack_message(message)
                self.send_ack(connection, ack_message)

    def process_mllp_message(self, data):
        # Extract the message by removing MLLP framing
        if data.startsWith(START_BLOCK) and data.endsWith(END_BLOCK + CARRIAGE_RETURN):
            hl7_message = data[len(START_BLOCK):-len(END_BLOCK + CARRIAGE_RETURN)]
            try:
                return hl7_message.data().decode('utf-8')
            except UnicodeDecodeError:
                logging.error("Failed to decode HL7 message. Invalid encoding.")
                return None
        else:
            logging.warning("Invalid MLLP message framing")
            return None

    def create_ack_message(self, message):
        try:
            # Parse the original message and create an HL7 acknowledgment (ACK)
            msh_fields = message.split('|')
            control_id = msh_fields[9]  # Control ID from MSH segment
            return f"MSH|^~\\&|ACK|||||ACK|{control_id}|ACK"
        except (IndexError, ValueError) as e:
            logging.error(f"Error parsing MSH segment: {e}")
            return None

    def send_ack(self, connection, ack_message):
        if ack_message:
            # Wrap ACK message in MLLP format
            ack = START_BLOCK + ack_message.encode('utf-8') + END_BLOCK + CARRIAGE_RETURN
            connection.write(ack)
            connection.flush()
            logging.info(f"ACK sent: {ack_message}")

            connection.disconnectFromHost()
            if connection.state() == QTcpSocket.UnconnectedState:
                logging.info("Connection closed successfully.")
            else:
                logging.warning("Client failed to disconnect properly.")
    
   