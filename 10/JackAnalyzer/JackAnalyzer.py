#!venv/bin/python3

import argparse

parser = argparse.ArgumentParser(
                    prog="JackAnalyzer",
                    description="First part of the compiler",
                    epilog="Implementation by b0n3sh - NAND2Tetris '25")

parser.add_argument("filename", help=".jack file or folder with .jack files")
parser.parse_args()
