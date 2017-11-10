# FTclient.py
# Implements custom protocol - to be used with FTserver.py
# File Transfer client for uploading a file to a server or downloading a file from a server
# CPSC 526 Assignment 4 - Fall 2017
# Authors: Shane Sims and Mason Lieu
# Version: 10 November 2017
# Sources viewed or consulted:
# https://docs.python.org/3/library/fileinput.html#fileinput.FileInput - for info on reading from stdin
from __future__ import print_function                                           # Import python3 print function
import socket
import sys
import fileinput
import os
import hashlib
import random

def download(conn):
    conn.sendall("1")                                                           # Indicate to server that client wants to download files
    data = conn.recv(1024)
    if str(data) == "1":                                                        # Server ready to receive fileName
        conn.sendall(fileName)
        fileSize = conn.recv(1024)                                              # receive file size from server
        if str(fileSize) != "-1":
            try:
                conn.sendall("1")                                               # Indicate ready to read file from server
                theFile = conn.recv(int(fileSize))                                      # get entire file
                print(theFile)
                conn.sendall("1")
            except:
                conn.sendall("-1")
        else:
            print("Error: file could not be read by server", file = sys.stderr)
    else:
        print("Error: file could not be read by server", file = sys.stderr)

def upload(conn):
    conn.sendall("0")                                                           # Indicate to server that client wants to upload files
    data = conn.recv(1024)
    if str(data) == "0":
        conn.sendall(fileName)
        fileNameEcho = conn.recv(1024)
        if str(fileNameEcho) == fileName :
            print(fileName)
            for block in fileinput.input(files='-',):
                conn.sendall(block)
            conn.shutdown(socket.SHUT_WR)
            statusResponse = conn.recv(1024)
            if str(statusResponse) == "1":
                print("Upload successful - closing client...")
        else:
            print("Error: file could not be written by server", file = sys.stderr)
    else:
        print("Error: file could not be written by server", file = sys.stderr)

def main():
    global PORT
    global KEY
    global HOST
    global command
    global fileName
    global cipher

    if(len(sys.argv) == 6):
        command = str(sys.argv[1])
        fileName = str(sys.argv[2])
        hostPort = ((str(sys.argv[3])).split(':'))
        HOST = hostPort[0]
        PORT = int(hostPort[1])
        cipher = str(sys.argv[4])
        KEY  = str(sys.argv[5])

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((HOST, PORT))

        # Authenticate client to server

        client_nounce = os.urandom(16)
        first_msg = cipher + "," + client_nounce
        server_socket.sendall(first_msg)                                        # Sebd cipher,nounce to server
        server_challenge = server_socket.recv(1024)
        challenge_response = hashlib.sha256(KEY + server_challenge).digest()
        server_socket.sendall(challenge_response)


        # Successful Authentication
        if command == "write":
            upload(server_socket)

        elif command == "read":
            download(server_socket)
        else:
            print(command)
            print("Error: wrong command line arguments", file = sys.stderr)

    else:
        print("Error: wrong command line arguments", file = sys.stderr)
        
    conn.close()
    sys.exit()


if __name__ == "__main__":
  main()
