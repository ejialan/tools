from regex import *
print 'init cai3g protocol'

cai3g_pattern = '''{
            "match" : ".*\\r\\n\\r\\n.*<soapenv:Body>(.*)",
            "adjust" : [["essionId>([0-9a-z]*)<", "essionId[^>]*>([0-9a-z]*)<"]]
           }'''
config(cai3g_pattern)

