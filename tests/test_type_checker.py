import pytest
from matrix_lang_interpreter.type_checker import TypeChecker
import matrix_lang_interpreter.AST as AST
from matrix_lang_interpreter.writer_maybe import WriterJust, WriterNothing
from matrix_lang_interpreter.symbol_table import Symbol, VariableSymbol


@pytest.mark.parametrize('node, expected', [
    (
        AST.AST([]),
        WriterJust(Symbol(None, None))
    ),
    (
        AST.AST([
            AST.Print([AST.IntNum(5)])
        ]),
        WriterJust(Symbol('int', ()))
    ),
    (
        AST.AST([
            AST.Print([AST.Id('x')])
        ]),
        WriterNothing()
    ),
])
def test_visit_AST(node, expected):
    typeChecker = TypeChecker()
    assert typeChecker.visit(node) == expected

@pytest.mark.parametrize('node, expected', [
    (
        AST.Block([]),
        WriterJust(Symbol(None, None))
    ),
    (
        AST.Block([
            AST.Print([AST.IntNum(5)])
        ]),
        WriterJust(Symbol('int', ()))
    ),
    (
        AST.Block([
            AST.Print([AST.Id('x')])
        ]),
        WriterNothing()
    ),
])
def test_visit_Block(node, expected):
    typeChecker = TypeChecker()
    assert typeChecker.visit(node) == expected

def test_visit_AssignStmt():
    typeChecker = TypeChecker()

    assert typeChecker.symbolTable.get('x') == None
    assert typeChecker.visit(AST.Id('x')) == WriterNothing()
    node = AST.AssignStmt(
        AST.Id('x'),
        AST.IntNum(5)
    )
    assert typeChecker.visit(node) == WriterJust(Symbol(None, None))
    assert typeChecker.symbolTable.get('x') == VariableSymbol('int', (), name='x')
    assert typeChecker.visit(AST.Id('x')) == WriterJust(VariableSymbol('int', (), name='x'))

    node = AST.AssignStmt(
        AST.Id('x'),
        AST.BinExpr('+', AST.IntNum(5), AST.String('a'))
    )
    assert typeChecker.visit(node) == WriterNothing()
    assert typeChecker.symbolTable.get('x') == VariableSymbol('int', (), name='x')
    assert typeChecker.visit(AST.Id('x')) == WriterJust(VariableSymbol('int', (), name='x'))

@pytest.mark.parametrize('node, expected', [
    (
        AST.IfStmt(
            AST.RelationExpr('==', AST.IntNum(4), AST.IntNum(5)),
            AST.Block([]),
        ),
        WriterJust(Symbol(None, None))
    ),
    (
        AST.IfStmt(
            AST.BinExpr('+', AST.IntNum(4), AST.IntNum(5)),
            AST.Block([]),
        ),
       WriterNothing()
    )
])
def test_visit_IfStmt(node, expected):
    typeChecker = TypeChecker()
    assert typeChecker.visit(node) == expected

@pytest.mark.parametrize('node, expected', [
    (
        AST.IfElseStmt(
            AST.RelationExpr('==', AST.IntNum(4), AST.IntNum(5)),
            AST.Block([]),
            AST.Block([])
        ),
        WriterJust(Symbol(None, None))
    ),
    (
        AST.IfElseStmt(
            AST.BinExpr('+', AST.IntNum(4), AST.IntNum(5)),
            AST.Block([]),
            AST.Block([])
        ),
       WriterNothing()
    )
])
def test_visit_IfElseStmt(node, expected):
    typeChecker = TypeChecker()
    assert typeChecker.visit(node) == expected

@pytest.mark.parametrize('node, expected', [
    (
        AST.WhileLoop(
            AST.RelationExpr('==', AST.IntNum(4), AST.IntNum(5)),
            AST.Block([])
        ),
        WriterJust(Symbol(None, None))
    ),
    (
        AST.WhileLoop(
            AST.BinExpr('+', AST.IntNum(4), AST.IntNum(5)),
            AST.Block([])
        ),
       WriterNothing()
    )
])
def test_visit_WhileLoop(node, expected):
    typeChecker = TypeChecker()
    assert typeChecker.visit(node) == expected

