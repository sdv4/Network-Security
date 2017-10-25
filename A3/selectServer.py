import socket
import select
import sys


port1 = socket.socket() #listening port?
port1.setblocking(0) #make socket non blocking so others can connections
port1.bind(("0.0.0.0",8003)) #bind port to port 8000 on local host
port1.listen()  #tell socket to listen for conenctions

port2 = socket.socket() # ? what is this port for
port2.setblocking(0)
port2.bind(("0.0.0.0", 8004))
port2.listen() # tell socket to listen on port 8001

#these will be used for the select library
inputs = [port1, port2]
outputs = []

#while there is a connection from the client side, loop
while inputs: #while there are inputs, loop
    readable, writable, exception = select.select(inputs, outputs, inputs)       # sockets in readable are ones we are reading from, ect
    #could also leave last two empty
    #now try to read all data in readable list
    for sock in readable: #for each socket that
        if sock is port1 or sock is port2:
            connection, client_address = sock.accept()
            connection.setblocking(0) #just incase, to ensure the same after connecting
            #now we have a client connected, so we add it to inputs
            inputs.append(connection)
        else: #if we are connected , try to recieve the data
            data = sock.recv(1024) # read in 1024 byte chunks
            if data: #i.e. not empty
                print("<--- %s to %s" % (data, sock))
                #this part is different that A3, but we can manipulate it to suit us
                if sock not in outputs: #write back to same socket
                    outputs.append(sock)
    for sock in writable:
        print("---> %s to %s" % (data, sock)) #print what we are sending to console
        sock.send(b"some message")
        outputs.remove(sock) #remove the socket since we are done with it now
