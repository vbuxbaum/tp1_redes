#!/usr/bin/python3

import socket
import sys
import struct
import codecs
import threading

# -*- coding: ascii -*-

###############################################################################
def decode16 (str_input):
	pass

###############################################################################
def encode16 (b_input):
	pass	

###############################################################################
def carry_around_add(a, b):
    c = a + b
    return(c &0xffff)+(c >>16)

###############################################################################
def checksum(msg):
    s =0
    for i in range(0, len(msg),2):
        w =(msg[i])+((msg[i+1])<<8)
        s = carry_around_add(s, w)
    return~s &0xffff






if __name__ == "__main__":
    
	# 	args [1 = -s|-c , 2 = [<IP server>:]port, 3 = input file, 4 = output file ]
	args = list(sys.argv) 	
	
	#	set host and port for connection
	HOST 	= "" 
	PORT 	= ""
	arg_2 	= args[2].split(":")
	if (args[1] == "-c"): 
		HOST 	= arg_2[0]
		PORT 	= arg_2[1]
	elif (args[1] == "-s"):
		PORT 	= arg_2[0]

	print
	file_IN 	= open(args[3],"rb")
	file_OUT	= open(args[4],"wb")

	#read input
	data = []
	read_count 	= 0
	b_in 		= file_IN.read(1)
	print(b_in)
	while ( b_in):
		read_count += 1
		b_in = file_IN.read(1)
		print(b_in)
		

	file_IN.close()
	file_OUT.close()


