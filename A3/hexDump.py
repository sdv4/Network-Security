def hexDump(byteData):
    newLines = []                                                               # each line holds 16 bytes of the original input string + offset and string
    stringAsByteArray = bytearray(byteData)                                         # convert bytestring to list of each byte an an element
    newln = ""
    charsProcessed = 0
    pString = ""
    for c in stringAsByteArray:                                                 # for each character in the bytestring
        newln = newln + hex(c)[2:4] + " "                                             # convert its ascii int value to hex: 0x?? and use [2:4] to take only the last two
        pString = pString + chr(c)
        charsProcessed += 1
        if charsProcessed % 16 == 0 or charsProcessed == len(stringAsByteArray):
            offset = str(16*(len(newLines))).zfill(8)                                    # pad for up to 8 zeros
            newln = offset + "    " + newln + "        " + "|" + pString + "|"
            newLines.append(newln.encode())
            pString = ""
            newln = ""
    return newLines

def autoNOutput(byteData, N):
    newLines = []                                                               # each line holds 16 bytes of the original input string + offset and string
    stringAsByteArray = bytearray(byteData)                                         # convert bytestring to list of each byte an an element
    newln = ""
    charsProcessed = 0
    for c in stringAsByteArray:                                                 # for each character in the bytestring
        if c == 10:
            newln = newln + "\\n"
        elif c == 13:
            newln = newln + "\\r"
        elif c == 9:
            newln = newln + "\\t"
        elif c == 92:
            newln = newln + "\\"
        elif c < 32 or c > 127:
            newln = newln + "/" + hex(c)[2:4]                                       # convert its ascii int value to hex: 0x?? and use [2:4] to take only the last two
        else:
            newln = newln + chr(c)
        charsProcessed += 1
        if (charsProcessed % N) == 0 or charsProcessed == len(stringAsByteArray):
            newLines.append(newln.encode())
            newln = ""
    return newLines

line = b'hello this is the times of our lives hello \n this \nis the times of \r\rour lives hello this is the times of our lives'
autoNlines = autoNOutput(line, 10)
for l in autoNlines:
    print(l)
