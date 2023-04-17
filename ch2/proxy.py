import sys
import socket
import threading

HEX_FILTER = ''.join([(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)])

# hexdump function: input bytes -> prints to console
def hexdump(src, length=16, show=True):
    # decode if byte string exists
    if isinstance(src, bytes):
        src = src.decode()
    
    results = list()
    for i in range(0, len(src), length):
        # take a piece of the hex string; put it in the word var
        word = str(src[i:i+length])

        # From not-printable to printable
        printable = word.translate(HEX_FILTER)
        hexa = ' '.join([f'{ord(c):02X}' for c in word])
        hexwidth = length*3
        # Array for holding the output string
        results.append(f'{i:04x} {hexa:<{hexwidth}} {printable}')
    if show:
        for line in results:
            print(line)
    else:
        return results

def receive_from(connection):
    buffer = b""
    # setting properties for the socket; going to store output in buffer string above
    connection.settimeout(5)
    try:
        while True:
            # loop listening for data, putting it together in the buffer
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except Exception as e:
        pass
    return buffer

def request_handler(buffer):
    # perform packet modification
    return buffer

def response_handler(buffer):
    # perform packet modification
    return buffer

def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Create socket and connect to the remote host
    remote_socket.connect((remote_host, remote_port))

    # check for connection establishment
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

    # send the contents of the remote_buffer to the response_handler function and save the manipulated traffic
    remote_buffer = response_handler(remote_buffer)
    if len(remote_buffer):
        print("[<==] Sending %d bytes to localhost." % len(remote_buffer))
        client_socket.send(remote_buffer)
    
    while True:
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            line = "[==>]Received %d bytes from localhost." % len(remote_buffer)
            print(line)
            hexdump(local_buffer)

            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote")

        remote_buffer = request_handler(local_buffer)
        if len(remote_buffer):
            print("[==>] Received %d bytes from remote." % len(remote_buffer))
            hexdump(remote_buffer)

            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<==] Sent to localhost.")

        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connection.")
            break

def server_loop(local_host, local_port,
                remote_host, remote_port, receive_first):
    # 1) Creating a socket for the server_loop function
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # 2) Bind to local host and listen on the port
        server.bind((local_host, local_port))
    except Exception as e:
        print("problem on bind: %r" % e)
        
        print("[!!] Failed to list on %s:%d" % (local_host, local_port))
        print("[!!] Check for other listening sockets or correct permissions.")
        sys.exit(0)
    print("[*] Listening on %s:%d" % (local_host, local_port))
    server.listen(5)
    # 3) Main loop! - When incoming connection request, hand off to proxy_handler in a new thread.
    while True:
        client_socket, addr = server.accept()
        # print out the local connection information
        line = "> Received incoming connection from %s:%d" % (addr[0], addr[1])
        print(line)
        # start a thread to talk to the remote host
        # 4) sending and receving of bit to either side of the data stream is handled in the threads generated.
        proxy_thread = threading.Thread(
            target=proxy_handler,
            args=(client_socket, remote_host,
            remote_port, receive_first))
        proxy_thread.start()
    
def main():
    if len(sys.argv[1:]) != 5:
        print("Usage: ./proxy.py [localhost] [localport]", end='')
        print("[remotehost] [remoteport] [receive_first]")
        print("Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    
    receive_first = sys.argv[5]
    
    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False
    
    server_loop(local_host, local_port,
        remote_host, remote_port, receive_first)
    
if __name__ == '__main__':
    main()