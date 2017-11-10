# FTclient.py
from __future__ import print_function                                           # Import python3 print function
import socket
import sys

def download(conn):
    conn.sendall("1")                                                           # Indicate to server that client wants to download files
    data = conn.recv(1024)
    if str(data) == "1":                                                        # Server ready to receive fileName
        conn.sendall(fileName)
        fileSize = conn.recv(1024)                                              # receive file size from server
        if str(fileSize) != "-1":
            conn.sendall("1")
            theFile = conn.recv(int(fileSize))                                      # get entire file
            print(theFile)
        else:
            print("Error: file could not be read by server", file = sys.stderr)
    else:
        print("Error: file could not be read by server", file = sys.stderr)
    conn.close()
    sys.exit()

def upload(conn):
    conn.sendall("1")                                                           # Indicate to server that client wants to download files


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
        if command == "write":
            upload(server_socket)

        elif command == "read":
            download(server_socket)
        else:
            print(command)
            print("Error: wrong command line arguments", file = sys.stderr)

    else:
        print("Error: wrong command line arguments", file = sys.stderr)


if __name__ == "__main__":
  main()
