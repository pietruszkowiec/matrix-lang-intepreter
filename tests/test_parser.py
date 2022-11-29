import pytest
from matrix_lang_interpreter.AST import *
from matrix_lang_interpreter.scanner import Scanner
from matrix_lang_interpreter.parser import Parser
from matrix_lang_interpreter.add_to_class import addToClass


@addToClass(IntNum)
def __eq__(self, other):
    if type(other) == int:
        return self.n == other
    return self.n == other.n

@addToClass(FloatNum)
def __eq__(self, other):
    if type(other) == float:
        return self.n == other
    return self.n == other.n


def test_BinExpr():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        '1 + 2')).stmt_set == [BinExpr('+', 1, 2)]
    assert parser.parse(scanner.tokenize(
        '1 - 2')).stmt_set == [BinExpr('-', 1, 2)]
    assert parser.parse(scanner.tokenize(
        '2 * 3')).stmt_set == [BinExpr('*', 2, 3)]
    assert parser.parse(scanner.tokenize(
        '3 / 2')).stmt_set == [BinExpr('/', 3, 2)]
    assert parser.parse(scanner.tokenize(
        '(3 + 1) * 2')).stmt_set == [BinExpr('*', BinExpr('+', 3, 1), 2)]
    assert parser.parse(scanner.tokenize(
        '2 * (3 + 1)')).stmt_set == [BinExpr('*', 2, BinExpr('+', 3, 1))]

def test_UnExpr():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        '-1')).stmt_set == [UnExpr('-', 1)]
    assert parser.parse(scanner.tokenize(
        '-(3 + 1)')).stmt_set == [UnExpr('-', BinExpr('+', 3, 1))]
    assert parser.parse(scanner.tokenize(
        "a'")).stmt_set == [UnExpr("'", Id('a'))]

def test_precedence():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        '2 * 3 + 1')).stmt_set == [BinExpr('+', BinExpr('*', 2, 3), 1)]
    assert parser.parse(scanner.tokenize(
        '1 + 2 * 3')).stmt_set == [BinExpr('+', 1, BinExpr('*', 2, 3))]
    assert parser.parse(scanner.tokenize(
        '-1 + 2')).stmt_set == [BinExpr('+', UnExpr('-', 1), 2)]
    assert parser.parse(scanner.tokenize(
        '2 + -1')).stmt_set == [BinExpr('+', 2, UnExpr('-', 1))]
    assert parser.parse(scanner.tokenize(
        '-2 - 1')).stmt_set == [BinExpr('-', UnExpr('-', 2), 1)]
    assert parser.parse(scanner.tokenize(
        '-1 * 2')).stmt_set == [BinExpr('*', UnExpr('-', 1), 2)]
    assert parser.parse(scanner.tokenize(
        '2 * -1')).stmt_set == [BinExpr('*', 2, UnExpr('-', 1))]

def test_Matrix():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        '''[[1]]'''
    )).stmt_set == [Matrix([Vector([1])])]
    assert parser.parse(scanner.tokenize(
        '''[[-1]]'''
    )).stmt_set == [Matrix([Vector([UnExpr('-', 1)])])]
    assert parser.parse(scanner.tokenize(
        '''[[1, 2]]'''
    )).stmt_set == [Matrix([Vector([1, 2])])]
    assert parser.parse(scanner.tokenize(
        '''[[1, 2],
            [3, 4]]'''
    )).stmt_set == [Matrix([Vector([1, 2]),
                   Vector([3, 4])])]

def test_SpecialMatrix():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        'zeros(0)'
    )).stmt_set == [SpecialMatrix('zeros', 0)]
    assert parser.parse(scanner.tokenize(
        'ones(2)'
    )).stmt_set == [SpecialMatrix('ones', 2)]
    assert parser.parse(scanner.tokenize(
        'eye(3)'
    )).stmt_set == [SpecialMatrix('eye', 3)]

