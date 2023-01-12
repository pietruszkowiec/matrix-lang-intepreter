from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass
class Symbol:
    type: Optional[str]
    size: Optional[Tuple[int, ...]]
    lineno: int = 0

@dataclass
class VariableSymbol(Symbol):
    name: str = ''

class SymbolTable:
    def __init__(self, parent: Optional['SymbolTable'] = None):
        self.parent: SymbolTable = parent
        self.table = {}
        self.children = []
        self.child: SymbolTable = None

    def getCurrentScope(self) -> 'SymbolTable':
        ptr = self
        while ptr.child is not None:
            ptr = ptr.child
        return ptr

    def printScopeRecursive(self, indent: int = 0):
        print(indent * '    ', end='')
        print('{')
        for symbol in self.table.values():
            print((indent+1) * '    ', end='')
            print(symbol)

        for child in self.children:
            child.printScopeRecursive(indent+1)

        print(indent * '    ', end='')
        print('}')

    def put(self, name: str, symbol: VariableSymbol):
        ptr = self.getCurrentScope()
        ptr.table[name] = symbol

    def get(self, name: str) -> Optional[VariableSymbol]:
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
