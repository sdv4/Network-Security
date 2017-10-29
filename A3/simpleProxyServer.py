# Materials Referenced:
# https://docs.python.org/3/howto/sockets.html
# https://docs.python.org/2/tutorial/datastructures.html
# Select example given in tutorial

#TODO: add keyboard interupt
#TODO: figure out if when how to close the sockets and return the "Connection closed" message

import string
import socket
import sys
import datetime
import select

global errorString
errorString = ("Usage: python3 proxyServer.py [logOptions] [replaceOptions] " +
        "<source port> <server> <destination port>")

def removeNonPrintable(lines):
    oldLines = lines
    newLines = []
    for line in oldLines:
        intList = list(line)
        intList = [46 if num < 32 or num > 126 else num for num in intList]
        byteLine = bytes(intList)
        newLines.append(byteLine)
    return newLines

def replacePattern(lines, opt1, opt2):
    oldLines = lines
    newLines = []
    bOpt1 = str(opt1).encode()
    bOpt2 = str(opt2).encode()
    for line in oldLines:
        line = line.replace(bOpt1, bOpt2)
        newLines.append(line)
    return newLines



if __name__ == "__main__":
    global destServer
    global destPort
    global HOST
    global loggingOption
    global replaceOptions
    global replaceOpt1, replaceOpt2

    cmdLineArgs = len(sys.argv)
    loggingOption  = ""
    replaceOptions = ""
    if cmdLineArgs == 4:
        HOST, srcPort = "localhost", int(sys.argv[1])                           # Get port number to listen on as command line input
        destServer, destPort = str(sys.argv[2]), int(sys.argv[3])               # Get destination server name or IP and port number to connect to
    elif cmdLineArgs == 5:
        loggingOption = str(sys.argv[1])
        HOST, srcPort = "localhost", int(sys.argv[2])                           # Get port number to listen on as command line input
        destServer, destPort = str(sys.argv[3]), int(sys.argv[4])               # Get destination server name or IP and port number to connect to
    elif cmdLineArgs == 8:
        loggingOption, replaceOptions, replaceOpt1, replaceOpt2 = str(sys.argv[1]), str(sys.argv[2]), str(sys.argv[3]), str(sys.argv[4])
        HOST, srcPort = "localhost", int(sys.argv[5])                           # Get port number to listen on as command line input
        destServer, destPort = str(sys.argv[6]), int(sys.argv[7])               # Get destination server name or IP and port number to connect to
    else:                                                                       # args must be less than 4 or greater than 6
        print(errorString)
        sys.exit()
    try:
        try:
            proxyListeningSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except:
            pass
        proxyListeningSocket.setblocking(0)                                         # Make socket non binding so that more than one connection can be made
        proxyListeningSocket.bind((HOST, srcPort))
        proxyListeningSocket.listen(5)                                              # Listen for connections and queue up to 5 of them
        print("\nPort logger running: srcPort=" + str(srcPort) + " host=" + destServer + " dstPort=" + str(destPort) + '\n')

        potential_readers = [proxyListeningSocket]
        potential_writers = []
        potential_errors = []

        dictionaryOfWriters = {}                                                    # will hold pairs of (A, B) where A writes only to B
        dictionaryOfClientWriters ={}
        while potential_readers:
            ready_to_read, ready_to_write, in_error = select.select(potential_readers, potential_writers, potential_errors)
            for sock in ready_to_read: #for each sock that has something to ready_to_read
                if sock is proxyListeningSocket: #then the thing being read is going to be a new local client conntection, which will need its own server connection
                    try:
                        remoteServerConn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                              # set up remote server connection for incoming client
                        remoteServerConn.connect((destServer,destPort))
                        localClientConn, clientAddress = sock.accept()                  # accept incoming local client
                    except:
                        pass

                    localClientConn.setblocking(0)                                  # double check that connection in non binding so more clients can connect
                    currentDateTime = datetime.datetime.now()
                    print("New connection: " + str(currentDateTime) + ", from " + str(clientAddress) + "\n" )
                    potential_readers.append(localClientConn)                       # add connection to those that may have something to read
                    potential_readers.append(remoteServerConn)
                    dictionaryOfClientWriters[localClientConn] = remoteServerConn         #now if localClientConn is ready_to_read, it will only do so from remoteServerConn
                    dictionaryOfWriters[remoteServerConn] = localClientConn         #and if remoteServerConn is ready_to_read, it will only do so from localClientConn
                else:
                    try:
                        dataFromSock = sock.recv(1024)                                  # get data in 1024 byte chunks
                        if dataFromSock: #i.e. not empty
                            linesOfData = dataFromSock.split(b'\n')
                            if loggingOption == "-strip":
                                linesOfData = removeNonPrintable(linesOfData)
                            if replaceOptions == "-replace":
                                linesOfData = replacePattern(linesOfData, replaceOpt1, replaceOpt2)
                            if sock in dictionaryOfWriters:
                                if loggingOption == "-raw" or loggingOption == "-strip":
                                    for line in linesOfData:
                                        sys.stdout.buffer.write(b' <--- ' + line + b'\n')
                                (dictionaryOfWriters[sock]).send(dataFromSock)              # send the data to socks pair in the dictionary
                            else:
                                if loggingOption == "-raw" or loggingOption == "-strip":
                                    for line in linesOfData:
                                        sys.stdout.buffer.write(b' ---> ' + line + b'\n')
                                (dictionaryOfClientWriters[sock]).send(dataFromSock)              # send the data to socks pair in the dictionary
                    except Exception as e:
                        pass
    except KeyboardInturrupt:
        print("Control-C detected. Closing proxy server...")
    finally:
        proxyListeningSocket.close()
        print("Listening socket closed.")
        sys.exit()
