from collections import defaultdict

from anytree import AnyNode, RenderTree

import scanner
from scanner import *

EPSILON_SYMBOL = 'ε'
END_SYMBOL = '$'

root = AnyNode(id="Program")
syntax_errors = defaultdict(list)
parse_tree = list()

follow = follow_sets = {'Program': ['$'],
                        'DeclarationList': ['$', 'ID', ';', 'NUM', '(', '{', '}', 'break', 'if', 'while', 'return', '+',
                                            '-'],
                        'Declaration': ['$', 'ID', ';', 'NUM', '(', 'int', 'void', '{', '}', 'break', 'if', 'while',
                                        'return', '+', '-'], 'DeclarationInitial': [';', '[', '(', ')', ','],
                        'DeclarationPrime': ['$', 'ID', ';', 'NUM', '(', 'int', 'void', '{', '}', 'break', 'if',
                                             'while', 'return', '+', '-'],
                        'VarDeclarationPrime': ['$', 'ID', ';', 'NUM', '(', 'int', 'void', '{', '}', 'break', 'if',
                                                'while', 'return', '+', '-'],
                        'FunDeclarationPrime': ['$', 'ID', ';', 'NUM', '(', 'int', 'void', '{', '}', 'break', 'if',
                                                'while', 'return', '+', '-'], 'TypeSpecifier': ['ID'], 'Params': [')'],
                        'ParamList': [')'], 'Param': [')', ','], 'ParamPrime': [')', ','],
                        'CompoundStmt': ['$', 'ID', ';', 'NUM', '(', 'int', 'void', '{', '}', 'break', 'if', 'endif',
                                         'else', 'while', 'return', '+', '-'], 'StatementList': ['}'],
                        'Statement': ['ID', ';', 'NUM', '(', '{', '}', 'break', 'if', 'endif', 'else', 'while',
                                      'return', '+', '-'],
                        'ExpressionStmt': ['ID', ';', 'NUM', '(', '{', '}', 'break', 'if', 'endif', 'else', 'while',
                                           'return', '+', '-'],
                        'SelectionStmt': ['ID', ';', 'NUM', '(', '{', '}', 'break', 'if', 'endif', 'else', 'while',
                                          'return', '+', '-'],
                        'ElseStmt': ['ID', ';', 'NUM', '(', '{', '}', 'break', 'if', 'endif', 'else', 'while', 'return',
                                     '+', '-'],
                        'IterationStmt': ['ID', ';', 'NUM', '(', '{', '}', 'break', 'if', 'endif', 'else', 'while',
                                          'return', '+', '-'],
                        'ReturnStmt': ['ID', ';', 'NUM', '(', '{', '}', 'break', 'if', 'endif', 'else', 'while',
                                       'return', '+', '-'],
                        'ReturnStmtPrime': ['ID', ';', 'NUM', '(', '{', '}', 'break', 'if', 'endif', 'else', 'while',
                                            'return', '+', '-'], 'Expression': [';', ']', ')', ','],
                        'B': [';', ']', ')', ','], 'H': [';', ']', ')', ','],
                        'SimpleExpressionZegond': [';', ']', ')', ','], 'SimpleExpressionPrime': [';', ']', ')', ','],
                        'C': [';', ']', ')', ','], 'Relop': ['ID', 'NUM', '(', '+', '-'],
                        'AdditiveExpression': [';', ']', ')', ','],
                        'AdditiveExpressionPrime': [';', ']', ')', ',', '<', '=='],
                        'AdditiveExpressionZegond': [';', ']', ')', ',', '<', '=='],
                        'D': [';', ']', ')', ',', '<', '=='], 'Addop': ['ID', 'NUM', '(', '+', '-'],
                        'Term': [';', ']', ')', ',', '<', '==', '+', '-'],
                        'TermPrime': [';', ']', ')', ',', '<', '==', '+', '-'],
                        'TermZegond': [';', ']', ')', ',', '<', '==', '+', '-'],
                        'G': [';', ']', ')', ',', '<', '==', '+', '-'], 'Mulop': ['ID', 'NUM', '(', '+', '-'],
                        'SignedFactor': [';', ']', ')', ',', '<', '==', '+', '-', '*', '/'],
                        'SignedFactorPrime': [';', ']', ')', ',', '<', '==', '+', '-', '*', '/'],
                        'SignedFactorZegond': [';', ']', ')', ',', '<', '==', '+', '-', '*', '/'],
                        'Factor': [';', ']', ')', ',', '<', '==', '+', '-', '*', '/'],
                        'VarCallPrime': [';', ']', ')', ',', '<', '==', '+', '-', '*', '/'],
                        'VarPrime': [';', ']', ')', ',', '<', '==', '+', '-', '*', '/'],
                        'FactorPrime': [';', ']', ')', ',', '<', '==', '+', '-', '*', '/'],
                        'FactorZegond': [';', ']', ')', ',', '<', '==', '+', '-', '*', '/'], 'Args': [')'],
                        'ArgList': [')'], 'ArgListPrime': [')']}

