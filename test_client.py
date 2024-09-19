import socket

START_BLOCK = b'\x0b'
END_BLOCK = b'\x1c'
CARRIAGE_RETURN = b'\x0d'

hl7_message = "MSH|^~\\&|LAB|1234||20210924120000||ORM^O01|MSG001|P|2.5\rPID|1||123456||Doe^John\r"

def send_hl7_message(ip, port, message):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, port))
    
    mllp_message = START_BLOCK + message.encode() + END_BLOCK + CARRIAGE_RETURN
    client_socket.sendall(mllp_message)

    # Receive ACK
    ack = client_socket.recv(1024)
    print(f"ACK received:\n{ack.decode()}")

    client_socket.close()

# Send message to the HL7 server
send_hl7_message("127.0.0.1", 5000, hl7_message)
