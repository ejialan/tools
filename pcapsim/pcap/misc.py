from scapy.all import *

tcp_flag_vals = {"F":0x1, "S":0x2, "R":0x4, "P":0x8,
                                  "A":0x10, "U":0x20, "E":0x40, "C":0x80 }


def has_load(pkt):
    return hasattr(pkt, 'load')

def has_same_load(pkt, load):
    if hasattr(pkt, 'load'):
        #print "'%s' -- '%s', %r" % (pkt.load, load, pkt.load == load)
        #print repr(pkt.load), repr(load)
        return pkt.load == load
    else :
        return False

def is_ack(pkt):
    return pkt[TCP].flags == tcp_flag_vals["A"]

def same_direction(p1, p2):
    return (p1[IP].dst == p2[IP].dst and
           p1[IP].src == p2[IP].src and
           p1[TCP].sport == p2[TCP].sport and
           p1[TCP].dport == p2[TCP].dport)

