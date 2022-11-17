import pytest
from matrix_lang_interpreter import *
from matrix_lang_interpreter.scanner import Scanner
from matrix_lang_interpreter.parser import *


def test_literals():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        '1 + 2')) == [BinExpr('+', 1, 2)]
    assert parser.parse(scanner.tokenize(
        '1 - 2')) == [BinExpr('-', 1, 2)]
    assert parser.parse(scanner.tokenize(
        '2 * 3')) == [BinExpr('*', 2, 3)]
    assert parser.parse(scanner.tokenize(
        '3 / 2')) == [BinExpr('/', 3, 2)]
    assert parser.parse(scanner.tokenize(
        '(3 + 1) * 2')) == [BinExpr('*', BinExpr('+', 3, 1), 2)]
    assert parser.parse(scanner.tokenize(
        '2 * (3 + 1)')) == [BinExpr('*', 2, BinExpr('+', 3, 1))]
    assert parser.parse(scanner.tokenize(
        '-1')) == [UnExpr('-', 1)]
    assert parser.parse(scanner.tokenize(
        '-(3 + 1)')) == [UnExpr('-', BinExpr('+', 3, 1))]

def test_precedence():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        '2 * 3 + 1')) == [BinExpr('+', BinExpr('*', 2, 3), 1)]
    assert parser.parse(scanner.tokenize(
        '1 + 2 * 3')) == [BinExpr('+', 1, BinExpr('*', 2, 3))]
    assert parser.parse(scanner.tokenize(
        '-1 + 2')) == [BinExpr('+', UnExpr('-', 1), 2)]
    assert parser.parse(scanner.tokenize(
        '2 + -1')) == [BinExpr('+', 2, UnExpr('-', 1))]
    assert parser.parse(scanner.tokenize(
        '-2 - 1')) == [BinExpr('-', UnExpr('-', 2), 1)]
    assert parser.parse(scanner.tokenize(
        '-1 * 2')) == [BinExpr('*', UnExpr('-', 1), 2)]
    assert parser.parse(scanner.tokenize(
        '2 * -1')) == [BinExpr('*', 2, UnExpr('-', 1))]

def test_outerlist():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        '''[[1]]'''
    )) == [Matrix(array=[[1]])]
    assert parser.parse(scanner.tokenize(
        '''[[-1]]'''
    )) == [Matrix(array=[[UnExpr('-', 1)]])]
    assert parser.parse(scanner.tokenize(
        '''[[1, 2]]'''
    )) == [Matrix(array=[[1, 2]])]
    assert parser.parse(scanner.tokenize(
        '''[[1, 2],
            [3, 4]]'''
    )) == [Matrix(array=[[1, 2],
                        [3, 4]])]

def test_zeros():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        'zeros(0)'
    )) == [Zeros(0)]
    assert parser.parse(scanner.tokenize(
        'zeros(2)'
    )) == [Zeros(2)]

def test_ones():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        'ones(1)'
    )) == [Ones(1)]
    assert parser.parse(scanner.tokenize(
        'ones(2)'
    )) == [Ones(2)]

def test_eye():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        'eye(1)'
    )) == [Eye(1)]
    assert parser.parse(scanner.tokenize(
        'eye(2)'
    )) == [Eye(2)]

def test_dotadd():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        '[[1]] .+ [[2]]'
    )) == [BinExpr('.+', Matrix(array=[[1]]), Matrix(array=[[2]]))]
    assert parser.parse(scanner.tokenize(
        '[[1, 2]] .+ [[3, 4]]'
    )) == [BinExpr('.+', Matrix(array=[[1, 2]]), Matrix(array=[[3, 4]]))]
    assert parser.parse(scanner.tokenize(
        '''[[1, 2],
            [3, 4]]
            .+
            [[4, 5],
             [6, 7]]'''
    )) == [BinExpr('.+', Matrix(array=[[1, 2], [3, 4]]),
                         Matrix(array=[[4, 5], [6, 7]]))]
    assert parser.parse(scanner.tokenize(
        '''[[1, 2, 3],
            [4, 5, 6]]
            .+
            [[7, 8, 9],
             [10, 11, 12]]'''
    )) == [BinExpr('.+', Matrix(array=[[1, 2, 3], [4, 5, 6]]),
                         Matrix(array=[[7, 8, 9], [10, 11, 12]]))]
    assert parser.parse(scanner.tokenize(
        'ones(2) .+ ones(2) .+ ones(2)'
    )) == [BinExpr('.+', BinExpr('.+', Ones(2), Ones(2)), Ones(2))]

