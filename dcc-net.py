#!/usr/bin/python3

import socket
import sys
import struct
import codecs
import threading
import binascii

# -*- coding: ascii -*-

my_id = '\x01'

def id_generator():
	global my_id
	if my_id == '\x01':
		my_id = '\x00'
	else:
		my_id = '\x01'
	return my_id

###############################################################################	
def bytes_to_int(b):
    return int(binascii.hexlify(''.join(i for i in b).encode('latin-1')), 16)

###############################################################################	
def list_to_str(b):
    return ''.join(i for i in b)

###############################################################################
def decode16 (b_input):
	#print("#debug in DECODE: ", b_input)
	data = codecs.decode(b_input, 'hex')
	return list(data.decode("latin-1"))

###############################################################################
def encode16 (b_input):
	#print("#debug in ENCODE: ", b_input)
	data = ''.join(str(i) for i in b_input)
	return codecs.encode(data.encode('latin-1'),'hex')    

###############################################################################
def carry_around_add(a, b):
	c = a + b
	return(c &0xFFFF)+(c >>16)

###############################################################################
def checksum(msg):
	if(len(msg)%2 == 1):
		msg.append('\x00')
	
	s =0
	for i in range(0, len(msg),2):
		w = ord(msg[i+1]) + (ord(msg[i])<<8)
		s = carry_around_add(s, w)
	return ~s & 0xFFFF

###############################################################################
def create_frame(data,length,ID,flag):
	sync = "\xdc\xc0\x23\xc2"
	frame = []
	
	#Frame without checksum
	for field in [sync,sync,length.decode('latin-1'),'\x00\x00',ID,flag]:
		for c in field:
			frame.append(c)
	for c in data:
		frame.append(c)

	# Calculates checksum
	chksum = struct.pack('!H', checksum(frame)).decode('latin-1')

	# Rebuilds the frame including the checksum
	frame = []
	for field in [sync,sync,length.decode('latin-1'),chksum,ID,flag]:
		for c in field:
			frame.append(c)
	for c in data:
		frame.append(c)

	return frame

###############################################################################
# Returns the beginning of a new frame. -1 if sync not found
def find_sync(msg):
	length = len(msg)
	for i in range(0,length - 4):	
		sync = msg[i:i+4]
		j = i + 4
		if(msg[j:j+4] == sync):
			return i
	return -1

###############################################################################
def get_data_from_frame(frame):
	return frame[14:]

###############################################################################
def receive_frame(msg):
	try:
		#Finds the beginning of a frame, in case there was some transmission problem 
		frame_begin = find_sync(msg)
		if(frame_begin == -1):
			print("ERROR RECEIVING FRAME") #Didn't find the beginning of the frame
			return -1
		frame = msg[frame_begin:] # Frame transmitted
		orig_chksum = frame[10:12] #received checksum
		# Get infos of the frame
		sync1 = frame[0:4]
		sync2 = frame[4:8]
		length = frame[8:10]
		chksum = '\x00\x00'
		ID = frame[12]
		flag = frame[13]
		data = frame[14:14+bytes_to_int(length)]
		if(''.join(i for i in length) == '\x00\x00' and flag == '\x80'): # Frame received is a ACK
			#needs to check if ID is the same as the one saved by the system
			print("ACK RECEIVED")
			return 1
		else: # Frame received is a regular frame
			frame = []
			
			#Frame without checksum
			for field in [sync1,sync2,length,chksum,ID,flag]:
				for c in field:
					frame.append(c)
			for c in data:
				frame.append(c)

			if (struct.pack('!H', checksum(frame)).decode('latin-1') == ''.join(i for i in orig_chksum)):
				return 1
			else:
				print("ERROR RECEIVING FRAME 2")
				return -1
	except:
		print("ERROR RECEIVING FRAME 3")
		return -1

###############################################################################
def work(sckt):
	str_size 	= struct.unpack(">i",sckt.recv(4))[0] 	# Recebe tamanho da string
	msg 		= sckt.recv(str_size).decode()			# Recebe string
	X 			= struct.unpack(">i",sckt.recv(4))[0] 	# Recebe chave para cifra de cesar
	#print (msg)
	msg  = decripto(msg,X)
	print (msg)
	sckt.send(str.encode(msg))
	sckt.close()

###############################################################################
def start_node():
	#   args [1 = -s|-c , 2 = [<IP server>:]port, 3 = input file, 4 = output file ]
	args = list(sys.argv)
	
	tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# variable that will hold the used socket
	sckt = '' 

	#   set host and port for connection
	HOST = '' 
	PORT = ''
	arg_2 = args[2].split(":")
	if (args[1] == "-c"): 	# CALLED AS CLIENT
		HOST = arg_2[0]
		PORT = int(arg_2[1])

		# dest = (HOST, PORT)
		# tcp.connect(dest)
		# sckt = tcp
	elif (args[1] == "-s"):	# CALLED AS SERVER 
		PORT = int(arg_2[0])

		# tcp.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		# time_out = struct.pack("2l", *[15,0])
		# tcp.setsockopt( socket.SOL_SOCKET, socket.SO_RCVTIMEO, time_out)
		# orig = (HOST, PORT)
		# tcp.bind(orig)
		# tcp.listen(1)
		# sckt,client = tcp.accept()

	# open files for input and output
	file_IN = open(args[3],"rb")
	file_OUT = open(args[4],"wb")

	#read input
	n_packs = 0
	count_len = 0
	b_in = file_IN.read(1)
	data_set = [[]]
	while (b_in):
		data_set[n_packs].append(b_in.decode())
		count_len += 1
		b_in = file_IN.read(1)
		if count_len == 65535:
			count_len = 0
			n_packs += 1
			data_set.append([])
			
	#create the protocol's frames
	for data in data_set:
		frame = create_frame(data,struct.pack('!H', len(data)),id_generator(),'\x00')	

		#encode the frame
		frame = encode16(frame)

		######(Send frame)########

	############################################################
		######(Receive frame)#######


		#dcc023c2dcc023c2........
		msg = decode16(frame)
		#if (receive_frame(list('\xdc\xc0\x23\xc2\xdc\xc0\x23\xc2\x00\x00\x00\x00\x00\x80')) == 1):  Test ACK
		if (receive_frame(msg) == 1):
			data = get_data_from_frame(msg)
			#write data
			#send ack
		
		print ("DECODED DATA: \n", list_to_str(data), "\n")



	file_IN.close()
	file_OUT.close()


server_thread = []
if __name__ == "__main__":
	start_node()

	#while(1):
	#server_thread.append(threading.Thread(target=start_node, args=()))
	#server_thread[0].start()
	#server_thread[0].join()


