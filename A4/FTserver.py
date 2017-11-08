# FTserver.py
# File Transfer server accepting connections from one client at a time and either
# uploading a file from the client or downloading a file to the client
# CPSC 526 Assignment 4 - Fall 2017
# Authors: Shane Sims and Mason Lieu
# Sources viewed or consulted:
# http://www.binarytides.com/python-socket-server-code-example/ - for help structuring server
from __future__ import print_function                                           # import python3 print function
import socket
import sys

def serve(connection):
    print("do something")



def main():
    global PORT
    global KEY
    if(len(sys.argv) == 3):
        PORT = int(sys.argv[1])
        KEY  = str(sys.argv[2])
        # Start listening on PORT
        listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)            # create TCP socket to communicate with IPv4 addresses
        #TODO: should we wrap the bind in try/except? why/why not?
        listening_socket.bind(("localhost",PORT))
        listening_socket.listen(5)                                                      # listen for client connections with queue for 5 connections
        print("FTserver started and listening on port " + str(PORT))
        while 1: #listen for client connections - serve - repeat
            client_connection, client_address = listening_socket.accept()
            print("New connection from client on address " + str(client_address))
            serve(client_connection)
    else:
        print("Error: wrong command line arguments", file = sys.stderr)


if __name__ == "__main__":
  main()
