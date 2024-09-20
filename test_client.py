import socket
import logging

START_BLOCK = b'\x0b'
END_BLOCK = b'\x1c'
CARRIAGE_RETURN = b'\x0d'

# configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

hl7_message = "MSH|^~\\&|SendingApp|SendingFac|||202301011230||ADT^A01|12345|P|2.3\rPID|1||123456||Doe^John\r"


def send_hl7_message(ip, port, message):
    try:
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Connect to the server
        server_address = (ip, port)
        logging.info(f"Connecting to {ip}:{port}")
        sock.connect(server_address)

        try:
            # Wrap the HL7 message in MLLP format
            wrapped_message = START_BLOCK + message.encode('utf-8') + END_BLOCK + CARRIAGE_RETURN
            logging.info(f"Sending HL7 message:\n{hl7_message}")
            
            # Send the HL7 message
            sock.sendall(wrapped_message)

            # Wait for the server to respond with an ACK message
            data = sock.recv(1024)  # Buffer size of 1024 bytes, adjust as needed
            if data:
                # Process the received message to remove MLLP framing
                ack_message = process_mllp_ack(data)
                if ack_message:
                    logging.info(f"ACK message received:\n{ack_message}")
                    return ack_message
                else:
                    logging.error("Failed to process ACK message")
                    return None
            else:
                logging.error("No response from server")
                return None

        finally:
            # Close the socket connection
            logging.info("Closing connection")
            sock.close()

    except socket.error as e:
        logging.error(f"Socket error: {e}")
        return None

def process_mllp_ack(data):
    """
    Process the received MLLP-encoded ACK message from the server.
    
    :param data: The raw data received from the server.
    :return: The extracted HL7 ACK message as a string.
    """
    if data.startswith(START_BLOCK) and data.endswith(END_BLOCK + CARRIAGE_RETURN):
        # Remove the MLLP framing
        hl7_ack_message = data[len(START_BLOCK):-len(END_BLOCK + CARRIAGE_RETURN)]
        try:
            # Decode the ACK message from bytes to a string
            return hl7_ack_message.decode('utf-8')
        except UnicodeDecodeError:
            logging.error("Failed to decode the ACK message. Invalid encoding.")
            return None
    else:
        logging.error("Invalid MLLP message framing")
        return None    

# Send message to the HL7 server
send_hl7_message("127.0.0.1", 5000, hl7_message)
