import pytest
from matrix_lang_interpreter.scanner import Scanner


def test_literals():
    scanner = Scanner()
    text = "= + - * / @ ( ) [ ] { } : , ; < >"
    expected_tokens = [
        '=', '+', '-', '*', '/', '@', '(', ')', '[', ']',
        '{', '}', ':', ',', ';', '<', '>'
    ]
    for token, expected_token in zip(scanner.tokenize(text), expected_tokens):
        assert token.type == expected_token
        assert token.value == expected_token

def test_operators():
    scanner = Scanner()
    text = "+= -= *= /= <= >= != =="
    expected_tokens = [
        ('ADDASSIGN', '+='), ('SUBASSIGN', '-='), ('MULASSIGN', '*='),
        ('DIVASSIGN', '/='), ('LEQ', '<='), ('GEQ', '>='),
        ('NEQ', '!='), ('EQU', '==')
    ]
    for token, expected_token in zip(scanner.tokenize(text), expected_tokens):
        assert token.type == expected_token[0]
        assert token.value == expected_token[1]

def test_transpose():
    scanner = Scanner()
    text = 'A.T'
    expected_tokens = [
        ('ID', 'A'), ('TRANSPOSE', '.T')
    ]
    for token, expected_token in zip(scanner.tokenize(text), expected_tokens):
        assert token.type == expected_token[0]
        assert token.value == expected_token[1]

def test_keywords():
    scanner = Scanner()
    text = 'if else for while break continue return eye zeros ones print'
    expected_tokens = [
        ('IF', 'if'), ('ELSE', 'else'), ('FOR', 'for'), ('WHILE', 'while'),
        ('BREAK', 'break'), ('CONTINUE', 'continue'), ('RETURN', 'return'),
        ('EYE', 'eye'), ('ZEROS', 'zeros'), ('ONES', 'ones'), ('PRINT', 'print')
    ]
    for token, expected_token in zip(scanner.tokenize(text), expected_tokens):
        assert token.type == expected_token[0]
        assert token.value == expected_token[1]

def test_ids():
    scanner = Scanner()
    text = 'a foo bar12 foo_ foo_bar _foo'
    expected_tokens = [
        'a', 'foo', 'bar12', 'foo_', 'foo_bar', '_foo'
    ]
    for token, expected_token in zip(scanner.tokenize(text), expected_tokens):
        assert token.type == 'ID'
        assert token.value == expected_token

def test_floatnums():
    scanner = Scanner()
    text = '12. 12.3 0.1 .1 12E1 12e2 12E-1 2e-23 60.52e-2'
    expected_tokens = [
        12., 12.3, 0.1, .1, 12E1, 12e2, 12E-1, 2e-23, 60.52e-2
    ]
    for token, expected_token in zip(scanner.tokenize(text), expected_tokens):
        assert token.type == 'FLOATNUM'
        assert token.value == expected_token

def test_intnums():
    scanner = Scanner()
    text = '0 012 2 12 43'
    expected_tokens = [0, 12, 2, 12, 43]
    for token, expected_token in zip(scanner.tokenize(text), expected_tokens):
        assert token.type == 'INTNUM'
        assert token.value == expected_token

def test_strings():
    scanner = Scanner()
    text = "'foo bar'" + '"bar foo"'
    expected_tokens = ['foo bar', 'bar foo']
    for token, expected_token in zip(scanner.tokenize(text), expected_tokens):
        assert token.type == 'STRING'
        assert token.value == expected_token

def test_ignore_chars():
    scanner = Scanner()
    text = "a b		c	d"
    expected_tokens = ['a', 'b', 'c', 'd']
    for token, expected_token in zip(scanner.tokenize(text), expected_tokens):
        assert token.type == 'ID'
        assert token.value == expected_token

def test_ignore_comments():
    scanner = Scanner()
    text = "a c d # foo bar"
    expected_tokens = ['a', 'c', 'd']
    tokens = list(scanner.tokenize(text))
    assert len(tokens) == len(expected_tokens)
    for token, expected_token in zip(tokens, expected_tokens):
        assert token.type == 'ID'
        assert token.value == expected_token

def test_ignore_newline():
    scanner = Scanner()
    text = '''a b
    c

    d


    f
    g
    '''
    expected_tokens = [
        ('a', 1), ('b', 1), ('c', 2), ('d', 4), ('f', 7), ('g', 8)
    ]
    for token, expected_token in zip(scanner.tokenize(text), expected_tokens):
        assert token.type == 'ID'
        assert token.value == expected_token[0]
        assert token.lineno == expected_token[1]
