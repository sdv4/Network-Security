# FTserver.py
# File Transfer server accepting connections from one client at a time and either
# uploading a file from the client or downloading a file to the client
# CPSC 526 Assignment 4 - Fall 2017
# Authors: Shane Sims and Mason Lieu
# Sources viewed or consulted:
# http://www.binarytides.com/python-socket-server-code-example/ - for help structuring server
# https://www.digitalocean.com/community/tutorials/how-to-handle-plain-text-files-in-python-3 - for information on file creation
from __future__ import print_function                                           # Import python3 print function
import socket
import sys

#TODO: implement client authentication using shared key
def authenticate_client(connection, key):
    return True

def serve(connection):
    data = connection.recv(1024)
    print(data)
    if int(data) is 0:                                                          # Client wants to upload file
        connection.sendall("0")
        fileName = connection.recv(1024)                                        # Get name of file to be uploaded
        fileName = (str(fileName)).replace('\n','')                             # for connecting with netcat
        theFile = open(fileName, "w+")                                          # Create file obj with specified name or write over file if already exists in dir
        connection.sendall(fileName)                                            # Echo file name back to client to indicate ready to receive
        while 1:                                                                # Receive file data from client until no more sent
            data = connection.recv(1024)
            theFile.write(data)                                                 # Write data to file
            if not data:
                break
        theFile.close()                                                         # Close/finish writting to file and
        connection.sendall("1")                                                 # Send success indicator
        print("OK", file = sys.stderr)
        print("Status: success")

    elif data is 1:                                                             # Client wants to download file
        connection.sendall("1")

    else:
        connection.sendall("-1")                                                # Invalid argument from client, respond with error code
    connection.close()


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
        print("FTserver started and listening on port " + str(PORT) + "\nUsing secret key: " + str(KEY))
        while 1: #listen for client connections - serve - repeat
            print("Waiting for client connection...")
            client_connection, client_address = listening_socket.accept()
            print("New connection from client on address " + str(client_address))
            if authenticate_client(client_connection, KEY) :
                serve(client_connection)
            else:
                print("Error: wrong key", file = sys.stderr)
    else:
        print("Error: wrong command line arguments", file = sys.stderr)


if __name__ == "__main__":
  main()