@pytest.mark.parametrize('node, expected', [
    (
        AST.ForLoop(
            AST.Id('i'),
            AST.IntNum(4),
            AST.IntNum(5),
            AST.Block([])
        ),
        WriterJust(Symbol(None, None))
    ),
    (
        AST.ForLoop(
            AST.Id('i'),
            AST.FloatNum(4.0),
            AST.IntNum(5),
            AST.Block([])
        ),
        WriterNothing()
    ),
    (
        AST.ForLoop(
            AST.Id('i'),
            AST.IntNum(5),
            AST.FloatNum(4.0),
            AST.Block([])
        ),
        WriterNothing()
    ),
    (
        AST.ForLoop(
            AST.Id('i'),
            AST.Vector([AST.IntNum(5)]),
            AST.IntNum(6),
            AST.Block([])
        ),
        WriterNothing()
    ),
    (
        AST.ForLoop(
            AST.Id('i'),
            AST.IntNum(6),
            AST.Vector([AST.IntNum(5)]),
            AST.Block([])
        ),
        WriterNothing()
    ),
])
def test_visit_ForLoop(node, expected):
    typeChecker = TypeChecker()
    assert typeChecker.visit(node) == expected

def test_visit_Break():
    typeChecker = TypeChecker()
    node = AST.Continue()
    assert typeChecker.loopState == False
    assert typeChecker.visit(node) == WriterNothing()

    typeChecker.loopState = True
    assert typeChecker.visit(node) == WriterJust(Symbol(None, None))
    typeChecker.loopState = False

    node = AST.ForLoop(
        AST.Id('i'),
        AST.IntNum(4),
        AST.IntNum(5),
        AST.Block([AST.Break()])
    )
    assert typeChecker.visit(node) == WriterJust(Symbol(None, None))

def test_visit_Continue():
    typeChecker = TypeChecker()
    node = AST.Continue()
    assert typeChecker.loopState == False
    assert typeChecker.visit(node) == WriterNothing()

    typeChecker.loopState = True
    assert typeChecker.visit(node) == WriterJust(Symbol(None, None))
    typeChecker.loopState = False

    node = AST.ForLoop(
        AST.Id('i'),
        AST.IntNum(4),
        AST.IntNum(5),
        AST.Block([AST.Continue()])
    )
    assert typeChecker.visit(node) == WriterJust(Symbol(None, None))

@pytest.mark.parametrize('node, expected', [
    (
        AST.Print([
            AST.IntNum(5)
        ]),
        WriterJust(Symbol('int', ()))
    ),
    (
        AST.Print([]),
        WriterJust(Symbol(None, None))
    )
])
def test_visit_Print(node, expected):
    typeChecker = TypeChecker()
    assert typeChecker.visit(node) == expected

@pytest.mark.parametrize('node, expected', [
    (
        AST.Return([
            AST.IntNum(5)
        ]),
        WriterJust(Symbol('int', ()))
    ),
    (
        AST.Return([]),
        WriterJust(Symbol(None, None))
    )
])
def test_visit_Return(node, expected):
    typeChecker = TypeChecker()
    assert typeChecker.visit(node) == expected

