#!/usr/bin/python3

import socket
import sys
import struct
import threading

# -*- coding: ascii -*-

###############################################################################
def decripto (stri, X):
	cesar = list(stri)
	for i in range(len(stri)):
		valc = ord(stri[i]) 
		valc = (valc - 97 - X)%26 + 97
		cesar[i] = chr(valc)
	
	return ''.join(cesar)

###############################################################################
def work(con):
	str_size 	= struct.unpack(">i",con.recv(4))[0] 	# Recebe tamanho da string
	msg 		= con.recv(str_size).decode()			# Recebe string
	X 			= struct.unpack(">i",con.recv(4))[0] 	# Recebe chave para cifra de cesar
	#print (msg)
	msg  = decripto(msg,X)
	print (msg)
	con.send(str.encode(msg))
	con.close()

###############################################################################
HOST = '' 					# Endereco IP do Servidor
PORT = int(sys.argv[1]) 	# Porta que o Servidor esta

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

time_out = struct.pack("2l", *[15,0])
tcp.setsockopt( socket.SOL_SOCKET, socket.SO_RCVTIMEO, time_out)

orig = (HOST, PORT)

tcp.bind(orig)
tcp.listen(1)

# thread calling work(con)

server_thread = []
for i in range(14):
    # socket.accept() return value is a pair (conn, address) where
    # conn is a new socket object usable to send and receive data on the connection
    # and address is the address bound to the socket on the other end of the connection.
    con, client = tcp.accept()
    server_thread.append(threading.Thread(target=work, args=(con,)))
    server_thread[i].start()

###############################################################################
###############################################################################
###############################################################################
