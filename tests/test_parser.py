import pytest
from matrix_lang_interpreter.AST import *
from matrix_lang_interpreter.scanner import Scanner
from matrix_lang_interpreter.parser import Parser
from matrix_lang_interpreter.add_to_class import addToClass


@addToClass(IntNum)
def __eq__(self, other):
    if isinstance(other, int):
        return self.n == other
    return self.n == other.n

@addToClass(FloatNum)
def __eq__(self, other):
    if isinstance(other, float):
        return self.n == other
    return self.n == other.n

@addToClass(Id)
def __eq__(self, other):
    if isinstance(other, Id):
        return self.id == other.id
    return False

@addToClass(Break)
def __eq__(self, other):
    return isinstance(other, Break)

@addToClass(Continue)
def __eq__(self, other):
    return isinstance(other, Continue)

@pytest.mark.parametrize('test_input, expected', [
    ('x = 1 + 2;', BinExpr('+', 1, 2)),
    ('x = 1 - 2;', BinExpr('-', 1, 2)),
    ('x = 2 * 3;', BinExpr('*', 2, 3)),
    ('x = 3 / 2;', BinExpr('/', 3, 2)),
    ('x = (3 + 1) * 2;', BinExpr('*', BinExpr('+', 3, 1), 2)),
    ('x = 2 * (3 + 1);', BinExpr('*', 2, BinExpr('+', 3, 1))),
])
def test_BinExpr(test_input, expected):
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(test_input)).stmt_set[0].expr == expected

@pytest.mark.parametrize('test_input, expected', [
    ('x = A @ B;', MatMulBinExpr('@', Id('A'), Id('B'))),
    ('x = (A @ B) @ C;', MatMulBinExpr('@', MatMulBinExpr('@', Id('A'), Id('B')), Id('C'))),
    ('x = A @ (B @ C);', MatMulBinExpr('@', Id('A'), MatMulBinExpr('@', Id('B'), Id('C')))),
    ('x = A @ B @ C;', MatMulBinExpr('@', MatMulBinExpr('@', Id('A'), Id('B')), Id('C'))),
])
def test_MatMulBinExpr(test_input, expected):
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(test_input)).stmt_set[0].expr == expected


@pytest.mark.parametrize('test_input, expected', [
    ('x = -1;', UnExpr('-', 1)),
    ('x = +(3 + -1);', UnExpr('+', BinExpr('+', 3, UnExpr('-', 1)))),
    ("x = a';", UnExpr("'", Id('a'))),
])
def test_UnExpr(test_input, expected):
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(test_input)).stmt_set[0].expr == expected

@pytest.mark.parametrize('test_input, expected', [
    ('x = 2 * 3 + 1;', BinExpr('+', BinExpr('*', 2, 3), 1)),
    ('x = 1 + 2 * 3;', BinExpr('+', 1, BinExpr('*', 2, 3))),
    ('x = -1 + 2;', BinExpr('+', UnExpr('-', 1), 2)),
    ('x = 2 + -1;', BinExpr('+', 2, UnExpr('-', 1))),
    ('x = -2 - 1;', BinExpr('-', UnExpr('-', 2), 1)),
    ('x = -1 * 2;', BinExpr('*', UnExpr('-', 1), 2)),
    ('x = 2 * -1;', BinExpr('*', 2, UnExpr('-', 1))),
])
def test_Precedence(test_input, expected):
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(test_input)).stmt_set[0].expr == expected

@pytest.mark.parametrize('test_input, expected', [
    ('x = [];', Vector([])),
    ('x = [[]];', Vector([Vector([])])),
    ('x = [[[]]];', Vector([Vector([Vector([])])])),
    ('x = [1];', Vector([1])),
    ('x = [1, 2];', Vector([1, 2])),
    ('x = [[1, 2]];', Vector([Vector([1, 2])])),
    ('x = [[[1], 2]];', Vector([Vector([Vector([1]), 2])])),
    ('x = [[[1], [2]]];', Vector([Vector([Vector([1]), Vector([2])])])),
    ('x = [[1, 2], [3, 4]];', Vector([Vector([1, 2]), Vector([3, 4])])),
])
def test_Vector(test_input, expected):
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(test_input)).stmt_set[0].expr == expected

