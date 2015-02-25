import re, ast
print 'init regualr expression based protocol'

match_pattern = None
adjust_patterns = []

def match(pkt, load):
  if hasattr(pkt, 'load'):
    m_pcap = match_pattern.match(pkt.load)
    m_recv = match_pattern.match(load)
    if m_pcap and m_recv and m_pcap.groups() == m_recv.groups():
      return True
       
  return False

def adjust(recv_pkt, resp):
  #print "load of recevied packet", recv_pkt.load
  return [ adjust_resp(recv_pkt, x) for x in resp ]


def adjust_resp(recv_pkt, resp):
  for ps in adjust_patterns:
    #print ps[0].pattern, ps[1].pattern
    m_recv = ps[0].search(recv_pkt.load)
    m_resp = ps[1].search(resp.load)
    if m_recv and m_resp:
       #print m_resp.group(1), m_recv.group(1)
       resp.load = resp.load.replace(m_resp.group(1), m_recv.group(1))
  return resp

def config(conf_str):
  global match_pattern
  global adjust_patterns
  print 'configure regular expression based protocol:', conf_str
  conf = ast.literal_eval(conf_str)
  match_pattern = re.compile(conf['match'], re.M|re.S)
  if conf['adjust'] is not None:
    adjust_patterns = [ [re.compile(ad[0], re.M|re.S), re.compile(ad[1], re.M|re.S)] for ad in conf['adjust'] ]
    

