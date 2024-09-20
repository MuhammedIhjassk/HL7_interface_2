import logging
from PyQt5.QtNetwork import QTcpServer, QTcpSocket, QHostAddress
from PyQt5.QtCore import QObject, pyqtSignal, QByteArray

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
            # Ensure `data` is in bytes
            if isinstance(data, QByteArray):
                data = data.data()  # Convert QByteArray to Python bytes
                logging.info(f"Received data type: {type(data)}")
            
            message = self.process_mllp_message(data)
            if message:
                self.message_received.emit(message)
                logging.info(f"HL7 message received: {message}")

                # Determine acknowledgment type based on message processing
                ack_type, error_details = self.process_message_for_ack(message)

                # Create the acknowledgment message
                ack_message = self.create_ack_message(message, ack_type, error_details)
                self.send_ack(connection, ack_message)

    def process_mllp_message(self, data):
        # Extract the message by removing MLLP framing
        if data.startswith(START_BLOCK) and data.endswith(END_BLOCK + CARRIAGE_RETURN):
            hl7_message = data[len(START_BLOCK):-len(END_BLOCK + CARRIAGE_RETURN)]
            try:
                # Decode bytes
                return hl7_message.decode('utf-8')
            except UnicodeDecodeError:
                logging.error("Failed to decode HL7 message. Invalid encoding.")
                return None
        else:
            logging.warning("Invalid MLLP message framing")
            return None    

    def process_message_for_ack(self, message):
        """
        Validates the HL7 message and determines the acknowledgment type.    

        :param message: The HL7 message as a string.
        :return: Tuple containing acknowledgment type ('AA', 'AE', 'AR') and error details (if any).
        """
        try:
            # Split the message into segments
            segments = message.strip().split('\r')
            if not segments:
                logging.error("No segments found in the message.")
                return 'AR', {'code': '100', 'description': 'Message is empty or improperly formatted.'}    

            # Extract the MSH segment
            msh_segment = next((seg for seg in segments if seg.startswith("MSH")), None)
            if not msh_segment:
                logging.error("MSH segment not found in the message.")
                return 'AR', {'code': '101', 'description': 'MSH segment is missing.'}    

            # Split MSH segment into fields
            msh_fields = msh_segment.split('|')
            if len(msh_fields) < 12:
                logging.error("MSH segment does not contain all required fields.")
                return 'AR', {'code': '102', 'description': 'MSH segment is incomplete.'}    

            # Extract necessary fields from MSH
            sending_app = msh_fields[2]
            sending_facility = msh_fields[3]
            receiving_app = msh_fields[4]
            receiving_facility = msh_fields[5]
            message_type = msh_fields[8]
            control_id = msh_fields[9]
            processing_id = msh_fields[10]
            version_id = msh_fields[11]    

            # Basic validation checks
            errors = []    

            # Check required MSH fields
            if not sending_app:
                errors.append({'code': '103', 'description': 'Sending Application is missing.'})
            if not sending_facility:
                errors.append({'code': '104', 'description': 'Sending Facility is missing.'})
            if not receiving_app:
                errors.append({'code': '105', 'description': 'Receiving Application is missing.'})
            if not receiving_facility:
                errors.append({'code': '106', 'description': 'Receiving Facility is missing.'})
            if not message_type:
                errors.append({'code': '107', 'description': 'Message Type is missing.'})
            if not control_id:
                errors.append({'code': '108', 'description': 'Message Control ID is missing.'})
            if not processing_id:
                errors.append({'code': '109', 'description': 'Processing ID is missing.'})
            if not version_id:
                errors.append({'code': '110', 'description': 'Version ID is missing.'})    

            # Validate message type
            valid_message_types = ['ADT^A01', 'ORM^O01', 'ORU^R01']  # Example valid types
            if message_type not in valid_message_types:
                errors.append({'code': '111', 'description': f'Unsupported Message Type: {message_type}.'})    

            # Additional validation can be added here for other segments (e.g., PID, PV1)    

            if errors:
                # Return AE acknowledgment with error details
                error_details = errors[0]  # Return the first error found
                return 'AE', error_details
            else:
                # All validations passed, return AA acknowledgment
                return 'AA', None    

        except Exception as e:
            logging.error(f"Exception during message validation: {e}")
            return 'AR', {'code': '999', 'description': 'Unexpected error during message validation.'}    
    

    def create_ack_message(self, message, ack_type='AA', error_details=None):
        """
        Create an HL7 acknowledgment message.
        
        :param message: The original HL7 message to acknowledge.
        :param ack_type: Type of acknowledgment ('AA', 'AE', 'AR').
        :param error_details: Dictionary containing error details for AE type.
        :return: Acknowledgment message as a string.
        """
        try:
            # Split the message into segments and validate
            segments = message.strip().split('\r')
            msh_segment = next((seg for seg in segments if seg.startswith("MSH")), None)
            if msh_segment is None:
                logging.error("MSH segment not found in the message")
                return None    

            msh_fields = msh_segment.split('|')
            if len(msh_fields) < 10:
                logging.error("Invalid MSH segment structure")
                return None    

            # Extract fields for ACK message
            sending_app = msh_fields[5]  # Original Receiving Application
            sending_facility = msh_fields[6]  # Original Receiving Facility
            receiving_app = msh_fields[3]  # Original Sending Application
            receiving_facility = msh_fields[4]  # Original Sending Facility
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            control_id = msh_fields[10]  # Message Control ID from MSH-10    

            # Create the MSH segment for ACK
            ack_msh_segment = (
                f"MSH|^~\\&|{sending_app}|{sending_facility}|{receiving_app}|{receiving_facility}|"
                f"{timestamp}||ACK|{control_id}|P|2.3"
            )    

            # Create the MSA segment
            msa_segment = f"MSA|{ack_type}|{control_id}"    

            ack_message = f"{ack_msh_segment}\r{msa_segment}"    

            # Include error details in the ERR segment if necessary
            if ack_type == 'AE' and error_details:
                error_code = error_details.get('code', '0000')
                error_description = error_details.get('description', 'Unknown error')
                err_segment = f"ERR|||{error_code}|E|||{error_description}"
                ack_message += f"\r{err_segment}"    

            return ack_message
        except Exception as e:
            logging.error(f"Error generating acknowledgment message: {e}")
            return None    


    def send_ack(self, connection, ack_message):
        if ack_message:
            logging.info(f"ACK Message being sent: {ack_message}")  # Log the ACK message content
            
            # Wrap ACK message in MLLP format
            ack = START_BLOCK + ack_message.encode('utf-8') + END_BLOCK + CARRIAGE_RETURN
            
            try:
                # Check connection state
                if connection.state() != QTcpSocket.ConnectedState:
                    logging.error("Connection is not in connected state.")
                    return    

                connection.write(ack)
                if connection.waitForBytesWritten(5000):
                    logging.info(f"ACK written to network successfully: {ack_message}")
                else:
                    logging.error("Failed to written ACK message within timeout.")
                connection.flush()
                logging.info(f"ACK flushed successfully: {ack_message}")

                
                # Wait until all the data is written to the network (timeout of 5000ms)
                # if connection.waitForBytesWritten(5000):
                #     logging.info(f"ACK sent successfully: {ack_message}")
                # else:
                #     logging.error("Failed to send ACK message within timeout.")
            
            except Exception as e:
                logging.error(f"Error sending ACK message: {e}")    

            # Connect the disconnected signal to log once the client disconnects
            connection.disconnected.connect(self.handle_disconnection)    

            # Request the client to disconnect
            connection.disconnectFromHost()
        else:
            logging.error("No ACK message to send")
        


    def handle_disconnection(self):
        logging.info("Client disconnected successfully.")