@pytest.mark.parametrize('test_input, expected', [
    ('x = zeros(2);', Zeros(Vector([2]))),
    ('x = zeros(2, 3);', Zeros(Vector([2, 3]))),
    ('x = ones(2);', Ones(Vector([2]))),
    ('x = ones(2, 3);', Ones(Vector([2, 3]))),
    ('x = eye(3);', Eye(3))
])
def test_SpecialMatrix(test_input, expected):
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(test_input)).stmt_set[0].expr == expected

@pytest.mark.parametrize('test_input, expected', [
    ('a = 5;', [AssignStmt(Id('a'), 5)]),
    ('b = 3; a = b;', [AssignStmt(Id('b'), 3), AssignStmt(Id('a'), Id('b'))]),
    ('a = 3 + 4 * 5;', [AssignStmt(Id('a'), BinExpr('+', 3, BinExpr('*', 4, 5)))]),
    ('a = b + c * d;', [AssignStmt(Id('a'), BinExpr('+', Id('b'), BinExpr('*', Id('c'), Id('d'))))]),
    ('a += 5;', [AssignStmt(Id('a'), BinExpr('+', Id('a'), 5))]),
    ('a -= 5;', [AssignStmt(Id('a'), BinExpr('-', Id('a'), 5))]),
    ('a *= 5;', [AssignStmt(Id('a'), BinExpr('*', Id('a'), 5))]),
    ('a /= 5;', [AssignStmt(Id('a'), BinExpr('/', Id('a'), 5))]),
    ('A = zeros(4);', [AssignStmt(Id('A'), Zeros(Vector([4])))]),
    ('A = eye(n);', [AssignStmt(Id('A'), Eye(Id('n')))]),
])
def test_AssignStmt(test_input, expected):
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(test_input)).stmt_set == expected

@pytest.mark.parametrize('test_input, expected', [
    ('x = a < b;', RelationExpr('<', Id('a'), Id('b'))),
    ('x = a > b;', RelationExpr('>', Id('a'), Id('b'))),
    ('x = a <= b;', RelationExpr('<=', Id('a'), Id('b'))),
    ('x = a >= b;', RelationExpr('>=', Id('a'), Id('b'))),
    ('x = a == b;', RelationExpr('==', Id('a'), Id('b'))),
    ('x = a != b;', RelationExpr('!=', Id('a'), Id('b'))),
    ('x = a + c != b;', RelationExpr('!=', BinExpr('+', Id('a'), Id('c')), Id('b'))),
    ('x = a == b + c;', RelationExpr('==', Id('a'), BinExpr('+', Id('b'), Id('c')))),
    ('x = a + c < b + d;', RelationExpr('<', BinExpr('+', Id('a'), Id('c')), BinExpr('+', Id('b'), Id('d'))))
])
def test_RelationExpr(test_input, expected):
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(test_input)).stmt_set[0].expr == expected

@pytest.mark.parametrize('test_input, expected', [
    ('{a = 1;}', [Block([AssignStmt(Id('a'), 1)])]),
    ('''{
            a = 1;
        }''', [Block([AssignStmt(Id('a'), 1)])]),
    ('{{a = 1;}}', [Block([Block([AssignStmt(Id('a'), 1)])])]),
    ('''{
            {
              a = 1;
            }
        }''',
        [Block([
            Block([
                AssignStmt(Id('a'), 1)
            ])
        ])]),
    ('''{
            b = 1;
            {
              a = 1;
            }
        }''',
        [Block([
            AssignStmt(Id('b'), 1),
            Block([
                AssignStmt(Id('a'), 1)
            ])
        ])]),
    ('''
        b = 1;
        {
            a = 1;
            {
                c = 1;
            }
        }''',
        [AssignStmt(Id('b'), 1),
            Block([
                AssignStmt(Id('a'), 1),
                Block([
                     AssignStmt(Id('c'), 1)
                ])
            ])
        ])
])
def test_Block(test_input, expected):
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(test_input)).stmt_set == expected

