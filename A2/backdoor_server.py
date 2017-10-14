# CPSC 526 Assignment 2
# backdoor_server.py
# Authors: Shane Sims and Mason Lieu
# Basic TCP server code written by Pavol Federl
# version: 4 October 2017
#
# Run: backdoor_server.py port
# replacing port with desired port number
# Code references consulted or viewed:
# https://stackoverflow.com/questions/33001309/subprocess-call-cd-not-working
# TODO: delete unnecessary comments before submission. Just provided for learning
# purposes and so we can understand what is being done.

import os
import socketserver
import socket, threading
import sys
import subprocess                                                               # subprocess module will allow us to spawn new processes and connect to their
                                                                                # pipes to collect their return results

serverPassword = "thepass"                                           # Hard coded server password
snapOutput = ""

def printWorkingDir():
    procc = subprocess.Popen(["pwd"], stdout=subprocess.PIPE)
    result = procc.communicate()[0]
    return result.decode("utf-8")

def listContents():
    procc = subprocess.Popen(["ls", "-la"], stdout=subprocess.PIPE)
    result = procc.communicate()[0]
    return result.decode("utf-8")

def changeDirectory(dirName):
    os.chdir(dirName)

# Function to take a snapshot of all files in the current directory and saved
# results to memory. A snapshot will include file names and a hash of each file,
# which will be saved in a hidden text file in the working directory.
#TODO: remember to change md5 to md5sum before running on linux machine
def snap():
    global snapOutput
    #subprocess.run("> snapshot.txt", shell=True, stdout=subprocess.PIPE)
    procc = subprocess.Popen(["ls"], stdout=subprocess.PIPE)
    result = procc.communicate()[0]
    snapOutput = result.decode("utf-8")
    procc = subprocess.Popen("md5 *", stdout=subprocess.PIPE, shell=True)
    result = procc.communicate()[0]
    snapOutput = snapOutput + result.decode("utf-8")
    
# Function to terminate the server script
def turnServerOff():
    sys.exit()

def copyFile(file1, file2):
    procc = subprocess.Popen('cp -r ' + file1 + " " + file2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    result, err = procc.communicate()
    if err is not None:
        result = err
    return result.decode("utf-8")

def moveFile(file1, file2):
    procc = subprocess.Popen('mv ' + file1 + " " + file2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    result, err = procc.communicate()
    if err is not None:
        result = err
    return result.decode("utf-8")

def removeFile(file1):
    procc = subprocess.Popen('rm -f ' + file1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    result, err = procc.communicate()
    if err is not None:
        result = err
    return result.decode("utf-8")


def cat(file1):
    procc = subprocess.Popen('cat ' + file1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    result, err = procc.communicate()
    if len(result) < 1:
        result = err
    else:
        result = result + bytes("\n", "utf-8")
    return result.decode("utf-8")

# Override of handle method to handle functionality of the server
class MyTCPHandler(socketserver.BaseRequestHandler):                            # Create a request handler as subclass of BaseRequestHandler
    BUFFER_SIZE = 4096                                                           # Input buffer for client requests will be 4096 bytes
    PASSWORD_SIZE = 1024
    COMMAND_LIST = {
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
    def handle(self):                                                            # Override parent class handle method to handle incoming requests
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
                data = self.request.recv(self.BUFFER_SIZE)                       # self.request is the TCP socket connected to the client and recv stores command from client into data
                if len(data) == self.BUFFER_SIZE:                                # Client sent string of BUFFER_SIZE
                    while 1:                                                     # Check to see if there is more data in the string
                        try:  # error means no more data
                            data += self.request.recv(self.BUFFER_SIZE, socket.MSG_DONTWAIT)
                        except:
                            break
                if len(data) == 0:
                    break
                data = (data.decode( "utf-8")).strip()                                     # Decode received byte array to interpret command
                wordsInCommand = data.split()
                # Process client command
                if (wordsInCommand[0].lower() == "help"): #TODO add two more commands of our choosing to this list and implement
                    if (len(wordsInCommand) == 1) or not(wordsInCommand[1].lower() in self.COMMAND_LIST):
                        self.request.sendall( bytearray( "Supported commands:\n" + str(list(self.COMMAND_LIST)).strip('[]').replace('\'','') + "\n", "utf-8"))
                    else:
                        self.request.sendall( bytearray(self.COMMAND_LIST[wordsInCommand[1].lower()] + "\n", "utf-8"))
                elif data.lower() == "pwd" :
                    result = printWorkingDir()
                    self.request.sendall(bytearray(result, "utf-8"))
                elif wordsInCommand[0].lower() == "cd" :
                    if len(wordsInCommand) == 2:
                        changeDirectory(wordsInCommand[1])
                    else:
                        self.request.sendall( bytearray(self.COMMAND_LIST[wordsInCommand[0].lower()] + "\n", "utf-8"))
                elif data.lower() == "cp" :
                    result = printWorkingDir()
                    self.request.sendall(bytearray(result, "utf-8"))
                elif data.lower() == "ls" :
                    result = listContents()
                    self.request.sendall(bytearray(result, "utf-8"))
                elif wordsInCommand[0] == "mv" :
                    if len(wordsInCommand) == 3:
                        result = moveFile(wordsInCommand[1], wordsInCommand[2])
                        self.request.sendall(bytearray(result, "utf-8"))
                    else:
                        self.request.sendall( bytearray(self.COMMAND_LIST[wordsInCommand[0].lower()] + "\n", "utf-8"))
                elif wordsInCommand[0] == "rm" :
                    if len(wordsInCommand) == 2:
                        result = removeFile(wordsInCommand[1])
                        self.request.sendall(bytearray(result, "utf-8"))
                    else:
                        self.request.sendall( bytearray(self.COMMAND_LIST[wordsInCommand[0].lower()] + "\n", "utf-8"))
                elif wordsInCommand[0] == "cat" :
                    if len(wordsInCommand) == 2:
                        result = cat(wordsInCommand[1])
                        self.request.sendall(bytearray(result, "utf-8"))
                    else:
                        self.request.sendall( bytearray(self.COMMAND_LIST[wordsInCommand[0].lower()] + "\n", "utf-8"))
                elif data.lower() == "snap" :
                    result = listContents()
                    self.request.sendall(bytearray(result, "utf-8"))
                elif data.lower() == "cat" :
                    result = listContents()
                    self.request.sendall(bytearray(result, "utf-8"))
                elif data.lower() == "snap" :
                    snap()
                    self.request.sendall(bytearray("OK\n", "utf-8"))
                elif data.lower() == "diff" :
                    result = listContents()
                    self.request.sendall(bytearray(result, "utf-8"))
                elif data.lower() == "logout" :
                    break
                elif data.lower() == "off" :
                    turnServerOff()
                elif data.lower() == "test" :
                    self.request.sendall(bytearray(snapOutput, "utf-8"))
                elif data.lower() == "who" :
                    self.request.sendall(bytearray(self.client_address[0] + "\n", "utf-8"))
                else:
                    # TODO: deleted this echo of the command when other functionality is implemented
                    self.request.sendall( bytearray( "You said: " + data + "\n I do not understand that command.\n", "utf-8"))
                    print("%s (%s) wrote: %s" % (self.client_address[0],
                        threading.currentThread().getName(), data.strip()))
        else:
            self.request.sendall( bytearray( "Incorrect Password. Goodbye.\n", "utf-8"))

if __name__ == "__main__":
    HOST, PORT = "localhost", int(sys.argv[1])                                   # Get port number from command line
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)                  # Instantiate the threaded TCP server class and give it our handler
    server.serve_forever()                                                       # Instruct server to handle many requests
