# Kasra Hajian    99109411
from scanner import *
from parser import *

if __name__ == '__main__':
    init_symbol_table()
    init_first_follow()
    compiler_scanner = Scanner("input.txt")
    compiler_parser = Parser(compiler_scanner)
    compiler_parser.parse_program()
