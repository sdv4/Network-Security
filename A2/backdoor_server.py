# CPSC 526 Assignment 2
# backdoor_server.py
# Authors: Shane Sims and Mason Lieu
# Basic TCP server code written by Pavol Federl
# version: 4 October 2017
#
# Run: backdoor_server.py port
# replacing port with desired port number
# Code references consulted or viewed:
# TODO: delete unnecessary comments before submission. Just provided for learning
# purposes and so we can understand what is being done.

import os
import socketserver
import socket, threading
import sys
import subprocess


serverPassword = "thepass"                                                      # Hard coded server password
snapOutput = ""
currentView = ""                                                                # Will hold a new snap without erasing last client initiated snap

COMMAND_LIST = {                                                                # Dictionary of help commands and execution instructions.
'pwd': 'pwd  - shows current working directory',
'cd': 'cd <dir> - change current working directory to <dir>',
'ls': 'ls - list contents of the current working directory',
'cp': 'cp <file1> <file2> - copy file1 to file2',
'mv': 'mv <file1> <file2> - rename file1 to file2',
'rm': 'rm <file> - delete file',
'cat': 'cat <file> - return contents of the file',
'snap': 'snap - takes a snapshot of all the files in the current directory',
'diff': 'diff - compares the content of the current directory to the saved snapshot',
'help': 'help - list command options\nhelp <cmd> - show detailed help for given cmd',
'logout': 'logout - disconnect client',
'off': 'off - terminate the backdoor program',
'opt1': 'PLACEHOLDER',
'opt2': 'PLACEHOLDER',
}

def printWorkingDir():
    procc = subprocess.Popen(["pwd"], stdout=subprocess.PIPE)
    result = procc.communicate()[0]
    return result.decode("utf-8")

def listContents():
    procc = subprocess.Popen(["ls", "-la"], stdout=subprocess.PIPE)
    result = procc.communicate()[0]
    return result.decode("utf-8")

def changeDirectory(listOfWords):
    if len(listOfWords) == 2:
        os.chdir(listOfWords[1])
        result = ""
    else:
        result = COMMAND_LIST[listOfWords[0].lower()] + "\n"
    return result

# Function to take a snapshot of all files in the current directory and saved
# results to memory. A snapshot will include file names and a hash of each file,
# which will be saved in a hidden text file in the working directory.
#TODO: remember to change md5 to md5sum before running on linux machine
def snap(locationToSaveSnap):
    global currentView
    global snapOutput
    procc = subprocess.Popen(["ls"], stdout=subprocess.PIPE)
    result = procc.communicate()[0]
    tempString = result.decode("utf-8")
    procc = subprocess.Popen("md5 *", stdout=subprocess.PIPE, shell=True)
    result = procc.communicate()[0]
    tempString = tempString + result.decode("utf-8")
    if locationToSaveSnap == 1:
        snapOutput = tempString
    else :
        currentView = tempString

# Function to compare the contents of the current directory with the most recent
# snapshot. If no snapshot has been taken, an error message is returned.
def checkDifference():
    global snapOutput
    global currentView
    snap(2)                                                                     # Save current view of directory to currentView
    result = ""
    if snapOutput == "" :
        return "ERROR: no snapshot\n"
    elif currentView == snapOutput :
        return "No change\n"
    else:
        stringOfDifferences = ""                                                # Start recording differences
        listOfDiff = currentView.split("\n")
        listOfSnap = snapOutput.split("\n")
        lenListOfSnap = len(listOfSnap)
        for i in range(int(lenListOfSnap/2)) :                                  # Compare each file in the saved snapshot -
            for j in range(int(len(listOfDiff)/2)) :                            # - to each file currently in the directory -
                if listOfSnap[i] == listOfDiff[j] :                             # - and if the same file exists in both lists -
                    if listOfSnap[i+(int(lenListOfSnap/2))].find(listOfSnap[i]) == -1: # - compare their hashes -
                        neverPrinted = "never printed"                          # - and if they are same, then there was no change -
                    elif listOfSnap[i+(int(lenListOfSnap/2))] != listOfDiff[j+(int(len(listOfDiff)/2))] : # - if the hashes don't match -
                        stringOfDifferences = stringOfDifferences + listOfSnap[i] + " - was changed\n" # then record the change
                    listOfDiff.pop(j)
                    listOfDiff.pop(j+(int(len(listOfDiff)/2)))
                    break
            stringOfDifferences = stringOfDifferences + listOfSnap[i] + " - was deleted\n" # If the file in the snapshot wasn't found, record.
        for k in range(int(len(listOfDiff)/2)) :                                # The elements remaining are those added since last snap of current dir
            stringOfDifferences = stringOfDifferences + listOfDiff[k] + " - was added\n"
        return stringOfDifferences

# Function to terminate the server script
def turnServerOff():
    sys.exit()

