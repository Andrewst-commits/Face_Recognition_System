import socket
import threading
import logging
import sys, traceback
from time import sleep
import os
import inspect


log = logging.getLogger(name="winter")

#CONSTANTS (logical)
#heder format for answer
FT_HTML = 1
FT_JS = 2
FT_JPG = 3
FT_ICO = 4
FT_GIF = 5

#CONSTANTS (functional)
BUFFER_DWNLOAD = 1024   # size of http buffer
BUFFER_UPLOAD = 1024	 # buffer for sending big files to client
HTTP_PORT = 8084	 # port of http server
HTTP_IP = ''
HTTP_CONNECTIONS = 1 # number of client connections
SERVER_SHTDWN_HNDL = '/shutdown'	# request from client for shutdown server thread
SERVER_DSCNCT_HNDL = '/disconnect'  # request from client for disconnect and free socket


#CONTAINERS
_handlers = {}
_server_thread = 0
client_sock = 0
client_addr = 0
recdata = 0
head = 0
lsn_res = True
dscnct_res = False

#FUNCTIONS
def debug():
	log.debug("call debug()")

def http_server_handler():
	#acess to constants
	global BUFFER_DWNLOAD
	global HTTP_PORT
	global HTTP_IP
	global HTTP_CONNECTIONS
	
	global client_sock
	global client_addr
	global recdata
	global head
	global lsn_res
	global dscnct_res
	
	try:
		#server listen socket init
		lsn_res = True
		http_lsn = socket.socket()
		http_lsn.bind((HTTP_IP, HTTP_PORT))
		http_lsn.listen(HTTP_CONNECTIONS)

		#connection init
		while(lsn_res):
			dscnct_res = False
			client_sock, client_addr = http_lsn.accept()

			# [+++] need a new thread for port listen (http_lsn.accept() blocking current thread)
			#crutch
			if not(lsn_res):
				break
			#crutch

			log.info('request from ['+ str(client_addr[0]) +'] for client connection accepted')
			
			while(True):
				data = client_sock.recv(BUFFER_DWNLOAD)
				recdata = data

				if (len(data) == 0):
					log.info('['+str(client_addr[0])+'] disconnected (received 0 bytes)')
					break
				#crutch
				if not(lsn_res):
					break
				#crutch

				log.info('received ['+ str(len(data)) + '] bytes from [' + str(client_addr[0])+']')

				phead = http_head_parser(data)
				head = phead
				
				log.debug('HEAD == '+str(phead))
				
				call_handler(phead['handler'], phead['args'])
				#crutch
				if (dscnct_res): #or not(phead['fields']['Connection'] == 'keep-alive')
					break
				if not(lsn_res):
					break
				#crutch
			log.info('['+str(client_addr[0])+'] disconnected')		
			client_sock.close()

		log.info('HTTP Server is shutdown')
	except:
		log.error("Critical exception\n")
		traceback.print_exc(limit=2, file=sys.stdout)
		log.info('HTTP Server is shutdown')
		
	finally:
		client_sock.close()
		lsn_res = False


def http_server_start(port = HTTP_PORT):
	HTTP_PORT = port
	global _server_thread
	_server_thread = threading.Thread(target=http_server_handler, args=())
	_server_thread.start()
	log.info("http interface created on port: "+ str(HTTP_PORT))
	#_server_thread.join()

def http_server_stop():
	global lsn_res
	lsn_res = False

	return lsn_res

def http_server_isruning():
	return lsn_res

def http_head_parser(head):
	linecounter = 0
	phead = {}
	args = {}
	fields = {}
	content_sep = head.find('\r\n\r\n'.encode()) #separatur between HEAD & filedata
	lines = head[:content_sep].decode().split('\n')

	#firstline parse
	firstline = lines[0].strip()					# 'GET /request/?kw1=arg1&kw2=arg2 HTTP/1.1'
	preq = firstline.strip().split()				# ['GET', '/request/?kw1=arg1&kw2=arg2', 'HTTP/1.1']
	
	sepindex = preq[1].find('/?')					# extracting arguments if request have
	if (sepindex > -1):
		pargs = preq[1][(sepindex+2):].split('&')		# '/request/?kw1=arg1&kw2=arg2' -> ['kw1=arg1','kw2=arg1']
		for strarg in pargs:							# ['kw1=arg1','kw2=arg1'] -> {'kw1':'arg1','kw2':'arg1'}
			parg = strarg.split('=')
			args[parg[0]] = parg[1]

		handler = preq[1][:sepindex]					# '/request/?kw=arg' -> '/request'
	else:
		handler = preq[1]

	#parse other head fields (after first line)
	for line in lines[1:]:
		seppos = line.find(':')
		kword = line[:seppos].strip()
		arg = line[(seppos+1):].strip()
		fields[kword] = arg
		linecounter += 1


	#request type
	phead['type'] = preq[0]

	#version
	phead['version'] = preq[2]

	#handler name
	phead['handler'] = handler

	#args
	phead['args'] = args

	#fields
	phead['fields'] = fields

	#data after field
	phead['end'] = head[content_sep+4:]

	return phead


