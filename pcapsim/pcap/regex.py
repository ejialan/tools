import re
print 'init regualr express based protocol'

def match(pkt, load):
  if hasattr(pkt, 'load'):
    m_pcap = re.match('.*\r\n\r\n.*<soapenv:Body>(.*)', pkt.load, re.M|re.S)
    m_recv = re.match('.*\r\n\r\n.*<soapenv:Body>(.*)', load, re.M|re.S)
    if m_pcap and m_recv and m_pcap.groups() == m_recv.groups():
      return True
       
  return False

def adjust(matched_pkt, resp):
  return resp
