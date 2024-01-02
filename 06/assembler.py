#!venv/bin/python3

import parser
import code
import sys

if len(sys.argv) != 1:
    print("usage: ./assembler.py <assembly_file>")

file_path = "rect/RectL.asm"

parser_file = parser.Parser(file_path)

# Iterae through each line
while parser_file.hasMoreLines():
    next_instruction = parser_file.advance()
    if parser_file.instructionType() == "C_INSTRUCTION":
        print(f"111{code.comp(parser_file.comp())}{code.dest(parser_file.dest())}{code.jump(parser_file.jump())}")
    elif parser_file.instructionType() == "A_INSTRUCTION":
        print(f"0{int(parser_file.symbol()):0>15b}") 
