# Kasra Hajian    99109411
# Andia Torabi
from scanner import *

if __name__ == '__main__':
    init_symbol_table()
    scanner = Scanner("input.txt")
    scanner.scan_tokens()
    save_errors()
    save_tokens()
    save_symbol_table()
