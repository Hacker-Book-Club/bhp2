import socket
import threading

IP = '0.0.0.0'
PORT = 9998

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 1) IP and Port we want the server to listen on. [IP:Port listening... |} <- client requests]
    server.bind((IP, PORT))
    # 2) Listen |} <<<<<
    server.listen(5)
    print(f'[*] Listening on {IP}:{PORT}')
    
    while True:
        # 3) Client connection -> 
        #   socket = client var, remote conn details = address var
        client, address = server.accept()
        print(f'[*] Accepted connection from {address[0]}:{address[1]}')
        client_handler = threading.Thread(target=handle_client, args=(client,))
        # 4) Start thread to handle the client connection. Using the new object ^^^
        client_handler.start()

# 5) recv() msg and sends msg back
def handle_client(client_socket):
    with client_socket as sock:
        request = sock.recv(1024)
        print(f'[*] Received: {request.decode("utf-8")}')
        sock.send(b'ACK')


if __name__ == '__main__':
    main()
