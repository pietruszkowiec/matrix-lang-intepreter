from dataclasses import dataclass, field
from typing import List


class Node:
    pass

@dataclass
class AST(Node):
    stmt_set: List['Stmt']

@dataclass
class Block(Node):
    stmt_set: List['Stmt']

class Stmt(Node):
    pass

@dataclass
class AssignStmt(Stmt):
    id: 'Term'
    expr: 'Expr'

@dataclass
class IfStmt(Stmt):
    condition: 'Expr'
    stmt: Stmt

@dataclass
class IfElseStmt(IfStmt):
    elseStmt: Stmt

@dataclass
class WhileLoop(Stmt):
    condition: 'Expr'
    stmt: Stmt

@dataclass
class ForLoop(Stmt):
    id: 'Id'
    beg: 'Expr'
    end: 'Expr'
    stmt: Stmt

@dataclass
class Break(Stmt):
    pass

@dataclass
class Continue(Stmt):
    pass

@dataclass
class Print:
    expr_set: List['Expr']

@dataclass
class Return:
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
    vector: Expr
    idxs: Expr

@dataclass
class Term(Expr):
    pass

@dataclass
class Id(Term):
    id: str

class Num(Term):
    pass

@dataclass
class IntNum(Num):
    n: int

@dataclass
class FloatNum(Num):
    n: float

@dataclass
class String(Term):
    s: str
