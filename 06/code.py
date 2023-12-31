#!venv/bin/python3

dest_map = {
    # dest
    "null": "000",
    "M": "001",
    "D": "010",
    "DM": "011",
    "MD": "011",
    "A": "100",
    "AM": "101",
    "MA": "101",
    "AD": "110",
    "DA": "110",
    "ADM": "111",
    "AMD": "111",
    "MAD": "111",
    "MDA": "111",
    "DAM": "111",
    "DMA": "111",
}
 
jump_map = {
    # jump
    "null": "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111",
}

comp_map = {
    # comp
    "0": "0101010",
    "1": "0111111",
    "-1": "0111010",
    "D": "0001100",
    "A": "0110000",
    "M": "1110000",
    "!D": "0001101",
    "!A": "0110001",
    "!M": "1110001",
    "-D": "0001111",
    "-A": "0110011",
    "-M": "1110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "M+1": "1110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "M-1": "1110010",
    "D+A": "0000010",
    "A+D": "0000010",
    "D+M": "1000010",
    "M+D": "1000010",
    "D-A": "0010011",
    "D-M": "1010011",
    "A-D": "0000111",
    "M-D": "1000111",
    "D&A": "0000000",
    "A&D": "0000000",
    "D&M": "1000000",
    "M&D": "1000000",
    "D|A": "0010101",
    "A|D": "0010101",
    "D|M": "1010101",
    "M|D": "1010101",
}

sym_map = {
    # symbols (predefined, label and variables)
    "R0": "0",
    "R1": "1",
    "R2": "2",
    "R3": "3",
    "R4": "4",
    "R5": "5",
    "R6": "6",
    "R7": "7",
    "R8": "8",
    "R9": "9",
    "R10": "10",
    "R11": "11",
    "R12": "12",
    "R13": "13",
    "R14": "14",
    "R15": "15",
    "SP": "0",
    "LCL": "1",
    "ARG": "2",
    "THIS": "3",
    "THAT": "4",
    "SCREEN": "16384",
    "KBD": "24576",
}

# Returns the binary code of the dest mnemonic
def dest(string):
    try:
        return dest_map[string]
    except KeyError as e:
        print(f"The following destination code does not exist: {e}")
        exit()

# Returns the binary code of the comp mnemonic
def comp(string):
    try:
        return comp_map[string]
    except KeyError as e:
        print(f"The following computation code does not exist: {e}")
        exit()

# Returns the binary code of the jump mnemonic
def jump(string):
    try:
        return jump_map[string]
    except KeyError as e:
        print(f"The following jump code does not exist: {e}")
        exit()
