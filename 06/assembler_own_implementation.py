#!venv/bin/python3

#
# I made this assembler before reading the lectures, just to compare how deviateed from the correct answer I was. This assembler is fully functional and looks pretty elegant as it is, imo.
#

import sys
import re

symbol_map = {
    "standard": {
        "SP": 0,
        "LCL": 1,
        "ARG": 2,
        "THIS": 3,
        "THAT": 4,
        "SCREEN": 16384,
        "KBD": 24576,
    },
    "local": {},
}

commands_map = {
    # jump
    "JGT": [0,0,1],
    "JEQ": [0,1,0],
    "JGE": [0,1,1],
    "JLT": [1,0,0],
    "JNE": [1,0,1],
    "JLE": [1,1,0],
    "JMP": [1,1,1],
    # comp
    "0": [0,1,0,1,0,1,0],
    "1": [0,1,1,1,1,1,1],
    "-1": [0,1,1,1,0,1,0],
    "D": [0,0,0,1,1,0,0],
    "A": [0,1,1,0,0,0,0],
    "M": [1,1,1,0,0,0,0],
    "!D": [0,0,0,1,1,0,1],
    "-A": [0,1,1,0,0,1,1],
    "-M": [1,1,1,0,0,1,1],
    "D+1": [0,0,1,1,1,1,1],
    "A+1": [0,1,1,0,1,1,1],
    "M+1": [1,1,1,0,1,1,1],
    "D-1": [0,0,0,1,1,1,0],
    "A-1": [0,1,1,0,0,1,0],
    "M-1": [1,1,1,0,0,1,0],
    "D+A": [0,0,0,0,0,1,0],
    "A+D": [0,0,0,0,0,1,0],
    "D+M": [1,0,0,0,0,1,0],
    "M+D": [1,0,0,0,0,1,0],
    "D-A": [0,0,1,0,0,1,1],
    "D-M": [1,0,1,0,0,1,1],
    "A-D": [0,0,0,0,1,1,1],
    "M-D": [1,0,0,0,1,1,1],
    "D&A": [0,0,0,0,0,0,0],
    "A&D": [0,0,0,0,0,0,0],
    "D&M": [1,0,0,0,0,0,0], 
    "M&D": [1,0,0,0,0,0,0], 
    "D|A": [0,0,1,0,1,0,1],
    "A|D": [0,0,1,0,1,0,1],
    "D|M": [1,0,1,0,1,0,1],
    "M|D": [1,0,1,0,1,0,1],
}


if len(sys.argv) != 2:
    print("Usage: ./assembler.py [assembly_file]")
    exit()

FILE_NAME = sys.argv[1]

with open(FILE_NAME, "r") as f:
    lines = f.read().splitlines()

def process_symbols():
    line_index = 0
    for line in lines:
        line = line.strip()
        if line and line[0:2]!="//":    
            if line[0] == "(":
                if line[1:-1] not in symbol_map:
                    symbol_map[line[1:-1]] = line_index+1
            else:
                print(process_line(line))
            line_index += 1

def process_line(line):
    # A instruction
    if line[0] == "@":
        reg = re.search("(?<=@R)1?[012345]?", line)
        # R register (0 to 15), from RAM[0] to RAM[15]
        if reg:
            address = int(reg.group(0))
            address = f"{address:016b}"
            return address
        # Not R register, store the local variable as RAM[16..n]
        else:
            # Already cached variable
            if line[1:] not in symbol_map["local"]:
                address = symbol_map["local"][line[1:]] = len(symbol_map["local"])+16
            else:
                pass
            return f"{symbol_map['local'][line[1:]]:016b}"

    # C instruction
    else:
        # dest
        instruction = [0]*16
        # The 3 MSB are 1 in C instruction
        instruction[0:3] = [1]*3
        if re.search("=", line):
            commands = line.split("=")
            if "A" in commands[0]:
                instruction[-6] = 1
            if "D" in commands[0]:
                instruction[-5] = 1
            if "M" in commands[0]:
                instruction[-4] = 1

        # jump
        if re.search(";", line):
            commands = line.split(";")
            try:
                instruction[-3:] = commands_map[commands[1]]
            except:
                print("Problem fetching the jump field")
                exit()

        # comp
        if "=" in line and ";" in line:
            commands = line.split("=")[1].split(";")[0]
        elif "=" in line:
            commands = line.split("=")[1]
        elif ";" in line:
            commands = line.split(";")[0]
        instruction[3:10] = commands_map[commands]
    
        return(''.join([str(x) for x in instruction]))

# Extract symbols first
process_symbols()