@pytest.mark.parametrize('test_input, expected', [
    ('if(b) {a = 1;}', [IfStmt(Id('b'), Block([AssignStmt(Id('a'), 1)]))]),
    ('if(b) a = 1;', [IfStmt(Id('b'), AssignStmt(Id('a'), 1))]),
    ('''if(b) {
            a = 1;
            c = a + b;
        }''', [
        IfStmt(Id('b'), Block([
            AssignStmt(Id('a'), 1),
            AssignStmt(Id('c'), BinExpr('+', Id('a'), Id('b')))
        ]))
    ]),
    ('''if(b) {
            a = 1;
            if(a > b) {
                b = 3;
            }
        }''', [
        IfStmt(Id('b'), Block([
            AssignStmt(Id('a'), 1),
            IfStmt(RelationExpr('>', Id('a'), Id('b')), Block([
                AssignStmt(Id('b'), 3)
            ]))
        ]))
    ]),
    ('''if(b) {
            a = 1;
            if(a > b)
                b = 3;
        }''', [
        IfStmt(Id('b'), Block([
            AssignStmt(Id('a'), 1),
            IfStmt(RelationExpr('>', Id('a'), Id('b')),
                AssignStmt(Id('b'), 3))
        ]))
    ]),
    ('''if(b)
            if(a > b)
                b = 3;
        ''', [
        IfStmt(Id('b'),
            IfStmt(RelationExpr('>', Id('a'), Id('b')),
                AssignStmt(Id('b'), 3)))
    ]),
    ('''if(b)
            a = 1;
        ''', [
        IfStmt(Id('b'),
            AssignStmt(Id('a'), 1))
    ]),
    ('''if(b)
            a = 1;
        if(a > b)
            b = 3;
        ''', [
        IfStmt(Id('b'),
            AssignStmt(Id('a'), 1)),
        IfStmt(RelationExpr('>', Id('a'), Id('b')),
            AssignStmt(Id('b'), 3))
    ]),
])
def test_IfStmt(test_input, expected):
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(test_input)).stmt_set == expected

