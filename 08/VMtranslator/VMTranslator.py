#!venv/bin/python3

import argparse
import os

import CodeWriter
from Parser import Parser

parser = argparse.ArgumentParser(description="Processes VM code into ASM code.")
parser.add_argument("filename", help="The filename that will be processed (VM code)")

args = parser.parse_args()
filename = args.filename

def parse_file(file_parser):
    while file_parser.has_more_lines():
        next_instruction = file_parser.advance()
        next_instruction_type = file_parser.command_type()
        if next_instruction_type == "C_PUSH" or next_instruction_type == "C_POP":
            code_writer.write_push_pop(next_instruction_type, file_parser.arg1(), file_parser.arg2())
        elif next_instruction_type == "C_ARITHMETIC":
            code_writer.write_arithmetic(file_parser.arg1())
        elif next_instruction_type == "C_LABEL":
            code_writer.write_label(file_parser.arg1())
        elif next_instruction_type == "C_GOTO":
            code_writer.write_goto(file_parser.arg1())
        elif next_instruction_type == "C_IF":
            code_writer.write_if(file_parser.arg1())
        elif next_instruction_type == "C_FUNCTION":
            code_writer.write_function(file_parser.arg1(), file_parser.arg2())
        elif next_instruction_type == "C_CALL":
            code_writer.write_call(file_parser.arg1(), file_parser.arg2())
        elif next_instruction_type == "C_RETURN":
            code_writer.write_return()

if ".vm" in filename or os.path.isdir(filename):
    is_dir = os.path.isdir(filename)
    if is_dir:
        dir_name = os.path.split(os.path.abspath(filename))[1]
        code_writer = CodeWriter.CodeWriter(dir_name)
        code_writer.bootstrap()
        for filename_rel in os.listdir(filename):
            if ".vm" in filename_rel:
                code_writer.set_file_name(filename_rel)
                file_parser = Parser(os.path.join(filename, filename_rel))
                parse_file(file_parser)
    else:
        file_parser = Parser(filename)
        code_writer = CodeWriter.CodeWriter(filename)
        code_writer.setFileName(filename)
        code_writer.bootstrap()
        parse_file(file_parser)
else: 
    raise ValueError("file must be a .VM file, with the correct extension")

# finish the code
code_writer.finish_him()
