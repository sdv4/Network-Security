#bot.py
import sys
import random
import socket
import string

# Function to get a nick with a high probability of being unique by using randomness
def getNick():
    rootOfName = "minion"
    candidateTail = ""
    for _ in range(6):
        candidateTail = candidateTail + str(random.choice(string.ascii_letters + string.digits))
    return (rootOfName + candidateTail)

# Function to connect to IRC server and send NICK and USER messages
def connectToIRC():
    #try:
        IRCconnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       # Create socket for TCP connection to IRC channet
        IRCconnection.connect((HOSTNAME,PORT))                                  # Connect to cmd line specified host and port
        #IRCconnection.settimeout(1)

        nickSet = False
        while(nickSet == False):
            candidateNick = getNick()
            NICK_Msg = "NICK " + candidateNick +"\r\n"                                # Construct NICK message
#            print(NICK_Msg)
            USER_Msg = "USER " + candidateNick + " * * :Not Yourconsern\r\n"        # Construct USER message
            IRCconnection.sendall(NICK_Msg.encode("utf-8"))                     # Send NICK message
            IRCconnection.sendall(USER_Msg.encode("utf-8"))
#            print(USER_Msg)
            NICK_Response = IRCconnection.recv(1024)                             # Recieve NICK response
            NICK_Response = NICK_Response.split()
#            print((NICK_Response[1]).decode("utf-8"))
            if((NICK_Response[1]).decode("utf-8") == "001"):
                nick = candidateNick                                            # If nick is not in use already, set global nick variable
                nickSet = True                                                  # Change nickSet flag to true


    #except Exception as e:
        #print("Error: " + str(e))
'''
def sendMessage():

def joinChannel():

def leaveChannel():

def authenticateController():

# Function that sends the nick of the bot to the controller
def sendStatus:

# Function that attacks hostName:hostPort by attempting to connect to hostName:hostPort
# and sending a string containing the attack count and nick of the bot. Sends status message
# to controler after attack is attempted
def attack(hostName, hostPort):

# Function to move bot from current IRC server to IRC server on hostName:hostPort #channel
# Will send status of migration attempt to controller on current IRC before disconnecting
def migrate(hostName, hostPort, channel):

# Function to shutdown the bot when instructed by controller.
def shutdownBot:
'''
def main():
    global HOSTNAME
    global PORT
    global CHANNEL
    global SECRET_PHRASE                                                        # Secret code word that IRC bot will listen for to ID controller
    global nick
    global attackCount                                                          # Counter for number of attacks executed by current instance of bot
    global controllerNick
    global IRCconnection


    if len(sys.argv) == 5:
        HOSTNAME = str(sys.argv[1])
        PORT = int(sys.argv[2])
        CHANNEL = str(sys.argv[3])
        SECRET_PHRASE = str(sys.argv[4])
        attackCount = 0

        connectToIRC()

    else:
        print("Error: wrong command line arguments", file = sys.stderr)

if __name__ == "__main__":
    main()
