import sys, fileinput

# Returns true if ip1 is in the CIDR block of ip2.
# ie. ip1 and ip2 have the same prefix
def checkCIDRPrefix(ip1, ip2):
    ip1Int = IPtoInt(ip1)
    if "/" in ip2:
        ip2, offset = ip2.split("/")
        ip2Int = IPtoInt(ip2)
        if maskIP(ip1Int, int(offset)) == maskIP(ip2Int, int(offset)):
            return True
        else:
            return False
    else:
        ip2Int = IPtoInt(ip2)
        if ip1Int == ip2Int:
            return True
        else:
            return False


# Returns an ip with its lower bits masked by an amount of (32 - <offset>)
# INPUT: int <ip>, int <number_of_higher_bits>
def maskIP(ip, offset):
    lowerBits = 32 - offset
    try:
        ip &= ~(2**lowerBits - 1)                               # AND the lower bits of the IP address with (32 - offset)
    except:
        print("Error: Invalid subnet mask " + "/" + str(offset) + "\nClosing firewall.", file = sys.stderr)
        sys.exit(0)
    return ip

# Convert IP in CIDR notation to an integer
def IPtoInt(IPString):
    ip = IPString.split(".")
    try:
        ipInt = (int(ip[0])*16777216) + (int(ip[1])*65536) + (int(ip[2])*256) + int(ip[3])     # ip[0]*2^24 + ip[1]*2^16 + ip[2]*2^8 + ip[3]*2^0
    except:
        print("Error: Invalid IP address " + str(IPString) + "\nClosing firewall.", file = sys.stderr)
        sys.exit(0)
    return ipInt

# Create dictionary of rules from a config file
# - rules are numbered by their line number in the config file
# - rules are also stored as a list of strings
def readConfig(configFile):
    try:
        config = open(configFile, 'r')
        for num, line in enumerate(config):
            line = line.split()                                     # Remove uneven whitespace
            if len(line) > 0 and line[0][0] != "#":                 # Reject lines that are empty or begin with a comment
                configDict[num+1] = line
    except:
        print("Error: Could not open file " + configFile + "\nClosing firewall.", file = sys.stderr)
        sys.exit(0)
    return

def filterPacket(packet):
    output = DEFAULT
    packet = packet.replace("\n", "")
    fields = packet.split()
    if len(fields) != 4:
        output += packet
        return output + packet
    rules = configDict.copy()
    for key in list(rules.keys()):
        if fields[0] != rules[key][0]:                              # Remove rule with a different direction than the packet's
            del rules[key]
        elif (fields[2] not in list(rules[key][3].split(","))) and (rules[key][3] != "*"):    # Remove rule that applies to ports that are different than the packet's
            del rules[key]
        elif (fields[3] == "0") and (len(rules[key]) == 5) and (rules[key][4] == "established"): # Remove rule for established packets when packet part of a new session
            del rules[key]
        elif (rules[key][2] != "*") and not(checkCIDRPrefix(fields[1], rules[key][2])):       # Remove rule that applies to a block of different IPs
            del rules[key]
    if len(rules) >= 1:
        key, value = rules.popitem()
        output = value[1] + "(" + str(key) + ")" + " " + packet
        return output
    elif len(rules) == 0:
        output += packet
        return output
    #TODO: QUESTION: If a packet is accepted under multiple rules, which takes precedence?
    # else:
    #     print("Error: FILTERING IS WRONG. Rules left " + str(list(rules.keys())))
    #     sys.exit(0)

def main():
    global configDict, ACCEPT, DROP, REJECT, DEFAULT

    if(len(sys.argv) == 2):
        configFile = str(sys.argv[1])
        configDict = {}
        ACCEPT = "accept"
        DROP = "drop"
        REJECT = "reject"
        DEFAULT = "drop() "
        readConfig(configFile)
        packet = sys.stdin.readline()
        while (packet):
            output = filterPacket(packet)
            #sys.stdout.write(output)
            print(output)
            packet = sys.stdin.readline()
    else:
        print("Error: wrong command line arguments.\nClosing firewall.", file = sys.stderr)

if __name__ == "__main__":
    main()
