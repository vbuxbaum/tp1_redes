#!/usr/bin/python3

import socket
import sys
import struct

# -*- coding: ascii  -*-


def cripto (stri, X):
	cesar = list(stri)
	for i in range(len(stri)):
		valc = ord(stri[i]) 
		valc = (valc - 97 + X )%26 + 97
		cesar[i] = chr(valc)
	
	return ''.join(cesar) 
		
################################################################################

args = list(sys.argv)	# 1 = IP servidor, 2 = porta, 3 = string, 4 = X para Cifra de Cesar 

HOST = args[1] 			# Endereco IP do Servidor
PORT = int(args[2]) 	# Porta que o Servidor esta
msg = args[3]			# String a ser enviada 
X = int(args[4])		# Chave para Cifra de Cesar



tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.settimeout(15)

print (HOST, PORT)
dest = (HOST, PORT)
tcp.connect(dest)


tcp.send (struct.pack("!i",len(msg)))
tcp.send (str.encode(cripto(msg,X)))
tcp.send (struct.pack("!i",X))


#print ('Para sair use CTRL+X\n')

re_msg = tcp.recv(len(msg)).decode()
print (re_msg)

#while msg != '\x18':
#	tcp.send (str.encode(cripto(msg,X)))
#	msg = tcp.recv(1024)
#	print (msg.decode())
#	msg = input()

tcp.close()
