import sys, fileinput

# Returns true if ip1 is in the CIDR block of ip2.
# ie. ip1 and ip2 have the same prefix
# OUTPUT: True if IPs are the same or part of the same CIDR block, False otherwise
def checkCIDRPrefix(ip1, ip2):
    ip1Int = IPtoInt(ip1)
    if "/" in ip2:                                                  # If a CIDR block was given as ip2, check that the prefix is the same between both IPs
        ip2, offset = ip2.split("/")
        ip2Int = IPtoInt(ip2)
        if maskIP(ip1Int, int(offset)) == maskIP(ip2Int, int(offset)):
            return True
        else:
            return False
    else:                                                           # Otherwise two IP addresses should be compared bit-by-bit
        ip2Int = IPtoInt(ip2)
        if ip1Int == ip2Int:
            return True
        else:
            return False


# Returns an ip with its lower bits masked by an amount of (32 - <offset>)
# INPUT: Int <ip>, Int <number_of_higher_bits>
# OUTPUT: Int <ip> - with masked bits
def maskIP(ip, offset):
    lowerBits = 32 - offset
    try:
        ip &= ~(2**lowerBits - 1)                               # AND the lower bits of the IP address with (32 - offset)
    except:
        print("Error: Invalid subnet mask " + "/" + str(offset) + "\nClosing firewall.", file = sys.stderr)
        sys.exit(0)
    return ip

# Convert IP in CIDR notation to an integer
# OUTPUT: Int <ip>
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

# Filters packet based on the set of rules from the config file
# OUTPUT: String <output> - what is done with each packet
def filterPacket(packet):
    fields = packet.split()
    rules = configDict.copy()                                       # Create copy of rules

    for key in list(rules.keys()):                                  # Iterate through each rule from the config file dropping rules that do not apply to the packet
        if fields[0] != rules[key][0]:                              # Remove rule with a different direction than the packet's
            del rules[key]
        elif (fields[2] not in list(rules[key][3].split(","))) and (rules[key][3] != "*"):    # Remove rule where the ports do not match
            del rules[key]
        elif (fields[3] == "0") and (len(rules[key]) == 5) and (rules[key][4] == "established"): # Remove rule if the packet is not established and the rule is for established packets
            del rules[key]
        elif (rules[key][2] != "*") and not(checkCIDRPrefix(fields[1], rules[key][2])):       # Remove rule if the IP or CIDR block does not match the packet's IP
            del rules[key]

    if len(rules) >= 1:                                             # Take the first rule left in the set of rules. TODO: Ask about multiple rules applying to one packet. Case: packets1.txt (packet 5), rules1.txt (rule 2 and 6)
        key, value = rules.popitem()
        output = value[1] + "(" + str(key) + ")" + " " + ' '.join(fields)   #TODO: ' '.join(fields) makes it so that a '|' doesn't appear in the diff
        #output = value[1] + "(" + str(key) + ")" + " " + packet            #TODO: packet makes it so that a '|' appears in the diff
        return output
    elif len(rules) == 0:                                           # Drop the package as the default option when no rules apply
        output = DEFAULT + ' '.join(fields)
        #output = DEFAULT + packet                                  #TODO: See a few lines above
        return output
    #TODO: QUESTION: If a packet is accepted under multiple rules, which takes precedence?
    # else:
    #     print("Error: Too many rules apply. Rules left " + str(list(rules.keys())))
    #     sys.exit(0)

def main():
    global configDict, ACCEPT, DROP, REJECT, DEFAULT

    if(len(sys.argv) == 2):
        configFile = str(sys.argv[1])
        configDict = {}
        DEFAULT = "drop() "
        readConfig(configFile)
        packet = sys.stdin.readline()
        while (packet):
            output = filterPacket(packet)
            print(output)
            packet = sys.stdin.readline()
    else:
        print("Error: wrong command line arguments.\nClosing firewall.", file = sys.stderr)

if __name__ == "__main__":
    main()
