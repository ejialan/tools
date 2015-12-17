from scapy.all import *
import logging
from misc import *

class PcapMatcher:
  def __init__(self, pkts, conf, protocol):
    self.pkts = pkts
    #print '__init__', len(pkts)
    self.conf = conf;
    self.peers = {}
    self.protocol = protocol

  def send_to_me(self, p):
    return (p[IP].dst == self.conf['address'] and
            p[TCP].dport == self.conf['port'])

  def get_first_matched(self, pkts, p):
    for offset, pkt in enumerate(pkts):
      if self.send_to_me(pkt) and self.protocol.match(pkt, p.load):
        return offset
    return -1

  def get_first_send_to_me(self, pkts):
    for offset, pkt in enumerate(pkts):
        if self.send_to_me(pkt) and not is_ack(pkt) and has_load(pkt):
            #print pkt.show()
            return offset
    return len(pkts)

  def match(self, pkt):
    peer=(pkt[IP].src, pkt[TCP].sport)
    if hasattr(pkt, 'load'):
        #print "recieved pkt load" , repr(pkt.load)
        l_index = self.peers.get(peer, 0)
        if self.conf.get('wrap', False):
          l_index = l_index % len(self.pkts)
          pkts=self.pkts[l_index:]+self.pkts[0:l_index]
        else: 
          pkts=self.pkts[l_index:]

        begin = self.get_first_matched(pkts, pkt)
        if begin != -1:
          begin += 1
          end = begin + self.get_first_send_to_me(pkts[begin:]) 
          self.peers[peer] = l_index+end
          return self.protocol.adjust(pkt, filter(lambda pkt: not is_ack(pkt), pkts[begin:end]))
    return []
