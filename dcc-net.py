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
		#print(s)
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
def get_data_from_frame(frame):
	return frame[14:]

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
		
	#print ("FILE DATA: \n", data_set, "\n\n")


	flag = '\x00'
	
	#create the protocol's frames
	for data in data_set:
		#print("len = ", len(data), struct.pack('!H', len(data)))
		frame = create_frame(data,struct.pack('!H', len(data)),id_generator(),'\x00')

		#print ("FRAME: \n", frame, "\n\n")
	
		#encode the frame
		frame = encode16(frame)
		#print ("ENCODED FRAME: \n", frame, "\n\n")
	
		#print ("DECODED FRAME: \n", decode16(frame), "\n\n")
		frame = decode16(frame)
	
		data = get_data_from_frame(frame)
		#print ("DECODED DATA: \n", data, "\n")







	file_IN.close()
	file_OUT.close()




server_thread = []
if __name__ == "__main__":
	start_node()

	#while(1):
	#server_thread.append(threading.Thread(target=start_node, args=()))
	#server_thread[0].start()
	#server_thread[0].join()