def copyFile(file1, file2):
    procc = subprocess.Popen('cp -r ' + file1 + " " + file2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    result, err = procc.communicate()
    if err is not None:
        result = err
    return result.decode("utf-8")

def copyFile(listOfWords):
    if len(listOfWords) == 3:
        procc = subprocess.Popen('cp -r ' + listOfWords[1] + " " + listOfWords[2], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        result, err = procc.communicate()
        if err is not None:
            result = err
    else:
        result = COMMAND_LIST[listOfWords[0].lower()] + "\n"
    return result.decode("utf-8")

def moveFile(file1, file2):
    procc = subprocess.Popen('mv ' + file1 + " " + file2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    result, err = procc.communicate()
    if err is not None:
        result = err
    return result.decode("utf-8")

def moveFile(listOfWords):
    if len(listOfWords) == 3:
        procc = subprocess.Popen('mv ' + listOfWords[1] + " " + listOfWords[2], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        result, err = procc.communicate()
        if err is not None:
            result = err
    else:
        result = COMMAND_LIST[listOfWords[0].lower()] + "\n"
    return result.decode("utf-8")

def removeFile(listOfWords):
    if len(listOfWords) == 2:
        procc = subprocess.Popen('rm -f ' + listOfWords[1], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        result, err = procc.communicate()
        if err is not None:
            result = err
    else:
        result = COMMAND_LIST[listOfWords[0].lower()] + "\n"
    return result.decode("utf-8")

def cat(listOfWords):
    if len(listOfWords) == 2 :
        procc = subprocess.Popen('cat ' + listOfWords[1], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        result, err = procc.communicate()
        if len(result) < 1:
            result = err
        return result.decode("utf-8")
    else:
        return COMMAND_LIST[listOfWords[0].lower()] + "\n"

def runningProcesses():
    procc = subprocess.Popen("ps", stdout=subprocess.PIPE, shell=True)
    result = procc.communicate()[0]

def helpCommand(listOfWords):
    if (len(listOfWords) == 1) or not(listOfWords[1].lower() in COMMAND_LIST):
        result = "Supported commands:\n" + str(list(COMMAND_LIST)).strip('[]').replace('\'','') + "\n"
        return result
    else:
        result = COMMAND_LIST[listOfWords[1].lower()] + "\n"
        return result

# Override of handle method to handle functionality of the server
class MyTCPHandler(socketserver.BaseRequestHandler):                            # Create a request handler as subclass of BaseRequestHandler

    BUFFER_SIZE = 4096                                                          # Input buffer for client requests will be 4096 bytes
    PASSWORD_SIZE = 1024

    def handle(self):                                                           # Override parent class handle method to handle incoming requests
        # Authenticate user via hardcoded password
        self.request.sendall( bytearray( "Enter Password: ", "utf-8"))
        clientPassword = self.request.recv(self.PASSWORD_SIZE)
        clientPassword = clientPassword.decode("utf-8")
        clientPassword = clientPassword.strip()
        if clientPassword == serverPassword:
            self.request.sendall(bytearray( "Password correct. Welcome.\n", "utf-8"))
            # Accept commands from authenticated user
            while 1:
                # Receive user command
                self.request.sendall(bytearray("> ", "utf-8"))
                data = self.request.recv(self.BUFFER_SIZE)                      # self.request is the TCP socket connected to the client and recv stores command from client into data
                if len(data) == self.BUFFER_SIZE:                               # Client sent string of BUFFER_SIZE
                    while 1:                                                    # Check to see if there is more data in the string
                        try:                                                    # error means no more data
                            data += self.request.recv(self.BUFFER_SIZE, socket.MSG_DONTWAIT)
                        except:
                            break
                if len(data) == 0:
                    break
                data = (data.decode( "utf-8")).strip()                          # Decode received byte array to interpret command
                wordsInCommand = data.split()
                # Process client command
                if (wordsInCommand[0].lower() == "help"):
                    result = helpCommand(wordsInCommand)
                    self.request.sendall( bytearray(result, "utf-8"))
                elif data.lower() == "pwd" :
                    result = printWorkingDir()
                    self.request.sendall(bytearray(result, "utf-8"))
                elif wordsInCommand[0].lower() == "cd" :
                    result = changeDirectory(wordsInCommand)
                    self.request.sendall( bytearray(result, "utf-8"))
                elif data.lower() == "cp" :
                    result = copyFile(wordsInCommand)
                    self.request.sendall(bytearray(result, "utf-8"))
                elif data.lower() == "ls" :
                    result = listContents()
                    self.request.sendall(bytearray(result, "utf-8"))
                elif wordsInCommand[0] == "mv" :
                    result = moveFile(wordsInCommand)
                    self.request.sendall(bytearray(result, "utf-8"))
                elif wordsInCommand[0] == "rm" :
                    result = removeFile(wordsInCommand)
                    self.request.sendall(bytearray(result, "utf-8"))
                elif wordsInCommand[0] == "cat" :
                    result = cat(wordsInCommand)
                    self.request.sendall(bytearray(result, "utf-8"))
                elif data.lower() == "snap" :
                    snap(1)
                    self.request.sendall(bytearray("OK\n", "utf-8"))
                elif data.lower() == "diff" :
                    result = checkDifference()
                    self.request.sendall(bytearray(result, "utf-8"))
                elif data.lower() == "logout" :
                    break
                elif data.lower() == "off" :
                    turnServerOff()
                elif data.lower() == "test" :#TODO: delete
                    self.request.sendall(bytearray(snapOutput, "utf-8"))
                elif data.lower() == "who" :
                    self.request.sendall(bytearray("Current User:\n" + self.client_address[0] + "\n", "utf-8"))
                elif data.lower() == "ps" :
                    result = runningProcesses()
                    self.request.sendall(bytearray("Current running processes: \n" + result, "utf-8"))
                else:
                    self.request.sendall( bytearray("You said: " + data + "\n I do not understand that command.\n", "utf-8"))
                print("%s (%s) wrote: %s" % (self.client_address[0],
                    threading.currentThread().getName(), data.strip()))
        else:
            self.request.sendall( bytearray("Incorrect Password. Goodbye.\n", "utf-8"))

if __name__ == "__main__":
    HOST, PORT = "localhost", int(sys.argv[1])                                   # Get port number from command line
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)                  # Instantiate the threaded TCP server class and give it our handler
    server.serve_forever()                                                       # Instruct server to handle many requests