@pytest.mark.parametrize('node, expected', [
    (
        AST.BinExpr('+', AST.IntNum(5), AST.IntNum(4)),
        WriterJust(Symbol('int', ()))
    ),
    (
        AST.BinExpr('-', AST.FloatNum(5), AST.FloatNum(3)),
        WriterJust(Symbol('float', ()))
    ),
    (
        AST.BinExpr('*', AST.IntNum(5), AST.FloatNum(3)),
        WriterJust(Symbol('float', ()))
    ),
    (
        AST.BinExpr('/', AST.FloatNum(5), AST.IntNum(3)),
        WriterJust(Symbol('float', ()))
    ),
    (
        AST.BinExpr('*', AST.IntNum(5), AST.String('ala')),
        WriterJust(Symbol('string', ()))
    ),
    (
        AST.BinExpr('*', AST.String('ala'), AST.IntNum(5)),
        WriterJust(Symbol('string', ()))
    ),
    (
        AST.BinExpr('+', AST.String('ala'), AST.String('ola')),
        WriterJust(Symbol('string', ()))
    ),
    (
        AST.BinExpr('*', AST.String('ala'), AST.String('ola')),
        WriterNothing()
    ),
    (
        AST.BinExpr('+', AST.IntNum(5), AST.String('ala')),
        WriterNothing()
    ),
    (
        AST.BinExpr('+', AST.IntNum(5), AST.Vector([AST.IntNum(4)])),
        WriterNothing()
    ),
    (
        AST.BinExpr('+', AST.Vector([AST.IntNum(1)]), AST.Vector([AST.IntNum(4)])),
        WriterJust(Symbol('int', (1,)))
    ),
    (
        AST.BinExpr('+', AST.Vector([AST.IntNum(1)]), AST.Vector([AST.FloatNum(4)])),
        WriterJust(Symbol('float', (1,)))
    ),
    (
        AST.BinExpr('*', AST.Vector([AST.Vector([AST.IntNum(1)])]), AST.Vector([AST.FloatNum(4)])),
        WriterNothing()
    ),
    (
        AST.BinExpr('*', AST.Vector([AST.Vector([AST.IntNum(1)])]), AST.Vector([AST.Vector([AST.FloatNum(4)])])),
        WriterJust(Symbol('float', (1, 1)))
    ),
    (
        AST.BinExpr('*', AST.Vector([AST.Vector([AST.IntNum(1)])]), AST.Vector([AST.Vector([AST.FloatNum(4), AST.FloatNum(5)])])),
        WriterNothing()
    )
])
def test_visit_BinExpr(node, expected):
    typeChecker = TypeChecker()
    assert typeChecker.visit(node) == expected

