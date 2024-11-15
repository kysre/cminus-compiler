from collections import defaultdict

symbol_table = dict()
lexical_errors = defaultdict(list)
tokens = defaultdict(list)


class Config:
    SYMBOLS = [';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '/', '=', '<', '==']
    KEYWORDS = ['break', 'else', 'if', 'endif', 'int', 'while', 'return', 'void']
    WHITESPACES = [' ', '\n', '\r', '\t', '\v', '\f']


class TokenType:
    SYMBOL = 'SYMBOL'
    NUM = 'NUM'
    ID = 'ID'
    KEYWORD = 'KEYWORD'
    COMMENT = 'COMMENT'
    WHITESPACE = 'WHITESPACE'
    ID_OR_KEYWORD = 'ID_OR_KEYWORD'
    INVALID = 'Invalid input'
    EQUAL = 'EQUAL'


class Token:
    def __init__(self, line_number, token_type, value):
        self.line_number = line_number
        self.token_type = token_type
        self.value = value


def get_token_type(char):
    if char in Config.WHITESPACES:
        return TokenType.WHITESPACE
    elif char in Config.SYMBOLS:
        return TokenType.SYMBOL
    elif char.isdigit():
        return TokenType.NUM
    elif char.isalnum():
        return TokenType.ID_OR_KEYWORD
    elif char == '/':
        return TokenType.COMMENT
    else:
        return TokenType.INVALID


def init_symbol_table():
    symbol_table['keywords'] = Config.KEYWORDS
    symbol_table['ids'] = []


def is_id_or_keyword(name):
    for name1 in symbol_table["keywords"]:
        if name == name1:
            return TokenType.KEYWORD
    else:
        return TokenType.ID


def get_short_comment(comment):
    return comment[:7] + '...' if len(comment) >= 7 else comment


def save_errors():
    with open('lexical_errors.txt', 'w') as f:
        if lexical_errors:
            for line_num, line_error in lexical_errors.items():
                f.write(f'{line_num + 1}.' + "\t")
                for i in range(len(line_error)):
                    if i == len(line_error) - 1:
                        for char in range(len(line_error[i])):
                            f.write(f'{line_error[i][char]}')
                        f.write("\n")
                    else:
                        f.write(f'{line_error[i]} ')
        else:
            f.write('There is no lexical error.')


def save_tokens():
    with open('tokens.txt', 'w') as f:
        f.write('\n'.join(
            [f'{line_no + 1}.\t' + ' '.join([f'({token.token_type}, {token.value})' for token in line_tkns])
             for line_no, line_tkns in tokens.items()]))


def save_symbol_table():
    with open('symbol_table.txt', 'w') as f:
        f.write('\n'.join(
            [f'{idx + 1}.\t{symbol}' for idx, symbol in enumerate(symbol_table['keywords'] + symbol_table['ids'])]))


class Scanner:
    def __init__(self, input_path):
        self.input_path = input_path
        self.lines = None
        self.line_number = 0
        self.cursor = 0

    def scan_next_token(self):
        if self.eof_reached():
            return False
        char = self.get_current_char()
        token_type = get_token_type(char)
        if token_type == TokenType.WHITESPACE:
            if char == '\n':
                self.line_number += 1
            self.cursor += 1
            return self.scan_next_token()
        elif token_type == TokenType.SYMBOL:
            flag = 0

            if char == '*':
                if self.cursor < len(self.lines) - 1 \
                        and self.lines[self.cursor + 1] == '/':
                    self.cursor += 2
                    lexical_errors[self.line_number].append("(" + "*/" + ", Unmatched comment)")
                    return False
                elif self.cursor < len(self.lines) - 1 \
                        and get_token_type(self.lines[self.cursor + 1]) == TokenType.INVALID:
                    lexical_errors[self.line_number].append(
                        "(" + "*" + self.lines[self.cursor + 1] + ", Invalid input)")
                    self.cursor += 1
                    flag = 1

            elif char == '=':
                if self.cursor < len(self.lines) - 1 and self.lines[self.cursor + 1] == '=':
                    self.cursor += 2
                    return Token(self.line_number, TokenType.SYMBOL, '==')
                elif self.cursor < len(self.lines) - 1 and get_token_type(
                        self.lines[self.cursor + 1]) == TokenType.INVALID:
                    lexical_errors[self.line_number].append(
                        "(" + "=" + self.lines[self.cursor + 1] + ", Invalid input)")
                    self.cursor += 1
                    flag = 1

            self.cursor += 1
            if flag == 0:
                return Token(self.line_number, TokenType.SYMBOL, char)

        elif token_type == TokenType.NUM:
            number, error = self.is_number()
            if not error:
                return Token(self.line_number, TokenType.NUM, number)
            lexical_errors[self.line_number].append("(" + number + ", Invalid number)")

        elif token_type == TokenType.ID_OR_KEYWORD:
            name, error = self.find_id_or_keyword()
            if not error:
                return Token(self.line_number, is_id_or_keyword(name), name)
            lexical_errors[self.line_number].append("(" + name + ", Invalid input)")

        elif token_type == TokenType.COMMENT:
            self.find_comment()

        elif token_type == TokenType.INVALID:
            lexical_errors[self.line_number].append("(" + char + ", Invalid input)")
            self.cursor += 1

    def eof_reached(self):
        return self.cursor >= len(self.lines)

    def get_next_token(self):
        while True:
            if self.eof_reached():
                return '$'
            token = self.scan_next_token()
            if token:
                return token.line_number + 1, f'({token.token_type}, {token.value})'

    def init_input(self):
        with open(self.input_path, 'r') as f:
            self.lines = ''.join([line for line in f.readlines()])

    def scan_tokens(self):
        with open(self.input_path, 'r') as f:
            self.lines = ''.join([line for line in f.readlines()])
        while True:
            if self.eof_reached():
                break
            token = self.scan_next_token()
            if token:
                tokens[token.line_number].append(token)
                if token.token_type == TokenType.ID and token.value not in symbol_table['ids']:
                    symbol_table['ids'].append(token.value)

    def get_current_char(self):
        return self.lines[self.cursor]

    def is_number(self):
        num = self.get_current_char()
        while self.cursor + 1 < len(self.lines):
            self.cursor += 1
            next_char = self.get_current_char()
            temp_type = get_token_type(next_char)
            if temp_type == TokenType.NUM:
                num += next_char
            elif temp_type == TokenType.WHITESPACE or temp_type == TokenType.SYMBOL:
                return num, False
            else:  # invalid num
                num += next_char
                self.cursor += 1
                return num, True
        self.cursor += 1
        return num, False

    def find_id_or_keyword(self):
        name = self.get_current_char()
        while self.cursor + 1 < len(self.lines):
            self.cursor += 1
            temp_char = self.get_current_char()
            temp_type = get_token_type(temp_char)
            if temp_type == TokenType.NUM or temp_type == TokenType.ID_OR_KEYWORD:
                name += temp_char
            elif temp_type == TokenType.WHITESPACE or temp_type == TokenType.SYMBOL:
                return name, False
            else:
                name += temp_char
                self.cursor += 1
                return name, True

    def find_comment(self):
        beginning_line_number = self.line_number
        lexeme = self.get_current_char()
        if self.cursor + 1 == len(self.lines):
            lexical_errors[self.line_number].append("(" + lexeme + ", Invalid input)")  # last char is /
            self.cursor += 1
            return
        next_char = self.lines[self.cursor + 1]
        if next_char not in ['*']:
            if get_token_type(next_char) == TokenType.WHITESPACE:
                lexical_errors[self.line_number].append("(" + lexeme + ", Invalid input)")
                if next_char == "\n":
                    self.cursor += 1
                else:
                    self.cursor += 2
            elif get_token_type(next_char) == TokenType.SYMBOL or get_token_type(next_char) == TokenType.NUM:
                lexical_errors[self.line_number].append("(" + lexeme + ", Invalid input)")
                self.cursor += 1
            elif get_token_type(next_char) == TokenType.COMMENT:
                lexical_errors[self.line_number].append("(" + lexeme + ", Invalid input)")
                self.cursor += 1
            else:
                lexical_errors[self.line_number].append("(" + lexeme + next_char + ", Invalid input)")
                self.cursor += 2
            return

        is_multiline = next_char == '*'

        while self.cursor + 1 < len(self.lines):
            self.cursor += 1
            temp_char = self.get_current_char()
            if is_multiline:
                if self.cursor + 1 < len(self.lines):
                    if temp_char == '*' and self.lines[self.cursor + 1] == '/':
                        self.cursor += 2
                        lexeme += "*/"
                        return False
                else:
                    self.cursor += 1
                    lexical_errors[beginning_line_number].append(
                        "(" + get_short_comment(lexeme) + ", Unclosed comment)")
                    return None, True
            if temp_char == '\n':
                self.line_number += 1
            lexeme += temp_char
        self.cursor += 1
        return lexeme, False
