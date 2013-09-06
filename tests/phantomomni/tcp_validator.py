#!/usr/bin/env python

import socket
import struct

def main():
    # Use hardcoded TCP connection ip and port
    TCP_IP = '127.0.0.1'
    TCP_PORT = 5555

    # Define the format of the data
    MSG_FMT = '!iiddddddd'
    msg_siz = struct.calcsize(MSG_FMT)

    # Set up the TCP connection
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    s.bind((TCP_IP, TCP_PORT))
    s.listen(1)

    conn, addr = s.accept()
    print 'Connected by', addr

    while True:
        raw_input('Press <Enter> to get next packet')

        # Get raw data from the TCP connection
        print 'Getting packet...'
        raw_data = conn.recv(msg_siz)
        print 'Packet received!'

        print 'Packet size: %d' % (len(raw_data))
        print 'Packet data: %s' % (raw_data)

        print 'Expected size: %d' % (msg_siz)

        # Verifify the size of the data from the 
        assert len(raw_data) == msg_siz

        # Unpack the raw data
        parsed_data = struct.unpack(MSG_FMT, raw_data)

        print 'Unpacked data:', parsed_data

    return


if __name__ == '__main__':
    main()
