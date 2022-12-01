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
        'x = 1 + 2;')).stmt_set[0].expr == BinExpr('+', 1, 2)
    assert parser.parse(scanner.tokenize(
        'x = 1 - 2;')).stmt_set[0].expr == BinExpr('-', 1, 2)
    assert parser.parse(scanner.tokenize(
        'x = 2 * 3;')).stmt_set[0].expr == BinExpr('*', 2, 3)
    assert parser.parse(scanner.tokenize(
        'x = 3 / 2;')).stmt_set[0].expr == BinExpr('/', 3, 2)
    assert parser.parse(scanner.tokenize(
        'x = (3 + 1) * 2;')).stmt_set[0].expr == BinExpr('*', BinExpr('+', 3, 1), 2)
    assert parser.parse(scanner.tokenize(
        'x = 2 * (3 + 1);')).stmt_set[0].expr == BinExpr('*', 2, BinExpr('+', 3, 1))

def test_UnExpr():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        'x = -1;')).stmt_set[0].expr == UnExpr('-', 1)
    assert parser.parse(scanner.tokenize(
        'x = +(3 + -1);')).stmt_set[0].expr == UnExpr('+', BinExpr('+', 3, UnExpr('-', 1)))
    assert parser.parse(scanner.tokenize(
        "x = a';")).stmt_set[0].expr == UnExpr("'", Id('a'))

def test_Precedence():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        'x = 2 * 3 + 1;')).stmt_set[0].expr == BinExpr('+', BinExpr('*', 2, 3), 1)
    assert parser.parse(scanner.tokenize(
        'x = 1 + 2 * 3;')).stmt_set[0].expr == BinExpr('+', 1, BinExpr('*', 2, 3))
    assert parser.parse(scanner.tokenize(
        'x = -1 + 2;')).stmt_set[0].expr == BinExpr('+', UnExpr('-', 1), 2)
    assert parser.parse(scanner.tokenize(
        'x = 2 + -1;')).stmt_set[0].expr == BinExpr('+', 2, UnExpr('-', 1))
    assert parser.parse(scanner.tokenize(
        'x = -2 - 1;')).stmt_set[0].expr == BinExpr('-', UnExpr('-', 2), 1)
    assert parser.parse(scanner.tokenize(
        'x = -1 * 2;')).stmt_set[0].expr == BinExpr('*', UnExpr('-', 1), 2)
    assert parser.parse(scanner.tokenize(
        'x = 2 * -1;')).stmt_set[0].expr == BinExpr('*', 2, UnExpr('-', 1))

def test_Vector():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        'x = [];'
    )).stmt_set[0].expr == Vector([])
    assert parser.parse(scanner.tokenize(
        'x = [[]];'
    )).stmt_set[0].expr == Vector([Vector([])])
    assert parser.parse(scanner.tokenize(
        'x = [[[]]];'
    )).stmt_set[0].expr == Vector([Vector([Vector([])])])
    assert parser.parse(scanner.tokenize(
        'x = [1];'
    )).stmt_set[0].expr == Vector([1])
    assert parser.parse(scanner.tokenize(
        'x = [1, 2];'
    )).stmt_set[0].expr == Vector([1, 2])
    assert parser.parse(scanner.tokenize(
        'x = [[1, 2]];'
    )).stmt_set[0].expr == Vector([Vector([1, 2])])
    assert parser.parse(scanner.tokenize(
        'x = [[[1], 2]];'
    )).stmt_set[0].expr == Vector([Vector([Vector([1]), 2])])
    assert parser.parse(scanner.tokenize(
        'x = [[[1], [2]]];'
    )).stmt_set[0].expr == Vector([Vector([Vector([1]), Vector([2])])])
    assert parser.parse(scanner.tokenize(
        'x = [[1, 2], [3, 4]];'
    )).stmt_set[0].expr == Vector([Vector([1, 2]), Vector([3, 4])])

