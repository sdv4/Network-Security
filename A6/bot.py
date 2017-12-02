#bot.py
import sys

def connectToIRC:

def sendMessage:

def joinChannel:

def leaveChannel:

def main():
    global HOSTNAME
    global PORT
    global CHANNEL
    global SECRET_PHRASE

    if len(sys.argv) == 5:
        HOSTNAME = str(sys.argv[1])
        PORT = int(sys.argv[2])
        CHANNEL = str(sys.argv[3])
        SECRET_PHRASE = str(sys.argv[4])

    else:
        print("Error: wrong command line arguments", file = sys.stderr)

if __name__ == "__main__":
    main()
