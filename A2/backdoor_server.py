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
class MyTCPHandler(socketserver.BaseRequestHandler):                            # Create a request handler as subclass of BaseRequestHandler
   BUFFER_SIZE = 4096                                                           # Input buffer for client requests will be 4096 bytes
   def handle(self):                                                            # Override parent class handle method to handle incoming requests
       while 1:                                                                 # Keep taking requests from a connected client without dropping connection
           data = self.request.recv(self.BUFFER_SIZE)                           # self.request is the TCP socket connected to the client and recv stores command from client into data
           if len(data) == self.BUFFER_SIZE:
               while 1:
                   try:  # error means no more data
                       data += self.request.recv(self.BUFFER_SIZE, socket.MSG_DONTWAIT)
                   except:
                       break
           if len(data) == 0:
               break
           data = data.decode( "utf-8")
           self.request.sendall( bytearray( "You said: " + data, "utf-8"))
           print("%s (%s) wrote: %s" % (self.client_address[0],
                 threading.currentThread().getName(), data.strip()))

if __name__ == "__main__":
   HOST, PORT = "localhost", int(sys.argv[1])                                   # Get port number from command line
   server = socketserver.ThreadingTCPServer((HOST, PORT), MyTCPHandler)         # Instantiate the threaded TCP server classs and give it our handler
   server.serve_forever()                                                       # Instruct server to handle many requests
