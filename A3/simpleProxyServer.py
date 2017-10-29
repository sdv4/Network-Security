# Materials Referenced:
# https://docs.python.org/3/howto/sockets.html
# https://docs.python.org/2/tutorial/datastructures.html
# https://medium.com/@gdieu/build-a-tcp-proxy-in-python-part-1-3-7552cd5afdfe
# http://zguide.zeromq.org/py:interrupt
# https://stackoverflow.com/questions/2269827/how-to-convert-an-int-to-a-hex-string
# tutorial material: http://pages.cpsc.ucalgary.ca/~henrique.pereira/pdfs/cpsc526_fall17_tutorial11.pdf

#TODO: figure out if when how to close the sockets and return the "Connection closed" message

import string
import socket
import sys
import datetime
import select
import signal

global errorString
errorString = ("Usage: python3 proxyServer.py [logOptions] [replaceOptions]" +
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

#Input: bytestring and integer
#output: list of lines for output, each containing N bytes from input bytestring
def autoNOutput(byteData, N):
    newLines = []                                                               # each line holds 16 bytes of the original input string + offset and string
    stringAsByteArray = bytearray(byteData)                                         # convert bytestring to list of each byte an an element
    newln = ""
    charsProcessed = 0
    for c in stringAsByteArray:                                                 # for each character in the bytestring
        if c == 10:
            newln = newln + "\\n"
        elif c == 13:
            newln = newln + "\\r"
        elif c == 9:
            newln = newln + "\\t"
        elif c == 92:
            newln = newln + "\\"
        elif c < 32 or c > 127:
            newln = newln + "/" + hex(c)[2:4]                                       # convert its ascii int value to hex: 0x?? and use [2:4] to take only the last two
        else:
            newln = newln + chr(c)
        charsProcessed += 1
        if (charsProcessed % N) == 0 or charsProcessed == len(stringAsByteArray):
            newLines.append(newln.encode())
            newln = ""
    return newLines

# Function to prepare for display, the list of input strings, in Canonical
# hex+ascii form, as per the Linux utility hexdump with argument -C
# Input: A byte string
# Output: a list of bytestrings with 16 hex chars on each line, in format specified above
def hexDump(byteData):
    newLines = []                                                               # each line holds 16 bytes of the original input string + offset and string
    stringAsByteArray = bytearray(byteData)                                         # convert bytestring to list of each byte an an element
    newln = ""
    charsProcessed = 0
    pString = ""
    index = 0
    for c in stringAsByteArray:                                                 # replace \t \r \n with \\t \\r \\n resp.
        if c == 10:
            stringAsByteArray.insert(index, 92)
            stringAsByteArray[index+1] = 110
        if c == 13:
            stringAsByteArray.insert(index, 92)
            stringAsByteArray[index+1] = 114
        if c == 9:
            stringAsByteArray.insert(index, 92)
            stringAsByteArray[index+1] = 116
        index +=1

    for c in stringAsByteArray:                                                 # for each character in the bytestring
        newln = newln + hex(c)[2:4] + " "                                       # convert its ascii int value to hex: 0x?? and use [2:4] to take only the last two
        if c == 13:
            pString = pString + "\\r"
        elif c == 9:
            pString = pString + "\\t"
        elif c == 10:
            pString = pString + "\\n"
        else:
            pString = pString + chr(c)
        charsProcessed += 1
        if (charsProcessed % 16) == 0 or charsProcessed == len(stringAsByteArray):
            offset = str(16*(len(newLines))).zfill(8)                           # pad for up to 8 zeros
            numberOfCharsMissing = 16 - (charsProcessed % 16)                   # Number of spaces to add to right justify
            newln = offset + "    " + newln
            extraSpaces = 85 - len(newln)
            newln = newln + " "*extraSpaces + "|" + pString + "|"
            newLines.append(newln.encode())
            pString = ""
            newln = ""
    return newLines






if __name__ == "__main__":
    global destServer
    global destPort
    global HOST
    global loggingOption
    global replaceOptions
    global loggingOn

    cmdLineArgs = len(sys.argv)
    loggingOption  = ""
    replaceOptions = ""
    loggingOn = True
    if cmdLineArgs == 4:
        HOST, srcPort = "localhost", int(sys.argv[1])                           # Get port number to listen on as command line input
        destServer, destPort = str(sys.argv[2]), int(sys.argv[3])               # Get destination server name or IP and port number to connect to
        loggingOn = False
    elif cmdLineArgs == 5:
        loggingOption = str(sys.argv[1])
        HOST, srcPort = "localhost", int(sys.argv[2])                           # Get port number to listen on as command line input
        destServer, destPort = str(sys.argv[3]), int(sys.argv[4])               # Get destination server name or IP and port number to connect to
    elif cmdLineArgs == 6:
        loggingOption, replaceOptions = str(sys.argv[1]), str(sys.argv[2])
        HOST, srcPort = "localhost", int(sys.argv[3])                           # Get port number to listen on as command line input
        destServer, destPort = str(sys.argv[4]), int(sys.argv[5])               # Get destination server name or IP and port number to connect to
    else:                                                                       # args must be less than 4 or greater than 6
        print(errorString)
        sys.exit(0)
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
                        if len(dataFromSock) != 0: #i.e. not empty
                            if loggingOption == "-hex":
                                linesOfData = hexDump(dataFromSock)
                            elif loggingOption == "-autoN":
                                linesOfData = autoNOutput(dataFromSock, 30)     #TODO: be able to take additional argument for N
                            else:
                                linesOfData = dataFromSock.split(b'\n')
                            if loggingOption == "-strip":
                                linesOfData = removeNonPrintable(linesOfData)
                            if sock in dictionaryOfWriters:
                                if loggingOn:
                                    for line in linesOfData:
                                        sys.stdout.buffer.write(b' <--- ' + line + b'\n\r')
                                (dictionaryOfWriters[sock]).send(dataFromSock)              # send the data to socks pair in the dictionary
                            else:
                                if loggingOn:
                                    for line in linesOfData:
                                        sys.stdout.buffer.write(b' ---> ' + line + b'\n\r')
                                (dictionaryOfClientWriters[sock]).send(dataFromSock)              # send the data to socks pair in the dictionary
                        else:                                                   # That is, data is empty
                            #sock.close()
                            #print("Conncetion closed.\n")
                            pass
                    except Exception as e:
                        pass
    except KeyboardInterrupt:
        print("\nControl-C detected. Closing proxy server...")
        proxyListeningSocket.close()
        sys.exit(0)
