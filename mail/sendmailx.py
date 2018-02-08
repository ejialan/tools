#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
send or cancel meeting requst by batch

Usage: sendmailx [OPTIONS]
Options:
  -h, --help
    Help message
  -s, --mailserver
    SMTP server to send mail
  -p, --mailport
    SMTP server port
  -u, --user
    user name who sends the mail
  -f, --from 
    user name showed in the mail 
  -b, --batch
    batch csv file
  -d, --delete
    cance meeting request
  -o, --options
    load options from config file
  -e, --seed
    seed used to generate uid of meeting request
'''

SMTP_SERVER = ''
SMTP_PORT = 25
SMTP_USERNAME = ''
SMTP_PASSWORD = ''
SEED=''
METHOD='REQUEST'
batchfile=''

# Now construct the message
import smtplib, email
from email import encoders
from email.header import Header
import os,getopt,getpass,sys
from datetime import datetime
import icalendar
import pytz
import hashlib

def uid(str):
  print 'seed=', SEED
  return int(hashlib.sha1(str+SEED).hexdigest(), 16) % (10 ** 10)

#def sendmail(name, toList, start, end, uid):
def sendmail(organizer,location,starttime,endtime,to,attendees,subject,method):
	#tz = pytz.timezone("Asia/Shanghai")
	#start = tz.localize(start)
	#end = tz.localize(end)
        print "send mail to ", organizer,location,starttime,endtime,attendees,subject,to,method
	msg = email.MIMEMultipart.MIMEMultipart()
	
	#body = email.MIMEText.MIMEText(MESSAGE.replace('XX', name), 'html', 'utf-8')
	#msg.attach(body)

	#'''
        cal = icalendar.Calendar()
        cal.add('prodid', '-//My calendar application//example.com//')
        cal.add('version', '2.0')
        cal.add('method', method)
        event = icalendar.Event()
	attendees.append(to)
        for attendee in attendees:
          event.add('attendee', 'MAILTO:' + attendee)
        event.add('organizer', organizer)
        event.add('location', location)
        event.add('dtstart', datetime.strptime(starttime, "%Y.%m.%d %H:%M"))
        event.add('dtend', datetime.strptime(endtime, "%Y.%m.%d %H:%M"))
        event['uid'] = uid(organizer + location + starttime + to) # Generate some unique ID
        print 'uid=', event['uid']
        event.add('priority', 5)
        event.add('sequence', 1)
        event.add('created', datetime.now())

        alarm = icalendar.Alarm()
        alarm.add("action", "DISPLAY")
        alarm.add('description', "Reminder")
        #alarm.add("trigger", dt.timedelta(hours=-reminderHours))
        # The only way to convince Outlook to do it correctly
        alarm.add("TRIGGER;RELATED=START", "-PT{0}M".format(15))
        event.add_component(alarm)
        cal.add_component(event)

        filename = "invite.ics"
        part = email.MIMEBase.MIMEBase('text', "calendar", method=method, name=filename)
        part.set_payload( cal.to_ical() )
        email.Encoders.encode_base64(part)
        part.add_header('Content-Description', filename)
        part.add_header("Content-class", "urn:content-classes:calendarmessage")
        part.add_header("Filename", filename)
        part.add_header("Path", filename)
        msg.attach(part)

	msg.add_header('X-Priority', '1')
	msg.add_header('From', SMTP_USERNAME)
	msg.add_header('To', to)
	subject = Header(subject, 'utf-8')
	msg['Subject'] = subject

	# Now send the message
	mailer = smtplib.SMTP(SMTP_SERVER, int(SMTP_PORT))
	mailer.login(SMTP_USERNAME, SMTP_PASSWORD)
	mailer.sendmail(SMTP_USERNAME, attendees, msg.as_string())
	mailer.close()

def load(stream):
  data={}
  for line in stream:
    [n,v] = [x.strip() for x in line.split(':')]
    data[n] = v
  return data

header="organizer,location,subject,starttime,endtime,to,attendees"

def batchsend(file,method):
  with open (file, 'r') as f:
    lines = [x.strip() for x in f.readlines()]
  for line in lines:
    if(line == "" or line == None or line.startswith(header) or line.split(",")[0] == ""):
      continue    
    [organizer,location,subject,starttime,endtime,to,attendees]=line.split(",", 7)
    attendees = attendees.split(";")
    sendmail(organizer,location,starttime,endtime,to, attendees,subject,method)

def parseOpt():
  global SEED,batchfile,METHOD,SMTP_SERVER,SMTP_USERNAME,SMTP_PORT
  try:
    cmdlineOptions, args= getopt.getopt(sys.argv[1:],'hds:p:o:b:u:e:',
      ["help","delete","server", "port","options","batch","user","seed"])
  except getopt.GetoptError, e:
    sys.exit("Error in a command-line option:\n\t" + str(e))
  for (n,v) in cmdlineOptions:
    if n in ("-h","--help"):
      print __doc__
      exit(-1)
    elif n in ("-d", "--delete"):
      METHOD="CANCEL"
    elif n in ("-e", "--seed"):
      SEED=v
    elif n in ("-s", "--sever"):
      SMTP_SERVER=v
    elif n in ("-u", "--user"):
      SMTP_USERNAME=v
    elif n in ("-p", "--port"):
      SMTP_PORT=v
    elif n in ("-b", "--batch"):
      batchfile=v
      print 'batchfile=', batchfile
    elif n in ("-o", "--options"):
      with open(v, 'r') as stream:
          data=load(stream)
          print 'Load options'
          print data
          globals().update(data)

    
if __name__ == "__main__":
  if len(sys.argv) == 1:
    print __doc__
    exit(0)
  
  parseOpt() 
  SMTP_PASSWORD = getpass.getpass()
  print batchfile
  batchsend(batchfile, METHOD)


