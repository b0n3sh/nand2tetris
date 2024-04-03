#!venv/bin/python3

import argparse

import CodeWriter
from Parser import Parser

parser = argparse.ArgumentParser(description="Processes VM code into ASM code.")
parser.add_argument("filename", help="The filename that will be processed (VM code)")

args = parser.parse_args()
filename = args.filename

if ".vm" not in filename:
    raise ValueError("file must be a .VM file, with the correct extension")

file_parser = Parser(filename)
code_writer = CodeWriter.CodeWriter(filename)
while file_parser.has_more_lines():
    next_instruction = file_parser.advance()
    next_instruction_type = file_parser.command_type()
    if next_instruction_type == "C_PUSH" or next_instruction_type == "C_POP":
        code_writer.write_push_pop(next_instruction_type, file_parser.arg1(), file_parser.arg2())
    elif next_instruction_type == "C_ARITHMETIC":
        code_writer.write_arithmetic(file_parser.arg1())

# finish the code
code_writer.finish_him()