def test_SpecialMatrix():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        'x = zeros(2);'
    )).stmt_set[0].expr == Zeros(Vector([2]))
    assert parser.parse(scanner.tokenize(
        'x = zeros(2, 3);'
    )).stmt_set[0].expr == Zeros(Vector([2, 3]))
    assert parser.parse(scanner.tokenize(
        'x = ones(2);'
    )).stmt_set[0].expr == Ones(Vector([2]))
    assert parser.parse(scanner.tokenize(
        'x = ones(2, 3);'
    )).stmt_set[0].expr == Ones(Vector([2, 3]))
    assert parser.parse(scanner.tokenize(
        'x = eye(3);'
    )).stmt_set[0].expr == Eye(3)

def test_AssignStmt():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        'a = 5;'
    )).stmt_set == [AssignStmt(Id('a'), 5)]
    assert parser.parse(scanner.tokenize(
        '''b = 3;
        a = b;'''
    )).stmt_set == [AssignStmt(Id('b'), 3), AssignStmt(Id('a'), Id('b'))]
    assert parser.parse(scanner.tokenize(
        'a = 3 + 4 * 5;'
    )).stmt_set == [AssignStmt(Id('a'), BinExpr('+', 3, BinExpr('*', 4, 5)))]
    assert parser.parse(scanner.tokenize(
        'a = b + c * d;'
    )).stmt_set == [AssignStmt(Id('a'), BinExpr('+', Id('b'), BinExpr('*', Id('c'), Id('d'))))]
    assert parser.parse(scanner.tokenize(
        'a += 5;'
    )).stmt_set == [AssignStmt(Id('a'), BinExpr('+', Id('a'), 5))]
    assert parser.parse(scanner.tokenize(
        'a -= 5;'
    )).stmt_set == [AssignStmt(Id('a'), BinExpr('-', Id('a'), 5))]
    assert parser.parse(scanner.tokenize(
        'a *= 5;'
    )).stmt_set == [AssignStmt(Id('a'), BinExpr('*', Id('a'), 5))]
    assert parser.parse(scanner.tokenize(
        'a /= 5;'
    )).stmt_set == [AssignStmt(Id('a'), BinExpr('/', Id('a'), 5))]
    assert parser.parse(scanner.tokenize(
        'A = zeros(4);'
    )).stmt_set == [AssignStmt(Id('A'), Zeros(Vector([4])))]
    assert parser.parse(scanner.tokenize(
        'A = eye(n);'
    )).stmt_set == [AssignStmt(Id('A'), Eye(Id('n')))]


def test_RelationExpr():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        'x = a < b;'
    )).stmt_set[0].expr == RelationExpr('<', Id('a'), Id('b'))
    assert parser.parse(scanner.tokenize(
        'x = a > b;'
    )).stmt_set[0].expr == RelationExpr('>', Id('a'), Id('b'))
    assert parser.parse(scanner.tokenize(
        'x = a <= b;'
    )).stmt_set[0].expr == RelationExpr('<=', Id('a'), Id('b'))
    assert parser.parse(scanner.tokenize(
        'x = a >= b;'
    )).stmt_set[0].expr == RelationExpr('>=', Id('a'), Id('b'))
    assert parser.parse(scanner.tokenize(
        'x = a == b;'
    )).stmt_set[0].expr == RelationExpr('==', Id('a'), Id('b'))
    assert parser.parse(scanner.tokenize(
        'x = a != b;'
    )).stmt_set[0].expr == RelationExpr('!=', Id('a'), Id('b'))
    assert parser.parse(scanner.tokenize(
        'x = a + c != b;'
    )).stmt_set[0].expr == RelationExpr('!=', BinExpr('+', Id('a'), Id('c')), Id('b'))
    assert parser.parse(scanner.tokenize(
        'x = a == b + c;'
    )).stmt_set[0].expr == RelationExpr('==', Id('a'), BinExpr('+', Id('b'), Id('c')))
    assert parser.parse(scanner.tokenize(
        'x = a + c < b + d;'
    )).stmt_set[0].expr == RelationExpr('<', BinExpr('+', Id('a'), Id('c')), BinExpr('+', Id('b'), Id('d')))

