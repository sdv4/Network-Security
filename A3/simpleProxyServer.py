# Materials Referenced:
# https://docs.python.org/3/howto/sockets.html
# https://docs.python.org/2/tutorial/datastructures.html
# Select example given in tutorial

import socket
import sys
import datetime
import select
from threading import Thread

global errorString
errorString = ("Usage: python3 proxyServer.py [logOptions] [replaceOptions]" +
        "<source port> <server> <destination port>")


if __name__ == "__main__":
    global destServer
    global destPort
    global HOST
    global loggingOption
    global replaceOptions

    if len(sys.argv) == 4:
        HOST, srcPort = "localhost", int(sys.argv[1])                           # Get port number to listen on as command line input
        destServer, destPort = str(sys.argv[2]), int(sys.argv[3])               # Get destination server name or IP and port number to connect to

    #sproxyListeningSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxyListeningSocket = socket.socket()
        proxyListeningSocket.setblocking(0)                                     # Make socket non binding so that more than one connection can be made
        proxyListeningSocket.bind((HOST, srcPort))
        proxyListeningSocket.listen(5)                                          # Listen for connections and queue up to 5 of them
        print("Port logger running: srcPort=" + str(srcPort) + " host=" + destServer + " dstPort=" + str(destPort))

        potential_readers = [proxyListeningSocket]
        potential_writers = []
        potential_errors = []

        dictionaryOfWriters = {}                                                # will hold pairs of (A, B) where A writes only to B


        while potential_readers:
            ready_to_read, ready_to_write, in_error = select.select(potential_readers, potential_writers, potential_errors)
            for sock in ready_to_read: #for each sock that has something to ready_to_read
                if sock is proxyListeningSocket: #then the thing being read is going to be a new local client conntection, which will need its own server connection
                    remoteServerConn = socket.socket()                          # set up remote server connection for incoming client
                    remoteServerConn.connect((destServer,destPort))
                    localClientConn, clientAddress = sock.accept()              # accept incoming local client
                    localClientConn.setblocking(0)                              # double check that connection in non binding so more clients can connect
                    currentDateTime = datetime.datetime.now()
                    print("New connection: " + str(currentDateTime) + ", from " + str(clientAddress) + "\n" )
                    potential_readers.append(localClientConn)                   # add connection to those that may have something to read
                    potential_readers.append(remoteServerConn)
                    dictionaryOfWriters[localClientConn] = remoteServerConn     #now if localClientConn is ready_to_read, it will only do so from remoteServerConn
                    dictionaryOfWriters[remoteServerConn] = localClientConn     #and if remoteServerConn is ready_to_read, it will only do so from localClientConn
                    break
                dataFromSock = sock.recv(1024)                                  # get data in 1024 byte chunks
                if dataFromSock: #i.e. not empty
                    linesOfData = dataFromSock.split(b'\n')
                    if sock is remoteServerConn:
                        for line in linesOfData:
                            print("<--- %s" % line)
                        (dictionaryOfWriters[sock]).send(dataFromSock)              # send the data to socks pair in the dictionary
                    else:
                        for line in linesOfData:
                            print("---> %s" % line)
                        (dictionaryOfWriters[sock]).send(dataFromSock)              # send the data to socks pair in the dictionary













    else:
        print(errorString)