@pytest.mark.parametrize('test_input, expected', [
    ('if(b) {a = 1;} else {a = 2;}', [
        IfElseStmt(Id('b'), Block([
            AssignStmt(Id('a'), 1)
        ]), Block([
            AssignStmt(Id('a'), 2)
        ]))
    ]),
    ('if(b) { a = 1; } else a = 2;', [
        IfElseStmt(Id('b'), Block([
            AssignStmt(Id('a'), 1)
        ]),
            AssignStmt(Id('a'), 2)
        )
    ]),
    ('if(b) a = 1; else { a = 2; }',[
        IfElseStmt(Id('b'),
            AssignStmt(Id('a'), 1),
            Block([
                AssignStmt(Id('a'), 2)
            ])
        )
    ]),
    ('if(b) a = 1; else a = 2;', [
        IfElseStmt(Id('b'),
            AssignStmt(Id('a'), 1),
            AssignStmt(Id('a'), 2)
        )
    ]),
    ('if(b) x = a; else { if (c) x = d; }', [
        IfElseStmt(Id('b'),
            AssignStmt(Id('x'), Id('a')),
            Block([
            IfStmt(Id('c'),
                AssignStmt(Id('x'), Id('d')),
            )
        ]))
    ]),
    ('if(b) x = a; else if (c) x = d;', [
        IfElseStmt(Id('b'),
            AssignStmt(Id('x'), Id('a')),
            IfStmt(Id('c'),
                AssignStmt(Id('x'), Id('d')),
            )
        )
    ]),
    ('if(b) x = a; else if (c) x = d; else x = e;', [
        IfElseStmt(Id('b'),
            AssignStmt(Id('x'), Id('a')),
            IfElseStmt(Id('c'),
                AssignStmt(Id('x'), Id('d')),
                AssignStmt(Id('x'), Id('e')),
            )
        )
    ]),
    ('if(b) x = a; if (c) x = d; else x = e;', [
        IfStmt(Id('b'), AssignStmt(Id('x'), Id('a'))),
        IfElseStmt(Id('c'), AssignStmt(Id('x'), Id('d')), AssignStmt(Id('x'), Id('e')),)
    ]),
    ('''if(b) {
            a = 1;
            if(a > b) {
                b = 3;
            } else
                b = 4;
        }''', [
        IfStmt(Id('b'), Block([
            AssignStmt(Id('a'), 1),
            IfElseStmt(RelationExpr('>', Id('a'), Id('b')), Block([
                AssignStmt(Id('b'), 3)
            ]), AssignStmt(Id('b'), 4))
        ]))
    ]),
    ('''if(b) {
            a = 1;
            if(a > b) {
                b = 3;
            } else {
                b = 4;
            }
        }''', [
        IfStmt(Id('b'), Block([
            AssignStmt(Id('a'), 1),
            IfElseStmt(RelationExpr('>', Id('a'), Id('b')), Block([
                AssignStmt(Id('b'), 3)
            ]), Block([
                AssignStmt(Id('b'), 4)
            ]))
        ]))
    ]),
    ('''if(b) {
            a = 1;
            if(a > b) {
                b = 3;
            } else {
                b = 4;
            }
        } else {
            c = 4;
        }''', [
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
    ]),
    ('''if(b)
            if(a)
                x = c;
            else
                x = d;
        ''', [
        IfStmt(Id('b'),
            IfElseStmt(Id('a'),
                AssignStmt(Id('x'), Id('c')),
                AssignStmt(Id('x'), Id('d'))
            )
        )
    ]),
])
def test_IfElseStmt(test_input, expected):
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(test_input)).stmt_set == expected

@pytest.mark.parametrize('test_input, expected', [
    ('while(b) {a = 1;}', [
        WhileLoop(Id('b'), Block([
            AssignStmt(Id('a'), 1)
        ]))
    ]),
    ('while(b) a = 1;', [
        WhileLoop(Id('b'),
            AssignStmt(Id('a'), 1)
        )
    ]),
    ('''while(b) {
            a = 1;
            c = a + b;
        }''', [
        WhileLoop(Id('b'), Block([
            AssignStmt(Id('a'), 1),
            AssignStmt(Id('c'), BinExpr('+', Id('a'), Id('b')))
        ]))
    ]),
    ('''while(b) {
            a = 1;
            while(a > b) {
                b = 3;
            }
        }''', [
        WhileLoop(Id('b'), Block([
            AssignStmt(Id('a'), 1),
            WhileLoop(RelationExpr('>', Id('a'), Id('b')), Block([
                AssignStmt(Id('b'), 3)
            ]))
        ]))
    ]),
    ('''while(b) {
            a = 1;
            while(a > b)
                b = 3;
        }''', [
        WhileLoop(Id('b'), Block([
            AssignStmt(Id('a'), 1),
            WhileLoop(RelationExpr('>', Id('a'), Id('b')),
                AssignStmt(Id('b'), 3)
            )
        ]))
    ]),
    ('''while(b)
            a = 1;
        ''', [
        WhileLoop(Id('b'),
            AssignStmt(Id('a'), 1)
        )
    ]),
    ('''while(b)
            while(a > b)
                b = 3;''', [
        WhileLoop(Id('b'),
            WhileLoop(RelationExpr('>', Id('a'), Id('b')),
                AssignStmt(Id('b'), 3)
            )
        )
    ]),
    ('''while(b)
            a = 1;
        while(a > b)
            b = 3;
        ''', [
        WhileLoop(Id('b'),
            AssignStmt(Id('a'), 1)
        ),
        WhileLoop(RelationExpr('>', Id('a'), Id('b')),
            AssignStmt(Id('b'), 3)
        )
    ]),
])
def test_WhileLoop(test_input, expected):
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(test_input)).stmt_set == expected