predict = {}
rules = 88 * [0]


def save_syntax_errors():
    del syntax_errors[1]
    with open('syntax_errors.txt', 'w') as f:
        if syntax_errors:
            f.write('\n'.join(['#' + f'{line_no}' + ' : syntax error, ' + f'{error}'
                               for line_no, errors in syntax_errors.items()
                               for error in errors]))
        else:
            f.write('There is no syntax error.')


def save_parse_tree():
    with open('parse_tree.txt', 'w') as f:
        f.write(RenderTree(root).by_attr('id'))


def init_first_follow():
    with open("resource/grammar_rules.txt") as f1, open("resource/predict.txt") as f2:
        for x, y in zip(f1, f2):
            elements = x.strip().split('    ', 1)
            rules[int(elements[0])] = elements[1]
            rule = elements[1].split('⟶', 1)
            left = rule[0]
            right = rule[1]
            if left not in predict:
                predict[left] = {}
            y = y.strip().split(', ')
            for first_for_rule in y:
                predict[left][first_for_rule] = right.split(' ')


def finish():
    save_parse_tree()
    save_syntax_errors()
    exit()


def is_terminal(a):
    if a in follow.keys():
        return False
    return True


def print_token(t):
    if type(t) is str:
        return t
    return '(' + t[0] + ', ' + t[1] + ')'


class Parser:
    def __init__(self, p_scanner):
        self.token = None
        self.parse_scanner = p_scanner
        self.parse_scanner.init_input()
        self.line_number = 0
        self.LA = str()

    def parse_program(self):
        self.update_la(root)
        self.dfa(root)
        AnyNode(id=END_SYMBOL, parent=root)
        finish()

    def update_la(self, nt_node):
        if self.LA == END_SYMBOL:
            nt_node.parent = None
            syntax_errors[self.line_number].append('Unexpected EOF')
            finish()
        self.token = self.parse_scanner.get_next_token()
        if type(self.token) is str:
            # EOF
            self.LA = self.token
        else:
            self.line_number = self.token[0]
            self.token = self.token[1]
            self.LA = scanner.get_type(self.token[1])

    def dfa(self, nt_node):
        state = nt_node.id
        if self.LA in predict[state]:
            path = predict[state][self.LA]
            if len(path) == 1 and path[0] == EPSILON_SYMBOL:
                # epsilon
                AnyNode(id="epsilon", parent=nt_node)
                return
            else:
                for next in path:
                    if not is_terminal(next):
                        next_nt_node = AnyNode(id=next, parent=nt_node)
                        self.dfa(next_nt_node)
                    elif self.LA == next:
                        AnyNode(id=print_token(self.token), parent=nt_node)
                        if self.LA != END_SYMBOL:
                            self.update_la(nt_node)
                    else:
                        syntax_errors[self.line_number].append('missing ' + next)
        else:
            # delete nt_node
            if self.LA in follow[state]:
                # sync
                nt_node.parent = None
                syntax_errors[self.line_number].append('missing ' + state)
                return
            else:
                # empty
                if self.LA != END_SYMBOL:
                    syntax_errors[self.line_number].append('illegal ' + self.LA)
                self.update_la(nt_node)
                self.dfa(nt_node)
                return
