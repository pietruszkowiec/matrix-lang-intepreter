import pytest
from matrix_lang_interpreter.type_checker import TypeChecker
import matrix_lang_interpreter.AST as AST
from matrix_lang_interpreter.writer_maybe import WriterJust, WriterNothing
from matrix_lang_interpreter.symbol_table import Symbol, VariableSymbol


def test_visit_Id_from_symbolTable():
    typeChecker = TypeChecker()
    node = AST.Id('x', 5)
    assert typeChecker.visit(node) == WriterNothing()

    symbol = VariableSymbol(5, None, None, 'x')
    typeChecker.symbolTable.put('x', symbol)
    assert typeChecker.visit(node) == WriterJust(symbol)

def test_visit_Id_new():
    typeChecker = TypeChecker()
    node = AST.Id('x', 5)
    assert typeChecker.assignmentState == False
    assert typeChecker.visit(node) == WriterNothing()

    typeChecker.assignmentState = True
    symbol = VariableSymbol(5, None, None, 'x')
    assert typeChecker.visit(node) == WriterJust(symbol)
    assert typeChecker.symbolTable.get('x') == symbol
    assert typeChecker.visit(node) == WriterJust(symbol)

@pytest.mark.parametrize('node, expected', [
    (AST.IntNum(2, 1), WriterJust(Symbol(1, 'int', ())))
])
def test_visit_IntNum(node, expected):
    typeChecker = TypeChecker()
    assert typeChecker.visit(node) == expected

@pytest.mark.parametrize('node, expected', [
    (AST.FloatNum(2.0, 3), WriterJust(Symbol(3, 'float', ())))
])
def test_visit_FloatNum(node, expected):
    typeChecker = TypeChecker()
    assert typeChecker.visit(node) == expected

@pytest.mark.parametrize('node, expected', [
    (AST.String('ala ma kota', 3), WriterJust(Symbol(3, 'string', ())))
])
def test_visit_String(node, expected):
    typeChecker = TypeChecker()
    assert typeChecker.visit(node) == expected