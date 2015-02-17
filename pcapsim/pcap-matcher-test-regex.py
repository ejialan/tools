#!/usr/bin/env python

import unittest
from scapy.all import *
from scapy.utils import rdpcap
from pcap.matcher import *

protocol = __import__('pcap.regex', fromlist=['*'])

class TestPcapMatcher(unittest.TestCase):
  def setUp(self):
    c = "192.168.56.100"
    s = "150.236.225.96"
    cp = 52962
    sp = 5000

    pc = IP(src=c,dst=s)/TCP(sport=cp,dport=sp)
    ps = IP(src=s,dst=c)/TCP(sport=sp,dport=cp)
    c_ack = IP(src=c,dst=s)/TCP(sport=cp,dport=sp,flags="A")
    s_ack = IP(src=s,dst=c)/TCP(sport=sp,dport=cp,flags="A")
    
    self.req_load="GET /demo/real_data.js HTTP/1.1\r\nHost: 150.236.225.94\r\n\r\n<soapenv:Envelope><soapenv:Header><cai3:SessionId>a8c00401a8c00401000000001423682236048</cai3:SessionId></soapenv:Header><soapenv:Body></soapenv:Body></soapenv:Envelope>"
    self.res_load="HTTP/1.1 200 OK\r\nServer: Apache/2.4.10 (Ubuntu)\r\nContent-Type: application/javascript\r\n\r\n<s:Envelope><S:Header><SessionId xmlns=\"http://schemas.ericsson.com/cai3g1.2/\">a8c00401a8c00401000000001423682236048</SessionId></S:Header><S:Body></S:Body></S:Envelope>" 

    '''cai3g request, session id is a8c02601a8c02601000000001423799300048'''
    pkts = [pc/self.req_load,
            ps/self.res_load
           ]
    self.conf = {'address':s, 'port':sp, 'protocol':'regex'}
    self.matcher = PcapMatcher(pkts, self.conf, protocol) 

  def test_match(self):
    '''cai3g request, session id is a8c02601a8c02601000000001423799968050'''
    recevied=self.req_load.replace("150.236.225.94", "10.170.31.213").replace("a8c02601a8c02601000000001423799300048", "a8c02601a8c02601000000001423799968050")
    expected_res=self.res_load
    pkt=IP(src='192.56.118.76', dst=self.conf['address'])/TCP(sport=1234, dport=self.conf['port'])/recevied
    res=self.matcher.match(pkt)
    self.assertEqual(1, len(res))
    self.assertEqual(expected_res, res[0].load)

if __name__ == '__main__':
  unittest.main()
