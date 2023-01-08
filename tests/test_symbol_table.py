import pytest
from matrix_lang_interpreter.symbol_table import *


def test_getCurrentScope():
    symbolTable = SymbolTable(None)
    assert symbolTable.getCurrentScope() == symbolTable

    symbolTable.child = SymbolTable(symbolTable)
    assert symbolTable.getCurrentScope() == symbolTable.child

    symbolTable.child.child = SymbolTable(symbolTable)
    assert symbolTable.getCurrentScope() == symbolTable.child.child

def test_pushScope():
    symbolTable = SymbolTable(None)
    symbolTable.pushScope()
    assert symbolTable.getCurrentScope().parent == symbolTable
    assert symbolTable.child == symbolTable.getCurrentScope()

    symbolTable.pushScope()
    assert symbolTable.getCurrentScope().parent.parent == symbolTable
    assert symbolTable.child.child == symbolTable.getCurrentScope()

def test_popScope():
    symbolTable = SymbolTable(None)
    symbolTable.popScope()
    assert symbolTable.getCurrentScope() == symbolTable

    symbolTable.pushScope()
    symbolTable.pushScope()
    symbolTable.popScope()
    assert symbolTable.getCurrentScope().parent == symbolTable
    assert symbolTable.child == symbolTable.getCurrentScope()

def test_put():
    symbolTable = SymbolTable(None)
    symbol = Symbol(4, 'int', (1,))

    symbolTable.put('x', symbol)
    assert symbolTable.table['x'] == symbol

def test_get():
    symbolTable = SymbolTable(None)
    symbol = Symbol(4, 'int', (1,))
    symbolTable.put('x', symbol)
    assert symbolTable.get('x') == symbol

    symbolTable.pushScope()
    assert symbolTable.get('x') == symbol

    symbol = Symbol(5, 'float', (2,))
    symbolTable.put('y', symbol)
    assert symbolTable.get('y') == symbol

    symbolTable.pushScope()
    assert symbolTable.get('y') == symbol

    symbolTable.popScope()
    assert symbolTable.get('y') == symbol

    symbolTable.popScope()
    assert symbolTable.get('y') == None
