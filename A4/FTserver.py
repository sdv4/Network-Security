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
import os.path

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
        print("Command: write   File name: " + fileName)
        theFile = open(fileName, "w+")                                          # Create file obj with specified name or write over file if already exists in dir
        connection.sendall(fileName)                                            # Echo file name back to client to indicate ready to receive
        while 1:                                                                # Receive file data from client until no more sent
            data = connection.recv(1024)
            theFile.write(data)                                                 # Write data to file
            if not data:
                break
        theFile.close()                                                         # Close/finish writting to file and
        connection.sendall("1")                                                 # Send success indicator
        print("Status: success")

    elif int(data) is 1:                                                             # Client wants to download file
        connection.sendall("1")
        fileName = connection.recv(1024)                                        # Get name of file to be uploaded
        fileName = (str(fileName)).replace('\n','')                             # for connecting with netcat
        print("Command: read   File name: " + fileName)
        if os.path.exists(fileName):
            theFile = open(fileName, "r")
            data = theFile.read()
            fileSize = len(data)
            connection.sendall(str(fileSize))                                        # send file size so client knows file exists and will come next
            connection.sendall(data)                                            # Send file
            theFile.close()
            print("Status: success")

        else:
            connection.sendall("-1")                                            # File DNE, send protocol error code
            print("Status: fail - " + fileName + " does not exist on server")
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
        try:
            while 1: #listen for client connections - serve - repeat
                print("Waiting for client connection...")
                client_connection, client_address = listening_socket.accept()
                print("New connection from client on address " + str(client_address))
                if authenticate_client(client_connection, KEY) :
                    serve(client_connection)
                else:
                    print("Error: wrong key", file = sys.stderr)
        except KeyboardInterrupt:
            print("\nControl-C detected. Closing server...")
            listening_socket.close()
            sys.exit(0)
    else:
        print("Error: wrong command line arguments", file = sys.stderr)


if __name__ == "__main__":
  main()
