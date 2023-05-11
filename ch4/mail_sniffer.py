from scapy.all import sniff

# 1) We start by defining the callback function that will receive each sniffed packet
def packet_callback(packet):
    print(packet.show())

def main():
    # 2) then tell Scapy to start sniffing on all interfaces with no filtering 
    sniff(prn=packet_callback, count=1)

if __name__ == '__main__':
    main()