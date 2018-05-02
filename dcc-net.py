#!/usr/bin/python3

import socket
import sys
import time
import struct
import codecs
import threading
import binascii

# -*- coding: ascii -*-


###############################################################################	
###############################################################################	
my_id = '\x01'

def id_generator():
	global my_id
	if my_id == '\x01':
		my_id = '\x00'
	else:
		my_id = '\x01'
	return my_id


###############################################################################	
###############################################################################	
def bytes_to_int(b):
    return int(binascii.hexlify(''.join(i for i in b).encode('latin-1')), 16)


###############################################################################	
###############################################################################	
def list_to_str(b):
    return ''.join(i for i in b)


###############################################################################
###############################################################################
def decode16 (b_input):
	#print("#debug in DECODE: ", b_input)
	data = codecs.decode(b_input, 'hex')
	return list(data.decode("latin-1"))


###############################################################################
###############################################################################
def encode16 (b_input):
	#print("#debug in ENCODE: ", b_input)
	data = ''.join(str(i) for i in b_input)
	return codecs.encode(data.encode('latin-1'),'hex')    


###############################################################################
###############################################################################
def carry_around_add(a, b):
	c = a + b
	return(c &0xFFFF)+(c >>16)


###############################################################################
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
###############################################################################
# Checks if is sync pattern
def is_double_sync(msg):
	return msg == ['Ü', 'À', '#', 'Â', 'Ü', 'À', '#', 'Â']


###############################################################################
###############################################################################
def check_ack(frame):
	
	ID = frame[12]
	flag = frame[13]
	
	if(flag == '\x80'): # Frame received is a ACK
		#print("ACK RECEIVED")
		return 1 if ID == '\x01' else 0 #returns value for ID set in ACK
	else: # Frame received is a regular frame
		return -1


###############################################################################
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

		dest = (HOST, PORT)
		tcp.connect(dest)
		sckt = tcp
	elif (args[1] == "-s"):	# CALLED AS SERVER 
		PORT = int(arg_2[0])

		tcp.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		time_out = struct.pack("2l", *[5,0])
		tcp.setsockopt( socket.SOL_SOCKET, socket.SO_RCVTIMEO, time_out)

		orig = (HOST, PORT)

		tcp.bind(orig)
		tcp.listen(1)
		sckt,client = tcp.accept()
	else:
		print ("MUST DECLARE IF IT IS CLIENT OR SERVER")
		return -1
	# open files for input and output
	file_IN = open(args[3],"rb")
	

	#read input
	n_packs = 0
	count_len = 0
	b_in = file_IN.read(1)
	data_set = [[]]
	while (b_in):
		data_set[n_packs].append(b_in.decode('latin-1'))
		count_len += 1
		b_in = file_IN.read(1)
		if count_len == 65535:
			count_len = 0
			n_packs += 1
			data_set.append([])
	file_IN.close()	

	#create the protocol's frames
	frame_set = []
	for data in data_set:
		frame = create_frame(data,struct.pack('!H', len(data)),id_generator(),'\x7f')	

		#encode the frame
		frame_set.append((1 if my_id == '\x01' else 0,encode16(frame)))
		print (data)
		
		print ("DECODED DATA: \n", list_to_str(data), "\n")


	file_OUT = open(args[4],"wb")
	f_index = 0 
	f_id = ''
	while (1):
		if f_index >= 0:
			print("PACK SENT", f_index)
			sckt.send(frame_set[f_index][1])

		sckt.settimeout(15)
		f_sync = decode16(sckt.recv(8))
		if f_sync == []:
			break
		while 1: # procura por par de SYNCs 
			print ("hmm", f_sync)
			sync2 = decode16(sckt.recv(8))
			f_sync.extend(sync2)
			if is_double_sync(f_sync):
				print ("ok")
				break
			else:
				print ("ops", f_sync)
				f_sync = sync2
			
		f_header = decode16(sckt.recv(12)) # recebe resto do header
		f_sync.extend(f_header); f_header = f_sync # agrupa sync sync e header -> header completo
		print (args[1], f_header) # printa header completo
		d_length = bytes_to_int(f_header[8:10])

		if (d_length == 0): #recebeu um frame sem dados (provavel ACK)
			print("ACK RECEBIDO >>> ", f_index )
			if  (f_index >= 0) and (check_ack(f_header) == frame_set[f_index][0]): #se recebeu um ACK esperado
				print("ACK CONFIRMA >>> ", frame_set[f_index][0])
				if  f_index == len(frame_set) - 1: #confere se foi o ultimo frame a ser enviado
					f_index = -1
				else:
					f_index += 1 
					print("index ++")
			else:
				time.sleep(1)
			
		elif (d_length > 0) : # receberá dados de um frame
			f_data = decode16(sckt.recv(d_length*2)) # recebe os dados do frame
			ACK_to_send = create_frame([],struct.pack('!H', 0),f_header[12], '\x80') # prepara ACK a ser enviado
			f_header.extend(f_data); f_complete = f_header # agrupa header e dados -> f_complete
			if struct.pack('!H', checksum(f_complete)).decode('latin-1') == '\x00\x00':
				print("ACK SENT")
				sckt.send(encode16(ACK_to_send))
				if f_id != f_header[12]:
					f_id = f_header[12]
					for b in f_data:
						file_OUT.write(b.encode('latin-1'))
		


			
	#end while		

	sckt.close()
	
	file_OUT.close()


server_thread = []
if __name__ == "__main__":
	start_node()

	#while(1):
	#server_thread.append(threading.Thread(target=start_node, args=()))
	#server_thread[0].start()
	#server_thread[0].join()


