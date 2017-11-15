import sys, fileinput

# Returns an ip with its lower bits masked by an amount of (32 - <offeset>)
# INPUT: int <ip>, int <number_of_higher_bits>
def maskIP(ip, offset):
    lowerBits = 32 - offset
    try:
        ip &= ~(2**lowerBits - 1)                               # XOR the lower bits of the IP address with (32 - offset)
    except:
        print("Error: Invalid routing mask " + str(offset), file = sys.stderr)
        sys.exit(0)
    return ip

# Convert IP in CIDR notation to an integer
def IPtoInt(IPString):
    ip = IPString.split(".")
    try:
        ipInt = (int(ip[0])*16777216) + (int(ip[1])*65536) + (int(ip[2])*256) + int(ip[3])     # ip[0]*2^24 + ip[1]*2^16 + ip[2]*2^8 + ip[3]*2^0
    except:
        print("Error: Invalid IP address " + str(IPString), file = sys.stderr)
        sys.exit(0)
    return ipInt

# Create dictionary of rules from a config file
# - rules are numbered by their line number in the config file
# - rules are also stored as a list of strings
def readConfig(configFile):
    try:
        config = open(configFile, 'r')
        configDict = {'':''}
        for num, line in enumerate(config):
            line = line.split()                                     # Remove uneven whitespace
            if len(line) > 0 and line[0][0] != "#":                 # Reject lines that are empty or begin with a comment
                configDict[num+1] = line
                print("DEBUG: Line", num+1, configDict[num+1])      #TODO: Delete this line. For testing only.
    except:
        print("Error: Could not open file " + configFile, file = sys.stderr)
        sys.exit(0)
    return

def main():
    global configDict

    if(len(sys.argv) == 2):
        configFile = str(sys.argv[1])

        #TODO: Delete the following block of code. For testing purposes only.
        readConfig(configFile)
        ipStr= ["255.255.255.255", "192.168.1.254", "192.168.1.255"]
        for ip in ipStr:
            print("IP: " + ip + " is " + "\n"
                    + str(bin(IPtoInt(ip))) + "\n" + str(bin(maskIP(IPtoInt(ip), 33))))

    else:
        print("Error: wrong command line arguments", file = sys.stderr)

if __name__ == "__main__":
    main()