@pytest.mark.parametrize('node, expected', [
    (
        AST.MatMulBinExpr('@', AST.IntNum(5), AST.IntNum(4)),
        WriterNothing()
    ),
    (
        AST.MatMulBinExpr('@', AST.FloatNum(5), AST.FloatNum(3)),
        WriterNothing()
    ),
    (
        AST.MatMulBinExpr('@', AST.IntNum(5), AST.String('ala')),
        WriterNothing()
    ),
    (
        AST.MatMulBinExpr('@', AST.IntNum(5), AST.Vector([AST.IntNum(4)])),
        WriterNothing()
    ),
    (
        AST.MatMulBinExpr('@',
            AST.Vector([
                AST.IntNum(1)
            ]),
            AST.Vector([
                AST.IntNum(4)
            ])
        ),
        WriterJust(Symbol('int', ()))
    ),
    (
        AST.MatMulBinExpr('@',
            AST.Vector([
                AST.IntNum(1)
            ]),
            AST.Vector([
                AST.FloatNum(4)
            ])
        ),
        WriterJust(Symbol('float', ()))
    ),
    (
        AST.MatMulBinExpr('@',
            AST.Vector([
                AST.IntNum(1),
                AST.IntNum(1)
            ]),
            AST.Vector([
                AST.IntNum(4)
            ])
        ),
        WriterNothing()
    ),
    (
        AST.MatMulBinExpr('@',
            AST.Vector([
                AST.IntNum(1)
            ]),
            AST.Vector([
                AST.IntNum(4),
                AST.IntNum(1)
            ])
        ),
        WriterNothing()
    ),
    (
        AST.MatMulBinExpr('@',
            AST.Vector([
                AST.IntNum(1),
                AST.IntNum(2)
            ]),
            AST.Vector([
                AST.IntNum(4),
                AST.IntNum(1)
            ])),
        WriterJust(Symbol('int', ()))
    ),
    (
        AST.MatMulBinExpr('@',
            AST.Vector([
                AST.IntNum(1),
                AST.IntNum(2),
                AST.IntNum(3)
            ]),
            AST.Vector([
                AST.IntNum(4),
                AST.IntNum(1),
                AST.IntNum(2)
            ])),
        WriterJust(Symbol('int', ()))
    ),
    (
        AST.MatMulBinExpr('@',
            AST.Vector([
                AST.Vector([
                    AST.IntNum(1)
                ])
            ]),
            AST.Vector([
                AST.IntNum(4)
            ])),
        WriterJust(Symbol('int', (1,)))
    ),
    (
        AST.MatMulBinExpr('@',
            AST.Vector([
                AST.Vector([
                    AST.IntNum(1)
                ])
            ]),
            AST.Vector([
                AST.IntNum(4),
                AST.IntNum(1)
            ])),
        WriterNothing()
    ),
    (
        AST.MatMulBinExpr('@',
            AST.Vector([
                AST.Vector([
                    AST.IntNum(1),
                    AST.IntNum(1)
                ])
            ]),
            AST.Vector([
                AST.IntNum(4),
            ])),
        WriterNothing()
    ),
    (
        AST.MatMulBinExpr('@',
            AST.Vector([
                AST.Vector([
                    AST.IntNum(1),
                    AST.IntNum(1)
                ])
            ]),
            AST.Vector([
                AST.IntNum(4),
                AST.IntNum(4),
            ])),
        WriterJust(Symbol('int', (1,)))
    ),
    (
        AST.MatMulBinExpr('@',
            AST.Vector([
                AST.Vector([
                    AST.IntNum(1),
                    AST.IntNum(1)
                ]),
                AST.Vector([
                    AST.IntNum(1),
                    AST.IntNum(1)
                ])
            ]),
            AST.Vector([
                AST.IntNum(4),
                AST.IntNum(4),
            ])),
        WriterJust(Symbol('int', (2,)))
    ),
    (
        AST.MatMulBinExpr('@',
            AST.Vector([
                AST.Vector([
                    AST.IntNum(1),
                    AST.IntNum(1)
                ]),
                AST.Vector([
                    AST.IntNum(1),
                    AST.IntNum(1)
                ]),
                AST.Vector([
                    AST.IntNum(1),
                    AST.IntNum(1)
                ])
            ]),
            AST.Vector([
                AST.IntNum(4),
                AST.IntNum(4),
            ])),
        WriterJust(Symbol('int', (3,)))
    ),
    (
        AST.MatMulBinExpr('@',
            AST.Vector([
                AST.IntNum(4),
                AST.IntNum(4),
                AST.IntNum(4)
            ]),
            AST.Vector([
                AST.Vector([
                    AST.IntNum(1),
                    AST.IntNum(1)
                ]),
                AST.Vector([
                    AST.IntNum(1),
                    AST.IntNum(1)
                ]),
                AST.Vector([
                    AST.IntNum(1),
                    AST.IntNum(1)
                ])
            ])),
        WriterJust(Symbol('int', (2,)))
    ),
    (
        AST.MatMulBinExpr('@',
            AST.Vector([
                AST.IntNum(4),
                AST.IntNum(4),
            ]),
            AST.Vector([
                AST.Vector([
                    AST.IntNum(1),
                    AST.IntNum(1)
                ]),
                AST.Vector([
                    AST.IntNum(1),
                    AST.IntNum(1)
                ]),
                AST.Vector([
                    AST.IntNum(1),
                    AST.IntNum(1)
                ])
            ])),
        WriterNothing()
    ),
    (
        AST.MatMulBinExpr('@',
            AST.Vector([
                AST.Vector([
                    AST.IntNum(1)
                ])
            ]),
            AST.Vector([
                AST.Vector([
                    AST.IntNum(4)
                ])
            ])),
        WriterJust(Symbol('int', (1, 1)))
    ),
    (
        AST.MatMulBinExpr('@',
            AST.Vector([
                AST.Vector([
                    AST.IntNum(1),
                ]),
                AST.Vector([
                    AST.IntNum(1),
                ])
            ]),
            AST.Vector([
                AST.Vector([
                    AST.IntNum(4),
                    AST.IntNum(4)
                ])
            ])),
        WriterJust(Symbol('int', (2, 2)))
    ),
    (
        AST.MatMulBinExpr('@',
            AST.Vector([
                AST.Vector([
                    AST.IntNum(1),
                    AST.IntNum(1),
                    AST.IntNum(3)
                ])
            ]),
            AST.Vector([
                AST.Vector([
                    AST.IntNum(4)
                ]),
                AST.Vector([
                    AST.IntNum(4)
                ]),
                AST.Vector([
                    AST.IntNum(4)
                ]),
            ])),
        WriterJust(Symbol('int', (1, 1)))
    ),
    (
        AST.MatMulBinExpr('@',
            AST.Vector([
                AST.Vector([
                    AST.IntNum(1),
                    AST.IntNum(1),
                    AST.IntNum(3)
                ]),
                AST.Vector([
                    AST.IntNum(1),
                    AST.IntNum(1),
                    AST.IntNum(3)
                ]),
                AST.Vector([
                    AST.IntNum(1),
                    AST.IntNum(1),
                    AST.IntNum(3)
                ]),
                AST.Vector([
                    AST.IntNum(1),
                    AST.IntNum(1),
                    AST.IntNum(3)
                ])
            ]),
            AST.Vector([
                AST.Vector([
                    AST.IntNum(4),
                    AST.IntNum(4)
                ]),
                AST.Vector([
                    AST.IntNum(4),
                    AST.IntNum(4)
                ]),
                AST.Vector([
                    AST.IntNum(4),
                    AST.IntNum(4)
                ]),
            ])),
        WriterJust(Symbol('int', (4, 2)))
    ),
])
def test_visit_MatMulBinExpr(node, expected):
    typeChecker = TypeChecker()
    assert typeChecker.visit(node) == expected

