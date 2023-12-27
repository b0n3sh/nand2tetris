#!venv/bin/python3

import parser
import code
import sys

if len(sys.argv) != 1:
    print("usage: ./assembler.py <assembly_file>")

file_path = "add/Add.asm"

parser_file = parser.Parser(file_path)

while parser_file.hasMoreLines():
    print(parser_file.advance())