def test_assignment():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        'a = 5'
    )).stmt_set == [AssignStmt(Id('a'), 5)]
    assert parser.parse(scanner.tokenize(
        '''b = 3;
        a = b;'''
    )).stmt_set == [AssignStmt(Id('b'), 3), AssignStmt(Id('a'), Id('b'))]
    assert parser.parse(scanner.tokenize(
        'a = 3 + 4 * 5'
    )).stmt_set == [AssignStmt(Id('a'), BinExpr('+', 3, BinExpr('*', 4, 5)))]
    assert parser.parse(scanner.tokenize(
        'a = b + c * d'
    )).stmt_set == [AssignStmt(Id('a'), BinExpr('+', Id('b'), BinExpr('*', Id('c'), Id('d'))))]
    assert parser.parse(scanner.tokenize(
        'a += 5'
    )).stmt_set == [AssignStmt(Id('a'), BinExpr('+', Id('a'), 5))]
    assert parser.parse(scanner.tokenize(
        'a -= 5'
    )).stmt_set == [AssignStmt(Id('a'), BinExpr('-', Id('a'), 5))]
    assert parser.parse(scanner.tokenize(
        'a *= 5'
    )).stmt_set == [AssignStmt(Id('a'), BinExpr('*', Id('a'), 5))]
    assert parser.parse(scanner.tokenize(
        'a /= 5'
    )).stmt_set == [AssignStmt(Id('a'), BinExpr('/', Id('a'), 5))]
    assert parser.parse(scanner.tokenize(
        'A = zeros(4)'
    )).stmt_set == [AssignStmt(Id('A'), SpecialMatrix('zeros', 4))]
    assert parser.parse(scanner.tokenize(
        'A = zeros(n)'
    )).stmt_set == [AssignStmt(Id('A'), SpecialMatrix('zeros', Id('n')))]


def test_relationExpr():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        'a < b'
    )).stmt_set == [RelationExpr('<', Id('a'), Id('b'))]
    assert parser.parse(scanner.tokenize(
        'a > b'
    )).stmt_set == [RelationExpr('>', Id('a'), Id('b'))]
    assert parser.parse(scanner.tokenize(
        'a <= b'
    )).stmt_set == [RelationExpr('<=', Id('a'), Id('b'))]
    assert parser.parse(scanner.tokenize(
        'a >= b'
    )).stmt_set == [RelationExpr('>=', Id('a'), Id('b'))]
    assert parser.parse(scanner.tokenize(
        'a == b'
    )).stmt_set == [RelationExpr('==', Id('a'), Id('b'))]
    assert parser.parse(scanner.tokenize(
        'a != b'
    )).stmt_set == [RelationExpr('!=', Id('a'), Id('b'))]
    assert parser.parse(scanner.tokenize(
        'a + c != b'
    )).stmt_set == [RelationExpr('!=', BinExpr('+', Id('a'), Id('c')), Id('b'))]
    assert parser.parse(scanner.tokenize(
        'a == b + c'
    )).stmt_set == [RelationExpr('==', Id('a'), BinExpr('+', Id('b'), Id('c')))]
    assert parser.parse(scanner.tokenize(
        'a + c < b + d'
    )).stmt_set == [RelationExpr('<', BinExpr('+', Id('a'), Id('c')), BinExpr('+', Id('b'), Id('d')))]

def test_block():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        '{a = 1}'
    )).stmt_set == [Block([AssignStmt(Id('a'), 1)])]
    assert parser.parse(scanner.tokenize(
        '''{
            a = 1
        }'''
    )).stmt_set == [Block([AssignStmt(Id('a'), 1)])]
    assert parser.parse(scanner.tokenize(
        '{{a = 1}}'
    )).stmt_set == [Block([Block([AssignStmt(Id('a'), 1)])])]
    assert parser.parse(scanner.tokenize(
        '''{
            {
              a = 1
            }
        }'''
    )).stmt_set == [Block([Block([AssignStmt(Id('a'), 1)])])]
    assert parser.parse(scanner.tokenize(
        '''{
            b = 1
            {
              a = 1
            }
        }'''
    )).stmt_set == [Block([
            AssignStmt(Id('b'), 1),
            Block([
                AssignStmt(Id('a'), 1)
            ])
        ])]
    assert parser.parse(scanner.tokenize(
        '''
        c
        {
            b
            {
                a
            }
        }'''
    )).stmt_set == \
        [
            Id('c'),
            Block([
                Id('b'),
                Block([
                    Id('a')
                ])
            ])
        ]