@pytest.mark.parametrize('node, expected', [
    (
        AST.RelationExpr('==', AST.IntNum(5), AST.IntNum(4)),
        WriterJust(Symbol('bool', ()))
    ),
    (
        AST.RelationExpr('!=', AST.IntNum(5), AST.IntNum(4)),
        WriterJust(Symbol('bool', ()))
    ),
    (
        AST.RelationExpr('==', AST.FloatNum(5), AST.FloatNum(3)),
        WriterJust(Symbol('bool', ()))
    ),
    (
        AST.RelationExpr('!=', AST.FloatNum(5), AST.FloatNum(3)),
        WriterJust(Symbol('bool', ()))
    ),
    (
        AST.RelationExpr('>', AST.IntNum(5), AST.FloatNum(3)),
        WriterJust(Symbol('bool', ()))
    ),
    (
        AST.RelationExpr('==', AST.IntNum(5), AST.FloatNum(3)),
        WriterJust(Symbol('bool', ()))
    ),
    (
        AST.RelationExpr('<', AST.FloatNum(5), AST.IntNum(3)),
        WriterJust(Symbol('bool', ()))
    ),
    (
        AST.RelationExpr('==', AST.IntNum(5), AST.String('ala')),
        WriterNothing()
    ),
    (
        AST.RelationExpr('>', AST.String('ala'), AST.IntNum(5)),
        WriterNothing()
    ),
    (
        AST.RelationExpr('==', AST.String('ala'), AST.String('ola')),
        WriterJust(Symbol('bool', ()))
    ),
    (
        AST.RelationExpr('!=', AST.String('ala'), AST.String('ola')),
        WriterJust(Symbol('bool', ()))
    ),
    (
        AST.RelationExpr('<=', AST.String('ala'), AST.String('ola')),
        WriterNothing()
    ),
    (
        AST.RelationExpr('+', AST.IntNum(5), AST.Vector([AST.IntNum(4)])),
        WriterNothing()
    ),
    (
        AST.RelationExpr('==', AST.Vector([AST.IntNum(1)]), AST.Vector([AST.IntNum(4)])),
        WriterJust(Symbol('bool', ()))
    ),
    (
        AST.RelationExpr('>=', AST.Vector([AST.IntNum(1)]), AST.Vector([AST.IntNum(4)])),
        WriterJust(Symbol('bool', ()))
    ),
    (
        AST.RelationExpr('>', AST.Vector([AST.Vector([AST.IntNum(1)])]), AST.Vector([AST.FloatNum(4)])),
        WriterNothing()
    ),
    (
        AST.RelationExpr('==', AST.Vector([AST.Vector([AST.IntNum(1)])]), AST.Vector([AST.Vector([AST.FloatNum(4)])])),
        WriterJust(Symbol('bool', ()))
    ),
    (
        AST.RelationExpr('==', AST.Vector([AST.Vector([AST.IntNum(1)])]), AST.Vector([AST.Vector([AST.FloatNum(4), AST.FloatNum(5)])])),
        WriterNothing()
    )
])
def test_visit_RelationExpr(node, expected):
    typeChecker = TypeChecker()
    assert typeChecker.visit(node) == expected

@pytest.mark.parametrize('node, expected', [
    (
        AST.UnExpr('+', AST.IntNum(5)),
        WriterJust(Symbol('int', ()))
    ),
    (
        AST.UnExpr('-', AST.FloatNum(5)),
        WriterJust(Symbol('float', ()))
    )
])
def test_visit_UnExpr(node, expected):
    typeChecker = TypeChecker()
    assert typeChecker.visit(node) == expected

