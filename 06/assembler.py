#!venv/bin/python3

import parser
import code
import sys

# Creates a varaible 
def create_variable(symbol, variable_index):
    code.sym_map[symbol] = variable_index

if len(sys.argv) != 2 or ".asm" not in sys.argv[1]:
    print("usage: ./assembler.py <assembly_file>")
    exit()

file_path = sys.argv[1] 
print(file_path)

print("""[+] Doing first pass... [+]
   - Keep track of line number
   - If label declaration is found (xxx) it keeps track of the line number, for posterior jumps 
""")

# [+] First pass [+]
#   - Keep track of line number
#   - If label declaration is found (xxx) it keeps track of the line number, for posterior jumps 
parser_file = parser.Parser(file_path)
line_number = 0
while parser_file.hasMoreLines():
    next_instruction = parser_file.advance()
    if next_instruction[0] == "(":
        code.sym_map[next_instruction[1:-1]] = line_number
    else:
        line_number +=1

print("""[+] Doing second pass... [+]
    - Generating the machine code
""")


# Second pass 

with open(sys.argv[1].split(".asm")[0]+".hack", "w") as c:
    parser_file = parser.Parser(file_path)
    variable_index = 16
    while parser_file.hasMoreLines():
        next_instruction = parser_file.advance()
        if parser_file.instructionType() == "C_INSTRUCTION":
            print(f"111{code.comp(parser_file.comp())}{code.dest(parser_file.dest())}{code.jump(parser_file.jump())}", file=c)
        elif parser_file.instructionType() == "A_INSTRUCTION":
            # constant number 
            if parser_file.symbol().isnumeric():
                print(f"0{int(parser_file.symbol()):0>15b}", file=c) 
            # labels or predefined symbols
            elif parser_file.symbol() in code.sym_map:
                print(f"0{int(code.sym_map[parser_file.symbol()]):0>15b}", file=c)
            # variables
            else:
                create_variable(parser_file.symbol(), variable_index)
                print(f"0{int(code.sym_map[parser_file.symbol()]):0>15b}", file=c)
                variable_index += 1

print("Done, file created in the same folder with the same name but with .hack extension")
