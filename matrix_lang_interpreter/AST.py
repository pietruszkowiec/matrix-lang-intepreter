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
    id: str
    expr: 'Expr'

@dataclass
class IfStmt(Stmt):
    condition: 'Expr'
    block: Block

@dataclass
class IfElseStmt(Stmt):
    condition: 'Expr'
    block: Block
    elseBlock: Block

@dataclass
class WhileLoop(Stmt):
    condition: 'Expr'
    block: Block

@dataclass
class ForLoop(Stmt):
    id: 'Id'
    beg: 'Expr'
    end: 'Expr'
    block: Block

@dataclass
class LoopKeyword(Stmt):
    keyword: str

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
    type: str
    left: Expr
    right: Expr

@dataclass
class Vector(Expr):
    expr_set: List[Expr] = field(default_factory=list)

    def __add__(self, other):
        self.expr_set += other.expr_set
        return self

@dataclass
class Matrix(Expr):
    vectors: List[Vector] = field(default_factory=list)

    def __add__(self, other):
        self.vectors += other.vectors
        return self

@dataclass
class SpecialMatrix(Expr):
    type: str
    size: Expr

@dataclass
class Ref(Expr):
    matrix: Expr
    i: Expr
    j: Expr

@dataclass
class Term(Expr):
    pass

@dataclass
class Id(Term):
    id: str

@dataclass
class IntNum(Term):
    n: int

@dataclass
class FloatNum(Term):
    n: float

@dataclass
class String(Term):
    s: str
