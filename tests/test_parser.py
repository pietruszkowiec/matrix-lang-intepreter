import pytest
from matrix_lang_interpreter.scanner import Scanner
from matrix_lang_interpreter.parser import Parser, BinExpr, UnExpr


def test_literals():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        '1 + 2')) == BinExpr('+', 1, 2)
    assert parser.parse(scanner.tokenize(
        '1 - 2')) == BinExpr('-', 1, 2)
    assert parser.parse(scanner.tokenize(
        '2 * 3')) == BinExpr('*', 2, 3)
    assert parser.parse(scanner.tokenize(
        '3 / 2')) == BinExpr('/', 3, 2)
    assert parser.parse(scanner.tokenize(
        '(3 + 1) * 2')) == BinExpr('+', 1, 2)
    assert parser.parse(scanner.tokenize(
        '2 * (3 + 1)')) == 8
    assert parser.parse(scanner.tokenize(
        '-1')) == -1
    assert parser.parse(scanner.tokenize(
        '-(3 + 1)')) == -4

def test_precedence():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        '2 * 3 + 1')) == 7
    assert parser.parse(scanner.tokenize(
        '1 + 2 * 3')) == 7
    assert parser.parse(scanner.tokenize(
        '-1 + 2')) == 1
    assert parser.parse(scanner.tokenize(
        '2 + -1')) == 1
    assert parser.parse(scanner.tokenize(
        '-2 - 1')) == -3
    assert parser.parse(scanner.tokenize(
        '-1 * 2')) == -2
    assert parser.parse(scanner.tokenize(
        '2 * -1')) == -2

def test_outerlist():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        '''[[1]]'''
    )) == [[1]]
    assert parser.parse(scanner.tokenize(
        '''[[-1]]'''
    )) == [[-1]]
    assert parser.parse(scanner.tokenize(
        '''[[1, 2]]'''
    )) == [[1, 2]]
    assert parser.parse(scanner.tokenize(
        '''[[1, 2],
            [3, 4]]'''
    )) == [[1, 2],
           [3, 4]]

def test_zeros():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        'zeros(0)'
    )) == []
    assert parser.parse(scanner.tokenize(
        'zeros(1)'
    )) == [[0]]
    assert parser.parse(scanner.tokenize(
        'zeros(2)'
    )) == [[0, 0],
           [0, 0]]
    assert parser.parse(scanner.tokenize(
        'zeros(4)'
    )) == [[0, 0, 0, 0],
           [0, 0, 0, 0],
           [0, 0, 0, 0],
           [0, 0, 0, 0]]

def test_ones():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        'ones(1)'
    )) == [[1]]
    assert parser.parse(scanner.tokenize(
        'ones(2)'
    )) == [[1, 1],
           [1, 1]]
    assert parser.parse(scanner.tokenize(
        'ones(4)'
    )) == [[1, 1, 1, 1],
           [1, 1, 1, 1],
           [1, 1, 1, 1],
           [1, 1, 1, 1]]

def test_eye():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        'eye(1)'
    )) == [[1]]
    assert parser.parse(scanner.tokenize(
        'eye(2)'
    )) == [[1, 0],
           [0, 1]]
    assert parser.parse(scanner.tokenize(
        'eye(4)'
    )) == [[1, 0, 0, 0],
           [0, 1, 0, 0],
           [0, 0, 1, 0],
           [0, 0, 0, 1]]

def test_dotadd():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        '[[1]] .+ [[2]]'
    )) == [[3]]
    assert parser.parse(scanner.tokenize(
        '[[1, 2]] .+ [[3, 4]]'
    )) == [[4, 6]]
    assert parser.parse(scanner.tokenize(
        '''[[1, 2],
            [3, 4]]
            .+
            [[4, 5],
             [6, 7]]'''
    )) == [[5, 7],
           [9, 11]]
    assert parser.parse(scanner.tokenize(
        '''[[1, 2, 3],
            [4, 5, 6]]
            .+
            [[7, 8, 9],
             [10, 11, 12]]'''
    )) == [[8, 10, 12],
           [14, 16, 18]]
    assert parser.parse(scanner.tokenize(
        'ones(2) .+ ones(2) .+ ones(2)'
    )) == [[3, 3],
           [3, 3]]

def test_dotsub():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        '[[1]] .- [[2]]'
    )) == [[-1]]
    assert parser.parse(scanner.tokenize(
        '[[1, 1]] .- [[3, 4]]'
    )) == [[-2, -3]]
    assert parser.parse(scanner.tokenize(
        '''[[1, 2],
            [3, 4]]
            .-
            [[4, 4],
             [5, 5]]'''
    )) == [[-3, -2],
           [-2, -1]]
    assert parser.parse(scanner.tokenize(
        '''[[1, 2, 3],
            [4, 5, 6]]
            .-
            [[7, 8, 9],
             [7, 8, 9]]'''
    )) == [[-6, -6, -6],
           [-3, -3, -3]]
    assert parser.parse(scanner.tokenize(
        'zeros(2) .- ones(2) .- ones(2)'
    )) == [[-2, -2],
           [-2, -2]]

def test_dotmul():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        '[[-1]] .* [[2]]'
    )) == [[-2]]
    assert parser.parse(scanner.tokenize(
        '[[1, 2]] .* [[3, 4]]'
    )) == [[3, 8]]
    assert parser.parse(scanner.tokenize(
        '''[[1, 2],
            [3, 4]]
            .*
            [[4, 5],
             [6, 7]]'''
    )) == [[4, 10],
           [18, 28]]
    assert parser.parse(scanner.tokenize(
        '''[[1, 2, 3],
            [4, 5, 6]]
            .*
            [[7, 8, 9],
             [10, 11, 12]]'''
    )) == [[7, 16, 27],
           [40, 55, 72]]
    assert parser.parse(scanner.tokenize(
        '''[[1, 2],
            [3, 4]] .* zeros(2)'''
    )) == [[0, 0],
           [0, 0]]

def test_dotdiv():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        '[[-1]] ./ [[2]]'
    )) == [[-1/2]]
    assert parser.parse(scanner.tokenize(
        '[[1, 2]] ./ [[3, 4]]'
    )) == [[1/3, 1/2]]
    assert parser.parse(scanner.tokenize(
        '''[[1, 2],
            [3, 4]]
            ./
            [[4, 5],
             [6, 7]]'''
    )) == [[1/4, 2/5],
           [3/6, 4/7]]
    assert parser.parse(scanner.tokenize(
        '''[[1, 2, 3],
            [4, 5, 6]]
            .*
            [[7, 8, 9],
             [10, 11, 12]]'''
    )) == [[7, 16, 27],
           [40, 55, 72]]
    assert parser.parse(scanner.tokenize(
        '''ones(2)
           ./
           [[1, 2],
            [3, 4]]
           '''
    )) == [[1, 1/2],
           [1/3, 1/4]]
