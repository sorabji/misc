#! /usr/bin/python

import optparse
import re
import email
import getpass
import imaplib
import os
import re

cmdParser = optparse.OptionParser()
cmdParser.add_option("-u","--user",dest='user',
                     help='user login name')

cmdParser.add_option("-p",'--pass',dest='pwd',
                     help='login password')

cmdParser.add_option("-q",'--quiet',dest='verbose', default=True,
                     action="store_false",
                     help="don't print status messages to stdout")

cmdParser.add_option("-b","--mailbox",dest='mailBox', default='INBOX',
                     help='mail box to download mail from')

cmdParser.add_option("f","--file",dest='FILE',
                     default='/home/artie/scripts/emails/addresses.dat',
                     help='full pathname of the file to save addresses in')

cmdParser.add_option("-l",'--logFile',dest='logFile',
                     default = '/home/artie/scripts/emails/logFile.dat',
                     help='full pathname of the file to put logging info in')

(options, args) = cmdParser.parse_args()

user = options.user
pwd = options.pwd
verbose = options.verbose
mailBox = options.mailBox
FILE=options.FILE
logFile = options.logFile


yahooStartDelim = "Sorry it didn't work out."
yahooEndDelim = "Below this line is a copy of the message."

gmailStartDelim = "failed permanently:"
gmailEndDelim = "Technical details"


emailRegex = re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}\b')

#######################################
### in case you don't like cmd args ###
######### uncomment these #############

#user = 'itest243@gmail.com'
#pwd = 'fuckThis'

# connecting to the gmail imap server

if verbose: print "Connecting to the imap server as "+user+"..."

m = imaplib.IMAP4_SSL("imap.gmail.com")
m.login(user, pwd)
m.select(mailBox) # here you a can choose a mail box like INBOX instead
# use m.list() to get all the mailboxes

# you could filter using the IMAP rules here 
# (check http://www.example-code.com/csharp/imap-search-critera.asp)

if verbose: print "downloading..."

resp, items = m.search(None, "ALL") 
items = items[0].split() # getting the mails id

# list where all the emails will end up
meh = []


# count of emails
emailNum = 1

# test set
test = items[2:100]

# replaced 'items' with 'test' for...well, testing
for emailid in test:
    # fetching the mail, "`(RFC822)`" means "get the whole stuff"
    # but you can ask for headers only, etc
    if verbose: 
        print "fetching email Number: "+str(emailNum)+" of "+str(len(test))+" total"

    resp, data = m.fetch(emailid, "(RFC822)") 

    # getting the mail content
    if verbose: print "getting the mail content..."

    email_body = data[0][1] 

    # setting bounds where the addresses will reside
    if verbose: 
        print "checking if it's a yahoo or gmail generated bounce message..."

    if email_body.find(yahooStartDelim)!=-1 and email_body.find(yahooEndDelim)!=-1:
        start = email_body.index(yahooStartDelim)
        end = email_body.index(yahooEndDelim)
    
        # getting my special string to work on
        if verbose:
            print "getting the chunk of the message body we're interested in..."

        parsingString = email_body[start+len(yahooStartDelim):end]

        result = emailRegex.findall(parsingString)

        if verbose: print "successfully grabbed a list of emails..."

        count = 1
        for i in result:
            i=i.rstrip("...User")
            i=i.rstrip("...Du")
            if verbose:
                print "checking if we already have "+i,
                print " for email number: "+str(emailNum)

            if meh.__contains__(i):
                if verbose: print "already in list, moving on..."

                count +=1
                continue
            else:
                if verbose: print "unique email! adding it now..."

                meh.append(i)
                count +=1




    elif email_body.find(gmailStartDelim)!=-1 and email_body.find(gmailEndDelim)!=-1:
        start = email_body.index(gmailStartDelim)
        end = email_body.index(gmailEndDelim)

        if verbose: 
            print "getting the chunk of the message body we're interested in..."
        parsingString = email_body[start+len(gmailStartDelim):end]

        result = emailRegex.findall(parsingString)
        if verbose: print "successfully grabbed a list of emails..."

        count = 1

        for i in result:
            i=i.rstrip("...User")
            i=i.rstrip("...Du")
            if verbose: 
                print "checking if we already have "+i,
                print " for email number: "+str(emailNum)

            if meh.__contains__(i):
                if verbose: print "already in list, moving on..."

                continue
            else:
                if verbose: print "unique email! adding it now..."

                meh.append(i)
                count +=1
    emailNum+=1

if verbose: 
    print "sorting our list of emails..."

meh.sort(key=lambda x: x.lower())

if verbose: 
    print "writing to file..."

bak = open(FILE,"w")
for i in meh:
    print >>bak, i,
    print >>bak, "\n",
bak.close()

if verbose: print "Done!"

