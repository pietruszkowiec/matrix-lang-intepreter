from dataclasses import dataclass, field
from typing import List

@dataclass
class Node:
    pass

@dataclass
class AST(Node):
    stmt_set: List['Stmt']

@dataclass
class Block(Node):
    stmt_set: List['Stmt']

@dataclass
class Stmt(Node):
    pass

@dataclass
class AssignStmt(Stmt):
    term: 'Term'
    expr: 'Expr'

@dataclass
class IfStmt(Stmt):
    cond: 'Expr'
    stmt: Stmt

@dataclass
class IfElseStmt(IfStmt):
    elseStmt: Stmt

@dataclass
class WhileLoop(Stmt):
    cond: 'Expr'
    stmt: Stmt

@dataclass
class ForLoop(Stmt):
    term: 'Term'
    beg: 'Expr'
    end: 'Expr'
    stmt: Stmt

@dataclass
class Break(Stmt):
    lineno: int = None
    index: int = None

@dataclass
class Continue(Stmt):
    lineno: int = None
    index: int = None

@dataclass
class Print(Stmt):
    expr_set: List['Expr']

@dataclass
class Return(Stmt):
    expr_set: List['Expr']

@dataclass
class Expr(Node):
    pass

@dataclass
class BinExpr(Expr):
    op: str
    left: Expr
    right: Expr

@dataclass
class UnExpr(Expr):
    op: str
    child: Expr

@dataclass
class RelationExpr(Expr):
    op: str
    left: Expr
    right: Expr

@dataclass
class Vector(Expr):
    expr_set: List[Expr] = field(default_factory=list)

    def append(self, element):
        self.expr_set.append(element)
        return self

@dataclass
class SpecialMatrix(Expr):
    size: Expr

@dataclass
class Zeros(SpecialMatrix):
    pass

@dataclass
class Ones(SpecialMatrix):
    pass

@dataclass
class Eye(SpecialMatrix):
    pass

@dataclass
class Ref(Expr):
    term: 'Term'
    idxs: Vector

@dataclass
class Term(Expr):
    pass

@dataclass
class Id(Term):
    id: str
    lineno: int = None
    index: int = None

class Num(Term):
    pass

@dataclass
class IntNum(Num):
    n: int
    lineno: int = None
    index: int = None

@dataclass
class FloatNum(Num):
    n: float
    lineno: int = None
    index: int = None

@dataclass
class String(Term):
    s: str
    lineno: int = None
    index: int = None
