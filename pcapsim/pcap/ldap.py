from misc import has_same_load

print 'init ldap protocol'

'''
The payload of a ldap request is encoded using Basic Encoding Rule (BER).
Refer rfc4511 for the ldap protocol.
http://tools.ietf.org/html/rfc4511


'''
def match(pkt, load):
  if hasattr(pkt, 'load'):
    return pkt.load[10:] == load[10:]
  
def adjust(pkt, res):
  [tag, length, value]=ber_decode(pkt.load)
  print 'tag', repr(tag)
  print 'length', repr(length)
  print 'value', repr(value)
  message_id_index = len(tag) + len(length)

  [tag, length, value]=ber_decode(value)
  print 'tag', repr(tag)
  print 'length', repr(length)
  print 'value', repr(value)
  message_id_len = len(tag) + len(length) + len(value)
  
  '''
  here do not handle the case that nubmer of byte of the message id is different 
  '''
  load = res[0].load
  load = load[0:message_id_index] + tag + length + value + load[message_id_index+message_id_len:]
  res[0].load = load
  return res


def ber_decode(load):
  'assume the tag of ldap message is one byte'
  tag=load[0]

  #indefinite length
  if 0x80 == ord(load[1]):
    length = load[1] 
    value = load[2:]
  #short definite length
  elif 0x00 == (ord(load[1]) & 0x80):
    length = load[1]
    len = ord(load[1]) & 0x7F
    value = load[2 : 2+len]
  #long definite length
  else:
    nb_of_length = ord(load[1]) & 0x80
    length = load[1,2+nb_of_length]
    '''
    do not handle the long definite length properly because I  
    want to only extract the message id which shall not be so long.
    '''
    value = load[2+nb_of_length:]

  return [tag, length, value]
  