def call_handler(request, kwargs):
	if request in _handlers.keys():
		#test for keyword identation
		detector = True
		args = inspect.getfullargspec(_handlers[request]) # get arguments of function
		log.debug(str(args))
		for kwargname in kwargs.keys():					# kwarg test for entry
			if not(kwargname in args.args):
				detector = False
				log.error('The handler function ['+request+'] does not have an argument named ['+kwargname+']')

		if detector:	#if received keywords and function arguments is identyty
			_handlers[request](**kwargs)
			log.info("handler was called by ["+str(client_addr[0])+"] successfully: ["+ request+ "]")
	else:
		log.error('Client requested a non-existent handler function: ['+str(request)+']')
		client_sock.send('HTTP/1.1 204 No Content\r\n'.encode()) #404 doesn't work (may need html prewiew)
		client_sock.send('\r\n'.encode())
		
		#[+++] if need be
		#test_thread = threading.Thread(target=_handlers[name], args=())
		#test_thread.start()
		#test_thread.join()

def add_handler(name, handler):
	_handlers[name]=handler
	
def delete_handler(name):
	if _handlers.pop(name, True):
		log.error("handlers not contains element: "+name)

def send_head(ctype = None, clength = 0, kwargs = {}):
	#always for successfully answer
	client_sock.send('HTTP/1.1 200 OK\r\n'.encode())
	
	if (ctype == None):
		ctype = 'text/plain'
	elif (ctype == FT_HTML):
		ctype = 'text/html'
	elif (ctype == FT_JS):
		ctype = 'application/x-javascript'
	elif (ctype == FT_JPG):
		ctype = 'image/jpg'
	elif (ctype == FT_ICO):
		ctype = 'image/ico'
	else:
		log.warning('header format for answer is incorrect (set by user as "'+str(ctype)+'" )')
	
	#always
	client_sock.send(('Content-Type: '+ctype+'\r\n').encode())
	client_sock.send(('Content-Length: '+str(clength)+'\r\n').encode())
	if(len(kwargs)):
		for fieldkey in kwargs.keys():
			client_sock.send((str(fieldkey) +': '+ str(kwargs[fieldkey]) +'\r\n').encode())
	
	client_sock.send('\r\n'.encode())
	

def return_answer(data):
	size = client_sock.send(data.encode())
	log.debug('returned '+str(size)+' bytes to client on '+str(client_addr[0]))

def return_file(fname, ftype = None):
	fsize = os.path.getsize(fname)
	send_head(ctype=ftype, clength=os.path.getsize(fname))
	with open(fname, "rb") as f:
		while (f.tell() < fsize):
			fdata = f.read(BUFFER_UPLOAD)
			client_sock.send(fdata)
	
def return_file4load(fname, nameas = None, ftype = None):
	#filename set for client downloading
	if (nameas == None):
		setname = fname[(fname.rfind('/')+1):]
	else:
		setname = nameas

	fsize = os.path.getsize(fname)

	#file uploding
	send_head(ctype = ftype, clength = fsize, kwargs = {'Content-Disposition':('attachment; filename='+str(setname))})

	with open(fname, "rb") as f:
		while (f.tell() < fsize):
			fdata = f.read(BUFFER_UPLOAD)
			client_sock.send(fdata)

	log.info('Client is load file "'+str(fname)+'"')

