import ipaddress
import struct

class IP:
    def __init__(self, buff=None):
        header = struct.unpack('<BBHHHBBH4s4s', buff)
        # 1) 4 bit rightward shift! 10000 >> 4 == 00001
        self.ver = header[0] >> 4
        # 2) To get the second nybble of a byte use the boolean AND operator with 0xF (00001111)
        self.ihl = header[0] & 0xF

        self.tos = header[1]
        self.len = header[2]
        self.id = header[3]
        self.offset = header[4]
        self.ttl = header[5]
        self.protocol_num = header[6]
        self.sum = header[7]
        self.src = header[8]
        self.dst = header[9]

        # human readable IP addresses
        self.src_address = ipaddress.ip_address(self.src)
        self.dst_address = ipaddress.ip_address(self.dst)

        # map protocol constants to their name
        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}
        

class ICMP:
    def __init__(self, buff):
        header = struct.unpack('<BBHHH', buff)
        self.type = header[0]
        self.code = header[1]
        self.sum = header[2]
        self.id = header[3]
        self.seq = header[4]
        mypacket = IP(buff)
        print(f'{mypacket.src_address} -> {mypacket.dst_address}')

