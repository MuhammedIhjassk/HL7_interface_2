import socket

class HL7hie:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def send_message(self, message):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.ip, self.port))
                s.sendall(message.encode('utf-8'))
                response = s.recv(1024).decode('utf-8')
                return response
        except Exception as e:
            return f"Error: {e}"