def accept_file(vay='./', tofile = True):
	ctype = head['fields']['Content-Type']
	if('boundary=' in ctype):
		bcode = ctype[ctype.find('boundary=')+len('boundary='):].encode()
		codelen = len(bcode)
	else:
		log.error('Incorrect HTTP head for receiving file (not found "boundary")')
		return 1

	if(len(head['end']) > 0):
		bbuff = head['end']
	else:
		bbuff = client_sock.recv(BUFFER_DWNLOAD)

	#[+++] here will be parser for subhead
	#crutch
	filename = bbuff[bbuff.find('filename='.encode())+len('filename="'):]
	filename = filename[:filename.find('"\r\n'.encode())].decode()
	vay = vay + filename
	#crutch
	#shbeginx = bbuff.find(bcode)+codelen
	#shendx = bbuff.find('\r\n\r\n'.encode())
	#allsubhead = bbuff[shbeginx:shendx].decode().strip()
	#log.debug('allsubhead == '+str(allsubhead))
	#strsubhead = allsubhead.split('\r\n')
	#log.debug('strsubhead == '+str(strsubhead))
	#argsubhead = {}
	#for line in strsubhead:
	#	argname_data = line.split(':')
	#	argsubhead[argname_data[0]] = argname_data[1]
	#log.debug('argsubhead == '+str(argsubhead))
	#--

	content_sep = bbuff.find('\r\n\r\n'.encode())+4
	bbuff = bbuff[content_sep:]

	log.debug('vay == '+vay)
	log.debug('bcode == '+str(bcode))
	#log.debug('bbuff == '+str(bbuff))
	
	if (tofile):
		with open(vay, "wb") as f:
			#cyckle begin
			while True:
				#log.debug('bbuff == '+str(bbuff))
				#watch end border code (bcode)
				if(bcode in bbuff):
					#if buffer have bcode then cut this and break resaiving file
					endindx = bbuff.rfind(bcode)
					bbuff = bbuff[:endindx].replace('\r\n--'.encode(),''.encode())

					#save to file
					log.debug('(inif)bbuff == '+str(bbuff))
					f.write(bbuff)

					return filename
				#save to file
				log.debug('(noif)bbuff == '+str(bbuff))
				f.write(bbuff)
				#--
				#receive new chunk
				bbuff = client_sock.recv(BUFFER_DWNLOAD)

	else:
		bigbuffer = b''
		while True:
			#log.debug('bbuff == '+str(bbuff))
			#watch end border code (bcode)
			if(bcode in bbuff):
				#if buffer have bcode then cut this and break resaiving file
				endindx = bbuff.rfind(bcode)
				bbuff = bbuff[:endindx].replace('\r\n--'.encode(),''.encode())

				#save to file
				log.debug('(inif)bbuff == '+str(bbuff))
				bigbuffer = bigbuffer + bbuff

				return bigbuffer
			#save to file
			log.debug('(noif)bbuff == '+str(bbuff))
			bigbuffer = bigbuffer + bbuff
			#--
			#receive new chunk
			bbuff = client_sock.recv(BUFFER_DWNLOAD)

	return 1

def disconnect_client():
	global dscnct_res
	dscnct_res = True

	htmlstr = '<!DOCTYPE html><html><head></head><body><p>SUCCESFULLY CALL DISCONNECT<p></body></html>'
	send_head(ctype = FT_HTML, clength = len(htmlstr))
	return_answer(htmlstr)

def shutdown_server():
	global lsn_res
	lsn_res = False

	htmlstr = '<!DOCTYPE html><html><head></head><body><p>SUCCESFULLY CALL SHUTDOWN<p></body></html>'
	send_head(ctype = FT_HTML, clength = len(htmlstr))
	return_answer(htmlstr)

if not(__name__ == "__main__"):
	add_handler(SERVER_DSCNCT_HNDL, disconnect_client)
	add_handler(SERVER_SHTDWN_HNDL, shutdown_server)

#WInter recall
elif __name__ == "__main__":
	#Logging init
	logging.basicConfig(format='[%(asctime)s]-%(levelname)s-%(name)s: %(message)s', \
						datefmt='%d-%b-%Y %H:%M:%S', \
						level=logging.DEBUG)
	log.setLevel(logging.DEBUG)
	
	#Script for recall
	#log.debug("WInter recall")
	print(" _    _ _____      _            ")
	print("| |  | |_   _|    | |           ")
	print("| |  | | | | _ __ | |_ ___ _ __ ")
	print("| |/\| | | || '_ \| __/ _ \ '__|")
	print("\  /\  /_| || | | | ||  __/ |   ")
	print(" \/  \/ \___/_| |_|\__\___|_|   ")
	print("                      by Eladiel")
	print('DESCRIPTION:')
	print('WInter is a simple module for integrating web/http')
	print('server to your code for creating web interface to your app')
    
