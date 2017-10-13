# CPSC 526 Assignment 2
# backdoor_server.py
# Authors: Shane Sims and Mason Lieu
# Basic TCP server code written by Pavol Federl
# version: 4 October 2017
#
# Run: backdoor_server.py port
# replacing port with desired port number

# TODO: delete unnecessary comments before submission. Just provided for learning
# purposes and so we can understand what is being done.

import socketserver
import socket, threading
import sys
import subprocess                                                               # subprocess module will allow us to spawn new processes and connect to their
                                                                                # pipes to collect their return results

server_password = "thepasswordfornow"                                           # Hard coded server password

def printWorkingDir():
    procc = subprocess.Popen(["pwd"], stdout=subprocess.PIPE)
    result = procc.communicate()[0]
    return result.decode("utf-8")

def listContents():
    procc = subprocess.Popen(["ls"], stdout=subprocess.PIPE)
    result = procc.communicate()[0]
    return result.decode("utf-8")


# Override of handle method to handle functionality of the server
class MyTCPHandler(socketserver.BaseRequestHandler):                            # Create a request handler as subclass of BaseRequestHandler
   BUFFER_SIZE = 4096                                                           # Input buffer for client requests will be 4096 bytes
   PASSWORD_SIZE = 1024
   def handle(self):                                                            # Override parent class handle method to handle incoming requests
       # Authenticate user via hardcoded password
       self.request.sendall( bytearray( "Enter Password: ", "utf-8"))
       client_password = self.request.recv(self.PASSWORD_SIZE)
       client_password = client_password.decode("utf-8")
       client_password = client_password.strip()
       if client_password == server_password:
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
               if (data.lower() == "help"): #TODO add two more commands of our choosing to this list and implement
                   self.request.sendall( bytearray( "Supported commands:\n pwd, cd, cp, ls, mv, rm, cat, snap, diff, help, logout, off \n", "utf-8"))
               elif data.lower() == "pwd" :
                   result = printWorkingDir()
                   self.request.sendall(bytearray(result, "utf-8"))
               elif data.lower() == "cd" :
                   result = printWorkingDir()
                   self.request.sendall(bytearray(result, "utf-8"))
               elif data.lower() == "cp" :
                   result = printWorkingDir()
                   self.request.sendall(bytearray(result, "utf-8"))
               elif data.lower() == "ls" :
                   result = listContents()
                   self.request.sendall(bytearray(result, "utf-8"))
               elif data.lower() == "mv" :
                   result = listContents()
                   self.request.sendall(bytearray(result, "utf-8"))
               elif data.lower() == "rm" :
                   result = listContents()
                   self.request.sendall(bytearray(result, "utf-8"))
               elif data.lower() == "cat" :
                   result = listContents()
                   self.request.sendall(bytearray(result, "utf-8"))
               elif data.lower() == "snap" :
                   result = listContents()
                   self.request.sendall(bytearray(result, "utf-8"))
               elif data.lower() == "diff" :
                   result = listContents()
                   self.request.sendall(bytearray(result, "utf-8"))
               elif data.lower() == "logout" :
                   result = listContents()
                   self.request.sendall(bytearray(result, "utf-8"))
               elif data.lower() == "off" :
                   result = listContents()
                   self.request.sendall(bytearray(result, "utf-8"))


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
