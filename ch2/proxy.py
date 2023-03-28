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

def request_handle(buffer):
    # perform packet modification
    return cmd_buffer

def respone_handler(buffer):
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

            local_buffer = request_handles(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote".)

        remote_buffer = request_handler(local_buffer)
        if len(remote_buffer):
            print("[==>] Received %d bytes from remote." % len(remote_buffer))
            hexdump(remote_buffer)

            remote_buffer = response_handler(remote_buffer):
            client_socket.send(remote_buffer)
            print("[<==] Sent to localhost.")

        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connection.")
            break

## TODO: Pg23 -> server_loop function