def test_Block():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        '{a = 1;}'
    )).stmt_set == [Block([AssignStmt(Id('a'), 1)])]
    assert parser.parse(scanner.tokenize(
        '''{
            a = 1;
        }'''
    )).stmt_set == [Block([AssignStmt(Id('a'), 1)])]
    assert parser.parse(scanner.tokenize(
        '{{a = 1;}}'
    )).stmt_set == [Block([Block([AssignStmt(Id('a'), 1)])])]
    assert parser.parse(scanner.tokenize(
        '''{
            {
              a = 1;
            }
        }'''
    )).stmt_set == [Block([Block([AssignStmt(Id('a'), 1)])])]
    assert parser.parse(scanner.tokenize(
        '''{
            b = 1;
            {
              a = 1;
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
        b = 1;
        {
            a = 1;
            {
                c = 1;
            }
        }'''
    )).stmt_set == [
            AssignStmt(Id('b'), 1),
            Block([
                AssignStmt(Id('a'), 1),
                Block([
                     AssignStmt(Id('c'), 1)
                ])
            ])
        ]

def test_IfStmt():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        'if(b) {a = 1;}'
    )).stmt_set == [
            IfStmt(Id('b'), Block([AssignStmt(Id('a'), 1)]))
        ]
    assert parser.parse(scanner.tokenize(
        'if(b) a = 1;'
    )).stmt_set == [
            IfStmt(Id('b'), AssignStmt(Id('a'), 1))
        ]
    assert parser.parse(scanner.tokenize(
        '''if(b) {
            a = 1;
            c = a + b;
        }'''
    )).stmt_set == [
            IfStmt(Id('b'), Block([
                AssignStmt(Id('a'), 1),
                AssignStmt(Id('c'), BinExpr('+', Id('a'), Id('b')))
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        '''if(b) {
            a = 1;
            if(a > b) {
                b = 3;
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
            a = 1;
            if(a > b)
                b = 3;
        }'''
    )).stmt_set == [
            IfStmt(Id('b'), Block([
                AssignStmt(Id('a'), 1),
                IfStmt(RelationExpr('>', Id('a'), Id('b')),
                    AssignStmt(Id('b'), 3))
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        '''if(b)
            if(a > b)
                b = 3;'''
    )).stmt_set == [
            IfStmt(Id('b'),
                IfStmt(RelationExpr('>', Id('a'), Id('b')),
                    AssignStmt(Id('b'), 3)))
        ]
    assert parser.parse(scanner.tokenize(
        '''if(b)
            a = 1;
        '''
    )).stmt_set == [
            IfStmt(Id('b'),
                AssignStmt(Id('a'), 1))
        ]
    assert parser.parse(scanner.tokenize(
        '''if(b)
            a = 1;
        if(a > b)
            b = 3;
        '''
    )).stmt_set == [
            IfStmt(Id('b'),
                AssignStmt(Id('a'), 1)),
            IfStmt(RelationExpr('>', Id('a'), Id('b')),
                AssignStmt(Id('b'), 3))
        ]

def test_IfElseStmt():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        'if(b) {a = 1;} else {a = 2;}'
    )).stmt_set == [
            IfElseStmt(Id('b'), Block([
                AssignStmt(Id('a'), 1)
            ]), Block([
                AssignStmt(Id('a'), 2)
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        'if(b) { a = 1; } else a = 2;'
    )).stmt_set == [
            IfElseStmt(Id('b'), Block([
                AssignStmt(Id('a'), 1)
            ]),
                AssignStmt(Id('a'), 2)
            )
        ]
    assert parser.parse(scanner.tokenize(
        'if(b) a = 1; else { a = 2; }'
    )).stmt_set == [
            IfElseStmt(Id('b'),
                AssignStmt(Id('a'), 1),
                Block([
                    AssignStmt(Id('a'), 2)
                ])
            )
        ]
    assert parser.parse(scanner.tokenize(
        'if(b) a = 1; else a = 2; '
    )).stmt_set == [
            IfElseStmt(Id('b'),
                AssignStmt(Id('a'), 1),
                AssignStmt(Id('a'), 2)
            )
        ]
    assert parser.parse(scanner.tokenize(
        'if(b) x = a; else { if (c) x = d; }'
    )).stmt_set == [
            IfElseStmt(Id('b'),
                AssignStmt(Id('x'), Id('a')),
                Block([
                IfStmt(Id('c'),
                    AssignStmt(Id('x'), Id('d')),
                )
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        'if(b) x = a; else if (c) x = d;'
    )).stmt_set == [
            IfElseStmt(Id('b'),
                AssignStmt(Id('x'), Id('a')),
                IfStmt(Id('c'),
                    AssignStmt(Id('x'), Id('d')),
                )
            )
        ]
    assert parser.parse(scanner.tokenize(
        'if(b) x = a; else if (c) x = d; else x = e;'
    )).stmt_set == [
            IfElseStmt(Id('b'),
                AssignStmt(Id('x'), Id('a')),
                IfElseStmt(Id('c'),
                    AssignStmt(Id('x'), Id('d')),
                    AssignStmt(Id('x'), Id('e')),
                )
            )
        ]
    assert parser.parse(scanner.tokenize(
        'if(b) x = a; if (c) x = d; else x = e;'
    )).stmt_set == [
            IfStmt(Id('b'), AssignStmt(Id('x'), Id('a'))),
            IfElseStmt(Id('c'), AssignStmt(Id('x'), Id('d')), AssignStmt(Id('x'), Id('e')),)
        ]
    assert parser.parse(scanner.tokenize(
        '''if(b) {
            a = 1;
            if(a > b) {
                b = 3;
            } else
                b = 4;
        }'''
    )).stmt_set == [
            IfStmt(Id('b'), Block([
                AssignStmt(Id('a'), 1),
                IfElseStmt(RelationExpr('>', Id('a'), Id('b')), Block([
                    AssignStmt(Id('b'), 3)
                ]), AssignStmt(Id('b'), 4))
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        '''if(b) {
            a = 1;
            if(a > b) {
                b = 3;
            } else {
                b = 4;
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
            a = 1;
            if(a > b) {
                b = 3;
            } else {
                b = 4;
            }
        } else {
            c = 4;
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
                x = c;
            else
                x = d;
        '''
    )).stmt_set == [
            IfStmt(Id('b'),
                IfElseStmt(Id('a'),
                    AssignStmt(Id('x'), Id('c')),
                    AssignStmt(Id('x'), Id('d'))
                )
            )
        ]

def test_WhileLoop():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        'while(b) {a = 1;}'
    )).stmt_set == [
            WhileLoop(Id('b'), Block([
                AssignStmt(Id('a'), 1)
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        'while(b) a = 1;'
    )).stmt_set == [
            WhileLoop(Id('b'),
                AssignStmt(Id('a'), 1)
            )
        ]
    assert parser.parse(scanner.tokenize(
        '''while(b) {
            a = 1;
            c = a + b;
        }'''
    )).stmt_set == [
            WhileLoop(Id('b'), Block([
                AssignStmt(Id('a'), 1),
                AssignStmt(Id('c'), BinExpr('+', Id('a'), Id('b')))
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        '''while(b) {
            a = 1;
            while(a > b) {
                b = 3;
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
            a = 1;
            while(a > b)
                b = 3;
        }'''
    )).stmt_set == [
            WhileLoop(Id('b'), Block([
                AssignStmt(Id('a'), 1),
                WhileLoop(RelationExpr('>', Id('a'), Id('b')),
                    AssignStmt(Id('b'), 3)
                )
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        '''while(b)
            while(a > b)
                b = 3;'''
    )).stmt_set == [
            WhileLoop(Id('b'),
                WhileLoop(RelationExpr('>', Id('a'), Id('b')),
                    AssignStmt(Id('b'), 3)
                )
            )
        ]
    assert parser.parse(scanner.tokenize(
        '''while(b)
            a = 1;
        '''
    )).stmt_set == [
            WhileLoop(Id('b'),
                AssignStmt(Id('a'), 1)
            )
        ]
    assert parser.parse(scanner.tokenize(
        '''while(b)
            a = 1;
        while(a > b)
            b = 3;
        '''
    )).stmt_set == [
            WhileLoop(Id('b'),
                AssignStmt(Id('a'), 1)
            ),
            WhileLoop(RelationExpr('>', Id('a'), Id('b')),
                AssignStmt(Id('b'), 3)
            )
        ]

def test_ForLoop():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        'for i = 1:2 { x = i; }'
    )).stmt_set == [
            ForLoop(Id('i'), 1, 2, Block([
                AssignStmt(Id('x'), Id('i'))
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        '''
        for i = 1:2 {
            x = i;
        }'''
    )).stmt_set == [
            ForLoop(Id('i'), 1, 2, Block([
                AssignStmt(Id('x'), Id('i'))
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        '''
        for i = 1:2
            x = i;'''
    )).stmt_set == [
            ForLoop(Id('i'), 1, 2,
                AssignStmt(Id('x'), Id('i'))
            )
        ]
    assert parser.parse(scanner.tokenize(
        '''
        for i = 1:2 {
            for j = i:(i * i) {
                x = j;
            }
        }'''
    )).stmt_set == [
            ForLoop(Id('i'), 1, 2, Block([
                ForLoop(Id('j'), Id('i'), BinExpr('*', Id('i'), Id('i')), Block([
                    AssignStmt(Id('x'), Id('j'))
                ]))
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        '''
        for i = 1:2 {
            for j = i:(i * i)
                x = j;
        }'''
    )).stmt_set == [
           ForLoop(Id('i'), 1, 2, Block([
                ForLoop(Id('j'), Id('i'), BinExpr('*', Id('i'), Id('i')),
                    AssignStmt(Id('x'), Id('j'))
                )
            ]))
        ]
    assert parser.parse(scanner.tokenize(
        '''
        for i = 1:2
            for j = i:(i * i) {
                x = j;
            }
        '''
    )).stmt_set == [
            ForLoop(Id('i'), 1, 2,
                ForLoop(Id('j'), Id('i'), BinExpr('*', Id('i'), Id('i')), Block([
                    AssignStmt(Id('x'), Id('j'))
                ]))
            )
        ]
    assert parser.parse(scanner.tokenize(
        '''
        for i = 1:2
            for j = i:(i * i)
                x = j;'''
    )).stmt_set == [
            ForLoop(Id('i'), 1, 2,
                ForLoop(Id('j'), Id('i'), BinExpr('*', Id('i'), Id('i')),
                    AssignStmt(Id('x'), Id('j'))
                )
            )
        ]

def test_Ref():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        'x = a[1];'
    )).stmt_set[0].expr == Ref(Id('a'), Vector([1]))
    assert parser.parse(scanner.tokenize(
        'x = a[i, j, k];'
    )).stmt_set[0].expr == Ref(Id('a'), Vector([Id('i'), Id('j'), Id('k')]))

def test_Break():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        '''
        while(b) {
            a = 1;
            break;
        }
    '''
    )).stmt_set == [
            WhileLoop(Id('b'), Block([
                AssignStmt(Id('a'), 1),
                Break()
            ]))
        ]

def test_Continue():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        '''
        while(b) {
            continue;
            a = 1;
        }
    '''
    )).stmt_set == [
            WhileLoop(Id('b'), Block([
                Continue(),
                AssignStmt(Id('a'), 1)
            ]))
        ]

def test_Print():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        'print 2;'
    )).stmt_set == [Print([2])]
    assert parser.parse(scanner.tokenize(
        'print a;'
    )).stmt_set == [Print([Id('a')])]
    assert parser.parse(scanner.tokenize(
        'print a + 2;'
    )).stmt_set == [Print([BinExpr('+', Id('a'), 2)])]
    assert parser.parse(scanner.tokenize(
        'print a, 2;'
    )).stmt_set == [Print([Id('a'), 2])]
    assert parser.parse(scanner.tokenize(
        'print a, 2, b;'
    )).stmt_set == [Print([Id('a'), 2, Id('b')])]

def test_Return():
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(
        'return 2;'
    )).stmt_set == [Return([2])]
    assert parser.parse(scanner.tokenize(
        'return a;'
    )).stmt_set == [Return([Id('a')])]
    assert parser.parse(scanner.tokenize(
        'return a + 2;'
    )).stmt_set == [Return([BinExpr('+', Id('a'), 2)])]
    assert parser.parse(scanner.tokenize(
        'return a, b;'
    )).stmt_set == [Return([Id('a'), Id('b')])]
