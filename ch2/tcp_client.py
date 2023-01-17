import socket

target_host = "127.0.0.1"
target_port = 9998

# 1) create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 2) connect the client
client.connect((target_host,target_port))

# 3) send some data
client.send(b"ABCDEF\r\n\r\n")

# 4) receive some data
response = client.recv(4096)

print(response.decode())
client.close()
