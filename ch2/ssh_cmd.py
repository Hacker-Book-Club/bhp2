import paramiko

# 1) make connection to an SSH server and runs a single command.
def ssh_command(ip, port, user, passwd, cmd):
    client = paramiko.SSHClient()
    # 2) Setting the policy to accept the SSH key for the server being connected to.
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port=port, username=user, password=passwd)

    # 3) After connected, run command. print each line of output.
    _, stdout, stderr = client.exec_command(cmd)
    output = stdout.readlines() + stderr.readlines()
    if output:
        print('--- Output ---')
        for line in output:
            print(line.strip())

if __name__ == '__main__':
    # 4) helps get username/password from the current environment.
    import getpass
    # user = getpass.getuser()
    user = input('Username: ')
    password = getpass.getpass()

    ip = input('Enter server IP: ') or '192.168.1.203'
    port = input('Enter port or <CR>: ') or 2222
    cmd = input('Enter command or <CR>: ') or 'id'
    # 5) Get IP, Port, and Command to send.
    ssh_command(ip, port, user, password, cmd)