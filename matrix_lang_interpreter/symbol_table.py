from dataclasses import dataclass
from typing import Tuple


@dataclass
class Symbol:
    type: str
    size: Tuple[int]
    lineno: int = None

@dataclass
class VariableSymbol(Symbol):
    name: str = None

class SymbolTable:
    def __init__(self, parent):
        self.parent: SymbolTable = parent
        self.table = {}
        self.children = []
        self.child: SymbolTable = None

    def getCurrentScope(self):
        ptr = self
        while ptr.child is not None:
            ptr = ptr.child
        return ptr

    def printScopeRecursive(self, indent=0):
        print(indent * '    ', end='')
        print('{')
        for symbol in self.table.values():
            print((indent+1) * '    ', end='')
            print(symbol)

        for child in self.children:
            child.printScopeRecursive(indent+1)

        print(indent * '    ', end='')
        print('}')

    def put(self, name, symbol):
        ptr = self.getCurrentScope()
        ptr.table[name] = symbol

    def get(self, name):
        ptr = self.getCurrentScope()
        symbol = ptr.table.get(name, None)
        ptr = ptr.parent

        while ptr is not None and symbol is None:
            symbol = ptr.table.get(name, None)
            ptr = ptr.parent

        return symbol

    def pushScope(self):
        ptr = self.getCurrentScope()
        ptr.child = SymbolTable(ptr)
        ptr.children.append(ptr.child)

    def popScope(self):
        ptr = self.getCurrentScope()
        if ptr.parent is not None:
            ptr.parent.child = None
