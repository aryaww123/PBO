import socket
import threading

class Server:
    def __init__(self, host, port):
        self.HOST = host
        self.PORT = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.HOST, self.PORT))
        self.server.listen()
        self.clients = []

    def start(self):
        print("Server running...")
        while True:
            client, address = self.server.accept()
            print(f"Connected with {str(address)}!")
            client.send("NICK".encode('utf-8'))

            nickname = client.recv(1024)
            self.clients.append((client, nickname.decode('utf-8')))
            print(f"Nickname of the client is {nickname.decode('utf-8')}")
            self.broadcast(f"\n {nickname.decode('utf-8')} connected to the server!\n\n".encode('utf-8'),client)
            # client.send("Connected to the server".encode('utf-8'))
            thread = threading.Thread(target=self.handle, args=(client,nickname))
            thread.start()

    def broadcast(self, message, client_sender=None):
        for client in self.clients:
            if client != client_sender:
                try:
                    client.send(message)
                except:
                    self.remove(client)

    def remove(self, client):
        if client in self.clients:
            self.clients.remove(client)

    def handle(self, client,nickname):
        while True:
            try:
                message = client.recv(1024)
                if message:
                    decoded_message = message.decode('utf-8')
                    print(decoded_message)
                    # print(message.decode('utf-8'))
                    # self.broadcast(message, client)
                    if decoded_message.startswith("ADD_USER"):
                        new_user=decoded_message.split()[1]
                        self.broadcast(f"\n {new_user} connected to the server!\n\n".encode('utf-8'),client)
                    else:
                        self.broadcast(message, client)
                else:
                    self.remove(client)
            except:
                self.remove(client)
                break

if __name__ == "__main__":
    HOST = '127.0.0.1'
    PORT = 9090
    server = Server(HOST, PORT)
    server.start()
