import smtplib
import sys
from sys import stdout
import argparse
import time
from time import sleep
import re
import socket

def main():
	global host
	global infile
	global outfile
	global ver

        parser = argparse.ArgumentParser()
        parser.add_argument("-i", "--ip", help="host ip address", required=True)
        parser.add_argument("-f", "--infile", help="user name list file name", required=True)
        parser.add_argument("-o", "--outfile", help="file name to store valid users", required=True)
        parser.add_argument("-t", "--test", help="test options VRFY, EXPN, DEBUG, SHOWQ", required=False, action='store_true', default=False)
        parser.add_argument("-v", "--verbose", help="be verbose show current user name", required=False, action='store_true', default=False)

        args = parser.parse_args()

        host = args.ip
        infile = args.infile
        outfile = args.outfile
	if args.verbose:
		ver = True

	if args.test:
		dotests()
	else:
		testserv()

def testserv():
	print '******** Starting Scan at: ' + getdt() + ' ********'	
	try:
		server = smtplib.SMTP(host)
	except:
		print 'Error connecting to SMTP... Quiting.'
		sys.exit(0)

	server.ehlo()
	
	try:
		ho = socket.gethostbyaddr(host)[0]
                ho,ext = ho.split('.')[-2:]
                ho = ho + '.' + ext
	except:
		print 'Unknown hostname: using localhost instead'
		ho = 'localhost'
	
	fo = open(infile)
	for line in fo:
		uname = line.rstrip()
		#writeout(uname)

		try:
			ret = server.verify(uname)
		except smtplib.SMTPResponseException as e:
			err_msg = e.smtp_error
			print 'Error: ' + err_msg + '\n'
			sys.exit(0)
		except smtplib.SMTPConnectError:
			print 'Error with connection to server... Quiting.'
			sys.exit(0)
		
		for r in ret:
			if r == 252:
				re = dblchk(uname,ho,server)
				if re == 1:
					print '\nFound: ' + uname + '\n'
					fo2 = open(outfile,'a')
					fo2.write(uname + '\n')
					fo2.close()
				elif re == 2:
					print '\nCannot use mail FROM:... Quiting.'
					sys.exit(0)
			elif r == 502:
				print 'Cannot use VRFY on server.  Exiting...'
				sys.exit(0)
			elif r == 421:
				print 'Quiting... throttled server'
				sys.exit(0)

		
	fo.close()
	print '******** Scan completed at: ' + getdt() + ' ********'

def dotests():
        print '******** Starting options tests at: ' + getdt() + ' ********'
        try:
                server = smtplib.SMTP(host)
        except:
                print 'Error connecting to SMTP... Quiting.'
                sys.exit(0)

	try:
        	ret = server.verify()
        except smtplib.SMTPResponseException as e:
                err_code,err_msg = e.smtp_code, e.smtp_error
                print err_code + ' : ' + err_msg
                sys.exit(0)
	
	print '******** Options tests completed at: ' + getdt() + ' ********'


def dblchk(x,ho,server):
	mail_frm = server.mail('foo@' + ho)
	for r in mail_frm:
		if r == 550:
			return 2

	rcpt_ret = server.rcpt(x + '@' + ho)
	for t in rcpt_ret:
        	if ver == True:
                	i = '\r' + x + '@' + ho + ' - ' + str(rcpt_ret)
	                writeout(i)

		if t == 250:
			return 1
		else:
			return 0

def getdt():
	dt = time.strftime("%Y-%m-%d %H:%M")
	return dt

def writeout(val):
	stdout.write('\r%s' % val)
	stdout.flush()
	sleep(0.08)
	

if __name__ == "__main__":
	try:
        	main()
	except KeyboardInterrupt:
		print '\r'
	        sys.exit(0)
	except:
		raise
		print '\r Unknown error occurred... Quiting.  \r'
		sys.exit(0)

