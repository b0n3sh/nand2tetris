#!venv/bin/python3

import parser
import code
import sys

if len(sys.argv) != 1:
    print("usage: ./assembler.py <assembly_file>")

file_path = "rect/Rect.asm"

# [+] First pass [+]
#   - Keep track of line number
#   - If label declaration is found (xxx) it keeps track of the line number, for posterior jumps 
parser_file = parser.Parser(file_path)
line_number = 0
while parser_file.hasMoreLines():
    next_instruction = parser_file.advance()
    print(f"{next_instruction} => {line_number}")
    line_number +=1
    

# Second pass 
parser_file = parser.Parser(file_path)
while parser_file.hasMoreLines():
    next_instruction = parser_file.advance()
    if parser_file.instructionType() == "C_INSTRUCTION":
        print(f"111{code.comp(parser_file.comp())}{code.dest(parser_file.dest())}{code.jump(parser_file.jump())}")
    elif parser_file.instructionType() == "A_INSTRUCTION":
        print(f"0{int(parser_file.symbol()):0>15b}") 