def test_dotsub():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        '[[1]] .- [[2]]'
    )) == [BinExpr('.-', Matrix(array=[[1]]), Matrix(array=[[2]]))]
    assert parser.parse(scanner.tokenize(
        '[[1, 1]] .- [[3, 4]]'
    )) == [BinExpr('.-', Matrix(array=[[1, 1]]), Matrix(array=[[3, 4]]))]
    assert parser.parse(scanner.tokenize(
        '''[[1, 2],
            [3, 4]]
            .-
            [[4, 4],
             [5, 5]]'''
    )) == [BinExpr('.-', Matrix(array=[[1, 2], [3, 4]]), Matrix(array=[[4, 4], [5, 5]]))]
    assert parser.parse(scanner.tokenize(
        '''[[1, 2, 3],
            [4, 5, 6]]
            .-
            [[7, 8, 9],
             [7, 8, 9]]'''
    )) == [BinExpr('.-', Matrix(array=[[1, 2, 3], [4, 5, 6]]),
                        Matrix(array=[[7, 8, 9], [7, 8, 9]]))]
    assert parser.parse(scanner.tokenize(
        'zeros(2) .- ones(2) .- ones(2)'
    )) == [BinExpr('.-', BinExpr('.-', Zeros(2), Ones(2)), Ones(2))]

def test_dotmul():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        '[[1]] .* [[2]]'
    )) == [BinExpr('.*', Matrix(array=[[1]]), Matrix(array=[[2]]))]
    assert parser.parse(scanner.tokenize(
        '[[1, 2]] .* [[3, 4]]'
    )) == [BinExpr('.*', Matrix(array=[[1, 2]]), Matrix(array=[[3, 4]]))]
    assert parser.parse(scanner.tokenize(
        '''[[1, 2],
            [3, 4]]
            .*
            [[4, 5],
             [6, 7]]'''
    )) == [BinExpr('.*', Matrix(array=[[1, 2], [3, 4]]),
                         Matrix(array=[[4, 5], [6, 7]]))]
    assert parser.parse(scanner.tokenize(
        '''[[1, 2, 3],
            [4, 5, 6]]
            .*
            [[7, 8, 9],
             [10, 11, 12]]'''
    )) == [BinExpr('.*', Matrix(array=[[1, 2, 3], [4, 5, 6]]),
                         Matrix(array=[[7, 8, 9], [10, 11, 12]]))]
    assert parser.parse(scanner.tokenize(
        '''[[1, 2],
            [3, 4]] .* zeros(2)'''
    )) == [BinExpr('.*', Matrix(array=[[1, 2], [3, 4]]), Zeros(2))]

def test_dotdiv():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        '[[1]] ./ [[2]]'
    )) == [BinExpr('./', Matrix(array=[[1]]), Matrix(array=[[2]]))]
    assert parser.parse(scanner.tokenize(
        '[[1, 2]] ./ [[3, 4]]'
    )) == [BinExpr('./', Matrix(array=[[1, 2]]), Matrix(array=[[3, 4]]))]
    assert parser.parse(scanner.tokenize(
        '''[[1, 2],
            [3, 4]]
            ./
            [[4, 5],
             [6, 7]]'''
    )) == [BinExpr('./', Matrix(array=[[1, 2], [3, 4]]),
                         Matrix(array=[[4, 5], [6, 7]]))]
    assert parser.parse(scanner.tokenize(
        '''[[1, 2, 3],
            [4, 5, 6]]
            ./
            [[7, 8, 9],
             [10, 11, 12]]'''
    )) == [BinExpr('./', Matrix(array=[[1, 2, 3], [4, 5, 6]]),
                         Matrix(array=[[7, 8, 9], [10, 11, 12]]))]
    assert parser.parse(scanner.tokenize(
        '''ones(2)
           ./
           [[1, 2],
            [3, 4]]
           '''
    )) == [BinExpr('./', Ones(2), Matrix(array=[[1, 2], [3, 4]]))]

def test_assignment():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        'a = 5'
    )) == [AssignExpr(Id('a'), 5)]
    assert parser.parse(scanner.tokenize(
        '''b = 3
        a = b'''
    )) == [AssignExpr(Id('b'), 3), AssignExpr(Id('a'), Id('b'))]
    assert parser.parse(scanner.tokenize(
        'a = 3 + 4 * 5'
    )) == [AssignExpr(Id('a'), BinExpr('+', 3, BinExpr('*', 4, 5)))]
    assert parser.parse(scanner.tokenize(
        'a = b + c * d'
    )) == [AssignExpr(Id('a'), BinExpr('+', Id('b'), BinExpr('*', Id('c'), Id('d'))))]
    assert parser.parse(scanner.tokenize(
        'a += 5'
    )) == [AssignExpr(Id('a'), BinExpr('+', Id('a'), 5))]
    assert parser.parse(scanner.tokenize(
        'a -= 5'
    )) == [AssignExpr(Id('a'), BinExpr('-', Id('a'), 5))]
    assert parser.parse(scanner.tokenize(
        'a *= 5'
    )) == [AssignExpr(Id('a'), BinExpr('*', Id('a'), 5))]
    assert parser.parse(scanner.tokenize(
        'a /= 5'
    )) == [AssignExpr(Id('a'), BinExpr('/', Id('a'), 5))]
    assert parser.parse(scanner.tokenize(
        'A = zeros(4)'
    )) == [AssignExpr(Id('A'), Zeros(4))]
    assert parser.parse(scanner.tokenize(
        'A = zeros(n)'
    )) == [AssignExpr(Id('A'), Zeros(Id('n')))]