def test_ifStmt():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        'if(b) {a = 1}'
    )).stmt_set == [
            IfStmt(Id('b'), Block([
                AssignStmt(Id('a'), 1)
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        'if(b) a = 1'
    )).stmt_set == [
            IfStmt(Id('b'), Block([
                AssignStmt(Id('a'), 1)
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        '''if(b) {
            a = 1
            c = a + b
        }'''
    )).stmt_set == [
            IfStmt(Id('b'), Block([
                AssignStmt(Id('a'), 1),
                AssignStmt(Id('c'), BinExpr('+', Id('a'), Id('b')))
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        '''if(b) {
            a = 1
            if(a > b) {
                b = 3
            }
        }'''
    )).stmt_set == [
            IfStmt(Id('b'), Block([
                AssignStmt(Id('a'), 1),
                IfStmt(RelationExpr('>', Id('a'), Id('b')), Block([
                    AssignStmt(Id('b'), 3)
                ]))
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        '''if(b) {
            a = 1
            if(a > b)
                b = 3;
        }'''
    )).stmt_set == [
            IfStmt(Id('b'), Block([
                AssignStmt(Id('a'), 1),
                IfStmt(RelationExpr('>', Id('a'), Id('b')), Block([
                    AssignStmt(Id('b'), 3)
                ]))
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        '''if(b)
            if(a > b)
                b = 3;'''
    )).stmt_set == [
            IfStmt(Id('b'), Block([
                IfStmt(RelationExpr('>', Id('a'), Id('b')), Block([
                    AssignStmt(Id('b'), 3)
                ]))
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        '''if(b)
            a = 1;
        '''
    )).stmt_set == [
            IfStmt(Id('b'), Block([
                AssignStmt(Id('a'), 1)
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        '''if(b)
            a = 1;
        if(a > b)
            b = 3;
        '''
    )).stmt_set == [
            IfStmt(Id('b'), Block([
                AssignStmt(Id('a'), 1)
            ])),
            IfStmt(RelationExpr('>', Id('a'), Id('b')), Block([
                AssignStmt(Id('b'), 3)
            ]))
        ]

def test_ifElseStmt():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        'if(b) {a = 1} else {a = 2}'
    )).stmt_set == [
            IfElseStmt(Id('b'), Block([
                AssignStmt(Id('a'), 1)
            ]), Block([
                AssignStmt(Id('a'), 2)
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        'if(b) { a = 1 } else a = 2'
    )).stmt_set == [
            IfElseStmt(Id('b'), Block([
                AssignStmt(Id('a'), 1)
            ]), Block([
                AssignStmt(Id('a'), 2)
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        'if(b) a = 1 else { a = 2 }'
    )).stmt_set == [
            IfElseStmt(Id('b'), Block([
                AssignStmt(Id('a'), 1)
            ]), Block([
                AssignStmt(Id('a'), 2)
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        'if(b) a = 1 else a = 2 '
    )).stmt_set == [
            IfElseStmt(Id('b'), Block([
                AssignStmt(Id('a'), 1)
            ]), Block([
                AssignStmt(Id('a'), 2)
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        'if(b) a else { if (c) d }'
    )).stmt_set == [
            IfElseStmt(Id('b'), Block([
                Id('a')
            ]), Block([
                IfStmt(Id('c'), Block([
                    Id('d')
                ]))
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        'if(b) a else if (c) d'
    )).stmt_set == [
            IfElseStmt(Id('b'), Block([
                Id('a')
            ]), Block([
                IfStmt(Id('c'), Block([
                    Id('d')
                ]))
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        'if(b) a else if (c) d else e'
    )).stmt_set == [
            IfElseStmt(Id('b'), Block([
                Id('a')
            ]), Block([
                IfElseStmt(Id('c'), Block([
                    Id('d')
                ]), Block([
                    Id('e')
                ]))
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        'if(b) a if (c) d else e'
    )).stmt_set == [
            IfStmt(Id('b'), Block([Id('a')])),
            IfElseStmt(Id('c'), Block([Id('d')]), Block([Id('e')]))
        ]
    assert parser.parse(scanner.tokenize(
        '''if(b) {
            a = 1
            if(a > b) {
                b = 3
            } else
                b = 4
        }'''
    )).stmt_set == [
            IfStmt(Id('b'), Block([
                AssignStmt(Id('a'), 1),
                IfElseStmt(RelationExpr('>', Id('a'), Id('b')), Block([
                    AssignStmt(Id('b'), 3)
                ]), Block([
                    AssignStmt(Id('b'), 4)
                ]))
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        '''if(b) {
            a = 1
            if(a > b) {
                b = 3
            } else {
                b = 4
            }
        }'''
    )).stmt_set == [
            IfStmt(Id('b'), Block([
                AssignStmt(Id('a'), 1),
                IfElseStmt(RelationExpr('>', Id('a'), Id('b')), Block([
                    AssignStmt(Id('b'), 3)
                ]), Block([
                    AssignStmt(Id('b'), 4)
                ]))
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        '''if(b) {
            a = 1
            if(a > b) {
                b = 3
            } else {
                b = 4
            }
        } else {
            c = 4
        }'''
    )).stmt_set == [
            IfElseStmt(Id('b'), Block([
                AssignStmt(Id('a'), 1),
                IfElseStmt(RelationExpr('>', Id('a'), Id('b')), Block([
                    AssignStmt(Id('b'), 3)
                ]), Block([
                    AssignStmt(Id('b'), 4)
                ]))
            ]), Block([
                AssignStmt(Id('c'), 4)
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        '''if(b)
            if(a)
                c
            else
                d
        '''
    )).stmt_set == [
            IfStmt(Id('b'), Block([
                IfElseStmt(Id('a'), Block([Id('c')]), Block([Id('d')]))
            ]))
        ]

def test_whileLoop():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        'while(b) {a = 1}'
    )).stmt_set == [
            WhileLoop(Id('b'), Block([
                AssignStmt(Id('a'), 1)
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        'while(b) a = 1'
    )).stmt_set == [
            WhileLoop(Id('b'), Block([
                AssignStmt(Id('a'), 1)
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        '''while(b) {
            a = 1
            c = a + b
        }'''
    )).stmt_set == [
            WhileLoop(Id('b'), Block([
                AssignStmt(Id('a'), 1),
                AssignStmt(Id('c'), BinExpr('+', Id('a'), Id('b')))
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        '''while(b) {
            a = 1
            while(a > b) {
                b = 3
            }
        }'''
    )).stmt_set == [
            WhileLoop(Id('b'), Block([
                AssignStmt(Id('a'), 1),
                WhileLoop(RelationExpr('>', Id('a'), Id('b')), Block([
                    AssignStmt(Id('b'), 3)
                ]))
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        '''while(b) {
            a = 1
            while(a > b)
                b = 3;
        }'''
    )).stmt_set == [
            WhileLoop(Id('b'), Block([
                AssignStmt(Id('a'), 1),
                WhileLoop(RelationExpr('>', Id('a'), Id('b')), Block([
                    AssignStmt(Id('b'), 3)
                ]))
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        '''while(b)
            while(a > b)
                b = 3;'''
    )).stmt_set == [
            WhileLoop(Id('b'), Block([
                WhileLoop(RelationExpr('>', Id('a'), Id('b')), Block([
                    AssignStmt(Id('b'), 3)
                ]))
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        '''while(b)
            a = 1;
        '''
    )).stmt_set == [
            WhileLoop(Id('b'), Block([
                AssignStmt(Id('a'), 1)
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        '''while(b)
            a = 1;
        while(a > b)
            b = 3;
        '''
    )).stmt_set == [
            WhileLoop(Id('b'), Block([
                AssignStmt(Id('a'), 1)
            ])),
            WhileLoop(RelationExpr('>', Id('a'), Id('b')), Block([
                AssignStmt(Id('b'), 3)
            ]))
        ]

def test_forLoop():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        'for i = 1:2 { i }'
    )).stmt_set == [
            ForLoop(Id('i'), 1, 2, Block([
                Id('i')
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        '''
        for i = 1:2 {
            i
        }'''
    )).stmt_set == [
            ForLoop(Id('i'), 1, 2, Block([
                Id('i')
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        '''
        for i = 1:2
            i'''
    )).stmt_set == [
            ForLoop(Id('i'), 1, 2, Block([
                Id('i')
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        '''
        for i = 1:2 {
            for j = i:(i * i) {
                j
            }
        }'''
    )).stmt_set == [
            ForLoop(Id('i'), 1, 2, Block([
                ForLoop(Id('j'), Id('i'), BinExpr('*', Id('i'), Id('i')), Block([
                    Id('j')
                ]))
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        '''
        for i = 1:2 {
            for j = i:(i * i)
                j
        }'''
    )).stmt_set == [
            ForLoop(Id('i'), 1, 2, Block([
                ForLoop(Id('j'), Id('i'), BinExpr('*', Id('i'), Id('i')), Block([
                    Id('j')
                ]))
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        '''
        for i = 1:2
            for j = i:(i * i) {
                j
            }
        '''
    )).stmt_set == [
            ForLoop(Id('i'), 1, 2, Block([
                ForLoop(Id('j'), Id('i'), BinExpr('*', Id('i'), Id('i')), Block([
                    Id('j')
                ]))
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        '''
        for i = 1:2
            for j = i:(i * i)
                j'''
    )).stmt_set == [
            ForLoop(Id('i'), 1, 2, Block([
                ForLoop(Id('j'), Id('i'), BinExpr('*', Id('i'), Id('i')), Block([
                    Id('j')
                ]))
            ]))
        ]

def test_Ref():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        'a[1, 2]'
    )).stmt_set == [Ref(Id('a'), 1, 2)]
    assert parser.parse(scanner.tokenize(
        'a[i, j]'
    )).stmt_set == [Ref(Id('a'), Id('i'), Id('j'))]

def test_loopKeyword():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        '''
        while(b) {
            a = 1
            break
        }
    '''
    )).stmt_set == [
            WhileLoop(Id('b'), Block([
                AssignStmt(Id('a'), 1),
                LoopKeyword('break')
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        '''
        while(b) {
            continue
            a = 1
        }
    '''
    )).stmt_set == [
            WhileLoop(Id('b'), Block([
                LoopKeyword('continue'),
                AssignStmt(Id('a'), 1)
            ]))
        ]

def test_print():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        'print 2'
    )).stmt_set == [Print([2])]
    assert parser.parse(scanner.tokenize(
        'print a'
    )).stmt_set == [Print([Id('a')])]
    assert parser.parse(scanner.tokenize(
        'print a + 2'
    )).stmt_set == [Print([BinExpr('+', Id('a'), 2)])]
    assert parser.parse(scanner.tokenize(
        'print a, 2'
    )).stmt_set == [Print([Id('a'), 2])]
    assert parser.parse(scanner.tokenize(
        'print a, 2, b'
    )).stmt_set == [Print([Id('a'), 2, Id('b')])]

def test_return():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        'return 2'
    )).stmt_set == [Return([2])]
    assert parser.parse(scanner.tokenize(
        'return a'
    )).stmt_set == [Return([Id('a')])]
    assert parser.parse(scanner.tokenize(
        'return a + 2'
    )).stmt_set == [Return([BinExpr('+', Id('a'), 2)])]
    assert parser.parse(scanner.tokenize(
        'return a, b'
    )).stmt_set == [Return([Id('a'), Id('b')])]