@pytest.mark.parametrize('node, expected', [
    (
        AST.Vector([]),
        WriterJust(Symbol('int', (0,)))
    ),
    (
        AST.Vector([
            AST.IntNum(4)
        ]),
        WriterJust(Symbol('int', (1,)))
    ),
    (
        AST.Vector([
            AST.FloatNum(4)
        ]),
        WriterJust(Symbol('float', (1,)))
    ),
    (
        AST.Vector([
            AST.IntNum(4),
            AST.IntNum(5)
        ]),
        WriterJust(Symbol('int', (2,)))
    ),
    (
        AST.Vector([
            AST.IntNum(4),
            AST.FloatNum(5)
        ]),
        WriterNothing()
    ),
    (
        AST.Vector([
            AST.Vector([
                AST.IntNum(4),
                AST.IntNum(5)
            ]),
        ]),
        WriterJust(Symbol('int', (1, 2)))
    ),
    (
        AST.Vector([
            AST.Vector([
                AST.IntNum(4),
                AST.IntNum(5)
            ]),
            AST.Vector([
                AST.IntNum(3),
                AST.IntNum(1)
            ]),
        ]),
        WriterJust(Symbol('int', (2, 2)))
    ),
    (
        AST.Vector([
            AST.Vector([
                AST.IntNum(5)
            ]),
            AST.Vector([
                AST.IntNum(3),
                AST.IntNum(1)
            ]),
        ]),
        WriterNothing()
    ),
    (
        AST.Vector([
            AST.Vector([]),
        ]),
        WriterJust(Symbol('int', (1, 0)))
    ),
    (
        AST.Vector([
            AST.Vector([]),
            AST.Vector([]),
        ]),
        WriterJust(Symbol('int', (2, 0)))
    ),
    (
        AST.Vector([
            AST.Vector([
                AST.Vector([]),
            ]),
            AST.Vector([
                AST.Vector([]),
            ]),
        ]),
        WriterJust(Symbol('int', (2, 1, 0)))
    ),
    (
        AST.Vector([
            AST.Vector([
                AST.Vector([
                    AST.IntNum(4),
                    AST.IntNum(5),
                    AST.IntNum(4),
                ]),
            ]),
            AST.Vector([
                AST.Vector([
                    AST.IntNum(2),
                    AST.IntNum(3),
                    AST.IntNum(4),
                ]),
            ]),
        ]),
        WriterJust(Symbol('int', (2, 1, 3)))
    )
])
def test_visit_Vector(node, expected):
    typeChecker = TypeChecker()
    assert typeChecker.visit(node) == expected

@pytest.mark.parametrize('node, expected', [
    (
        AST.Zeros(
            AST.Vector([
                AST.IntNum(4)
            ])
        ),
        WriterJust(Symbol('int', (4,)))
    ),
    (
        AST.Zeros(
            AST.Vector([
                AST.IntNum(4),
                AST.IntNum(3)
            ])
        ),
        WriterJust(Symbol('int', (4, 3)))
    ),
    (
        AST.Zeros(
            AST.Vector([])
        ),
        WriterNothing()
    ),
    (
        AST.Zeros(
            AST.Vector([
                AST.FloatNum(4)
            ])
        ),
        WriterNothing()
    ),
])
def test_visit_Zeros(node, expected):
    typeChecker = TypeChecker()
    assert typeChecker.visit(node) == expected


@pytest.mark.parametrize('node, expected', [
    (
        AST.Ones(
            AST.Vector([
                AST.IntNum(4)
            ])
        ),
        WriterJust(Symbol('int', (4,)))
    ),
    (
        AST.Ones(
            AST.Vector([
                AST.IntNum(4),
                AST.IntNum(3)
            ])
        ),
        WriterJust(Symbol('int', (4, 3)))
    ),
    (
        AST.Ones(
            AST.Vector([])
        ),
        WriterNothing()
    ),
    (
        AST.Ones(
            AST.Vector([
                AST.FloatNum(4)
            ])
        ),
        WriterNothing()
    ),
])
def test_visit_Ones(node, expected):
    typeChecker = TypeChecker()
    assert typeChecker.visit(node) == expected


