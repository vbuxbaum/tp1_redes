#!/usr/bin/python3

import socket
import sys
import struct
import codecs
import threading
import binascii

# -*- coding: ascii -*-

###############################################################################
def decode16 (b_input):
    #print("#debug in DECODE: ", b_input)
    data = codecs.decode(b_input, 'hex')
    return list(data.decode("latin-1"))

###############################################################################
def encode16 (b_input):
    #print("#debug in ENCODE: ", b_input)
    data = ''.join(i for i in b_input)
    return codecs.encode(data.encode('latin-1'),'hex')    

###############################################################################
def carry_around_add(a, b):
    c = a + b
    return(c &0xffff)+(c >>16)

###############################################################################
def checksum(msg):
    str_msg = "".join(i for i in msg)
    msg = str.encode(str_msg)
    s =0
    for i in range(0, len(msg),2):
        w = (msg[i]) + ((msg[i+1])<<8)
        s = carry_around_add(s, w)
    return~s &0xffff

def create_frame(data,length,ID,flag):
    sync = "\xDC\xC0\x23\xC2"
    frame = []
    str_length = str(length)
    str_length = ((2 - len(str_length))*"\0")+str_length # length must be a 2 digit number

    #Frame without checksum
    for field in [sync,sync,str_length,'\x00\x00',ID,flag]:
        for c in field:
            frame.append(c)
    for c in data:
        frame.append(c)

    # Fixes the error when the length of the frame is odd by appending NULL char at the end of the frame
    if(len(frame)%2 == 1):
        frame.append('\x00')

    chksum = checksum(frame) # Calculates checksum
    #print(struct.pack('H', chksum))

    # Rebuilds the frame including the checksum
    frame = []
    for field in [sync,sync,str_length,'\x00\x00',ID,flag]:
        for c in field:
            frame.append(c)
    for c in data:
        frame.append(c)

    # Fixes the error when the length of the frame is odd by appending NULL char at the end of the frame
    if(len(frame)%2 == 1):
        frame.append('\x00')
    return frame

def get_data_from_frame(frame):
    return frame[14:]

def start_node():
    #   args [1 = -s|-c , 2 = [<IP server>:]port, 3 = input file, 4 = output file ]
    args = list(sys.argv)
    
    #   set host and port for connection
    HOST = "" 
    PORT = ""
    arg_2 = args[2].split(":")
    if (args[1] == "-c"): 
        HOST = arg_2[0]
        PORT = arg_2[1]
    elif (args[1] == "-s"):
        PORT = arg_2[0]

    file_IN = open(args[3],"rb")
    file_OUT = open(args[4],"wb")

    #read input

    length = 0
    b_in = file_IN.read(1)
    data = []
    while (b_in):
        data.append(b_in.decode())
        length += 1
        b_in = file_IN.read(1)
        
    #print ("FILE DATA: \n", data, "\n\n")

    ID = 0
    flag = 0
    #print(length)
    #create the protocol's frame
    frame = create_frame(data,chr(length),'\x00','\x00')
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


