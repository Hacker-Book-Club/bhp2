import ipaddress
import os
import socket
import struct
import sys
import threading
import time

from ctypes import *

# subnet to scan for live hosts
SUBNET = "192.168.1.0/24"
# magic string we'll check ICMP responses for
MESSAGE = "PYTHONRULES!"

# host to listen on
host = "192.168.1.108"


class IP(Structure):
    _fields_ = [
        ("ihl", c_ubyte, 4),
        ("version", c_ubyte, 4),
        ("tos", c_ubyte),
        ("len", c_ushort),
        ("id", c_ushort),
        ("offset", c_ushort),
        ("ttl", c_ubyte),
        ("protocol_num", c_ubyte),
        ("sum", c_ushort),
        ("src", c_uint32),
        ("dst", c_uint32),
    ]

    def __new__(cls, socket_buffer=None):
        return cls.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):
        self.socket_buffer = socket_buffer

        # map protocol constants to their names
        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}

        # human readable IP addresses
        self.src_address = socket.inet_ntoa(struct.pack("@I", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("@I", self.dst))

        # human readable protocol
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except IndexError:
            self.protocol = str(self.protocol_num)


# 1) This is creating the structure of our ICMP traffic.
class ICMP(Structure):
    _fields_ = [
        ("type", c_ubyte),
        ("code", c_ubyte),
        ("checksum", c_ushort),
        ("unused", c_ushort),
        ("next_hop_mtu", c_ushort),
    ]

    def __new__(cls, socket_buffer):
        return cls.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer):
        self.socket_buffer = socket_buffer


# this sprays out UDP datagrams with our magic message.
def udp_sender():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
        for ip in ipaddress.ip_network(SUBNET).hosts():
            sender.sendto(bytes(MESSAGE, "utf8"), (str(ip), 65212))


class Scanner:
    def __init__(self, host):
        self.host = host

        # create a raw socket and bind it to the public interface
        if os.name == "nt":
            socket_protocol = socket.IPPROTO_IP
        else:
            socket_protocol = socket.IPPROTO_ICMP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
        self.socket.bind((host, 0))

        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        # if we're on Windows we need to send some ioctl
        # to setup promiscuous mode
        if os.name == "nt":
            self.socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    def sniff(self):
        hosts_up = set([f"{str(self.host)} *"])
        try:
            while True:
                # read a packet
                raw_buffer = self.socket.recvfrom(65535)[0]
                # create an IP header from the first 20 bytes
                ip_header = IP(raw_buffer[0:20])
                # 2) if it's ICMP we want it
                if ip_header.protocol == "ICMP":
                    # 3) calculate where our ICMP packet starts
                    offset = ip_header.ihl * 4
                    buf = raw_buffer[offset : offset + sizeof(ICMP)]
                    # 4) create our ICMP structure
                    icmp_header = ICMP(buf)
                    # check for TYPE 3 and CODE
                    if icmp_header.code == 3 and icmp_header.type == 3:
                        if ipaddress.ip_address(
                            ip_header.src_address
                        ) in ipaddress.IPv4Network(SUBNET):
                            # make sureit has our magic message
                            if raw_buffer[len(raw_buffer) - len(MESSAGE) :] == bytes(
                                MESSAGE, "utf8"
                            ):
                                tgt = str(ip_header.src_address)
                                if tgt != self.host and tgt not in hosts_up:
                                    hosts_up.add(str(ip_header.src_address))
                                    # If all the checks pass then we print out that host's content
                                    print(f"Host Up: {tgt}")
        # this is an interrupt CTRL-C
        except KeyboardInterrupt:
            # if we're on Windows turn off promiscuous mode
            if os.name == "nt":
                self.socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
            print("\nUser interrupted.")
            if hosts_up:
                print(f"\n\nSummary: Hosts up on {SUBNET}")
            for host in sorted(hosts_up):
                print(f"{host}")
            print("")
            sys.exit()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        host = sys.argv[1]
    else:
        host = "192.168.1.108"
    s = Scanner(host)
    time.sleep(5)
    # Set up scan,s sleep, sniff.
    t = threading.Thread(target=udp_sender)
    t.start()
    s.sniff()