@pytest.mark.parametrize('node, expected', [
    (
        AST.Eye(AST.IntNum(4)),
        WriterJust(Symbol('int', (4, 4)))
    ),
    (
        AST.Eye(AST.FloatNum(4)),
        WriterNothing()
    )
])
def test_visit_Eye(node, expected):
    typeChecker = TypeChecker()
    assert typeChecker.visit(node) == expected

@pytest.mark.parametrize('node, expected', [
    (
        AST.Ref(
            AST.Zeros(
                AST.Vector([
                    AST.IntNum(1)
                ])
            ),
            AST.Vector([
                AST.IntNum(0)
            ])
        ),
        WriterJust(
            VariableSymbol('int', ())
        )
    ),
    (
        AST.Ref(
            AST.Zeros(
                AST.Vector([
                    AST.IntNum(1)
                ])
            ),
            AST.Vector([
                AST.IntNum(1)
            ])
        ),
        WriterNothing()
    ),
    (
        AST.Ref(
            AST.Zeros(
                AST.Vector([
                    AST.IntNum(1),
                    AST.IntNum(2)
                ])
            ),
            AST.Vector([
                AST.IntNum(0)
            ])
        ),
        WriterJust(
            VariableSymbol('int', (2,))
        )
    ),
    (
        AST.Ref(
            AST.Zeros(
                AST.Vector([
                    AST.IntNum(1),
                    AST.IntNum(2)
                ])
            ),
            AST.Vector([
                AST.IntNum(1)
            ])
        ),
        WriterNothing()
    ),
    (
        AST.Ref(
            AST.Zeros(
                AST.Vector([
                    AST.IntNum(2),
                    AST.IntNum(2)
                ])
            ),
            AST.Vector([
                AST.IntNum(1),
                AST.IntNum(2),
            ])
        ),
        WriterNothing()
    ),
    (
        AST.Ref(
            AST.Zeros(
                AST.Vector([
                    AST.IntNum(2),
                    AST.IntNum(2)
                ])
            ),
            AST.Vector([
                AST.IntNum(1),
                AST.IntNum(1),
                AST.IntNum(1),
            ])
        ),
        WriterNothing()
    ),
    (
        AST.Ref(
            AST.Zeros(
                AST.Vector([
                    AST.IntNum(2),
                    AST.IntNum(2)
                ])
            ),
            AST.Vector([])
        ),
        WriterNothing()
    ),
    (
        AST.Ref(
            AST.Zeros(
                AST.Vector([
                    AST.IntNum(2),
                    AST.IntNum(2)
                ])
            ),
            AST.Vector([
                AST.FloatNum(1.0),
            ])
        ),
        WriterNothing()
    ),
])
def test_visit_Ref(node, expected):
    typeChecker = TypeChecker()
    assert typeChecker.visit(node) == expected

def test_visit_Id_from_symbolTable():
    typeChecker = TypeChecker()
    node = AST.Id('x', 5)
    assert typeChecker.visit(node) == WriterNothing()

    symbol = VariableSymbol(None, None, name='x')
    typeChecker.symbolTable.put('x', symbol)
    assert typeChecker.visit(node) == WriterJust(symbol)

def test_visit_Id_new():
    typeChecker = TypeChecker()
    node = AST.Id('x')
    assert typeChecker.assignmentState == False
    assert typeChecker.visit(node) == WriterNothing()

    typeChecker.assignmentState = True
    symbol = VariableSymbol(None, None, name='x')
    assert typeChecker.visit(node) == WriterJust(symbol)
    assert typeChecker.symbolTable.get('x') == symbol
    assert typeChecker.visit(node) == WriterJust(symbol)

@pytest.mark.parametrize('node, expected', [
    (AST.IntNum(2), WriterJust(Symbol('int', ())))
])
def test_visit_IntNum(node, expected):
    typeChecker = TypeChecker()
    assert typeChecker.visit(node) == expected

@pytest.mark.parametrize('node, expected', [
    (AST.FloatNum(2.0), WriterJust(Symbol('float', ())))
])
def test_visit_FloatNum(node, expected):
    typeChecker = TypeChecker()
    assert typeChecker.visit(node) == expected

@pytest.mark.parametrize('node, expected', [
    (AST.String('ala ma kota'), WriterJust(Symbol('string', ())))
])
def test_visit_String(node, expected):
    typeChecker = TypeChecker()
    assert typeChecker.visit(node) == expected