@pytest.mark.parametrize('test_input, expected', [
    ('for i = 1:2 { x = i; }', [
        ForLoop(Id('i'), 1, 2, Block([
            AssignStmt(Id('x'), Id('i'))
        ]))
    ]),
    ('''
        for i = 1:2 {
            x = i;
        }''', [
        ForLoop(Id('i'), 1, 2, Block([
            AssignStmt(Id('x'), Id('i'))
        ]))
    ]),
    ('''
        for i = 1:2
            x = i;''', [
        ForLoop(Id('i'), 1, 2,
            AssignStmt(Id('x'), Id('i'))
        )
    ]),
    ('''
        for i = 1:2 {
            for j = i:(i * i) {
                x = j;
            }
        }''', [
        ForLoop(Id('i'), 1, 2, Block([
            ForLoop(Id('j'), Id('i'), BinExpr('*', Id('i'), Id('i')), Block([
                AssignStmt(Id('x'), Id('j'))
            ]))
        ]))
    ]),
    ('''
        for i = 1:2 {
            for j = i:(i * i)
                x = j;
        }''', [
        ForLoop(Id('i'), 1, 2, Block([
            ForLoop(Id('j'), Id('i'), BinExpr('*', Id('i'), Id('i')),
                AssignStmt(Id('x'), Id('j'))
            )
        ]))
    ]),
    ('''
        for i = 1:2
            for j = i:(i * i) {
                x = j;
            }
        ''', [
        ForLoop(Id('i'), 1, 2,
            ForLoop(Id('j'), Id('i'), BinExpr('*', Id('i'), Id('i')), Block([
                AssignStmt(Id('x'), Id('j'))
            ]))
        )
    ]),
    ('''
        for i = 1:2
            for j = i:(i * i)
                x = j;''', [
        ForLoop(Id('i'), 1, 2,
            ForLoop(Id('j'), Id('i'), BinExpr('*', Id('i'), Id('i')),
                AssignStmt(Id('x'), Id('j'))
            )
        )
    ])
])
def test_ForLoop(test_input, expected):
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(test_input)).stmt_set == expected

@pytest.mark.parametrize('test_input, expected', [
    ('x = a[1];', Ref(Id('a'), Vector([1]))),
    ('x = a[i, j, k];', Ref(Id('a'), Vector([Id('i'), Id('j'), Id('k')])))
])
def test_Ref(test_input, expected):
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(test_input)).stmt_set[0].expr == expected

@pytest.mark.parametrize('test_input, expected', [
    ('''
        while(b) {
            a = 1;
            break;
        }
    ''', [
        WhileLoop(Id('b'), Block([
            AssignStmt(Id('a'), 1),
            Break()
        ]))
    ]),
    ('''
        while(b) {
            continue;
            a = 1;
        }
    ''', [
        WhileLoop(Id('b'), Block([
            Continue(),
            AssignStmt(Id('a'), 1)
        ]))
    ]),
])
def test_BreakContinue(test_input, expected):
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(test_input)).stmt_set == expected

@pytest.mark.parametrize('test_input, expected', [
    ('print 2;', [Print([2])]),
    ('print a;', [Print([Id('a')])]),
    ('print a + 2;', [Print([BinExpr('+', Id('a'), 2)])]),
    ('print a, 2;', [Print([Id('a'), 2])]),
    ('print a, 2, b;', [Print([Id('a'), 2, Id('b')])]),
    ('return 2;', [Return([2])]),
    ('return a;', [Return([Id('a')])]),
    ('return a + 2;', [Return([BinExpr('+', Id('a'), 2)])]),
    ('return a, b;', [Return([Id('a'), Id('b')])])
])
def test_PrintReturn(test_input, expected):
    scanner = Scanner()
    parser = Parser()
    assert parser.parse(scanner.tokenize(test_input)).stmt_set == expected
