import sys
import operator
import numpy as np
from matrix_lang_interpreter import AST
from matrix_lang_interpreter.memory import *
from matrix_lang_interpreter.exceptions import  *
from matrix_lang_interpreter.dispatcher import *


sys.setrecursionlimit(10000)


class Interpreter:
    def __init__(self):
        self.memory_stack = MemoryStack(Memory())

    @on('node')
    def visit(self, node):
        pass

    @when(AST.AST)
    def visit(self, node: AST.AST):
        try:
            for stmt in node.stmt_set:
                self.visit(stmt)
        except ReturnValueException as e:
            list(map(print, e.values))

    @when(AST.Block)
    def visit(self, node: AST.Block):
        self.memory_stack.push(Memory())
        for stmt in node.stmt_set:
            self.visit(stmt)
        self.memory_stack.pop()

    @when(AST.AssignStmt)
    def visit(self, node: AST.AssignStmt):
        expr = self.visit(node.expr)
        if isinstance(node.lvalue, AST.Id):
            id = node.lvalue.id
            if self.memory_stack.has_key(id):
                self.memory_stack.set(id, expr)
            else:
                self.memory_stack.insert(id, expr)
        elif isinstance(node.lvalue, AST.Ref):
            id = node.lvalue.term.id
            vec = self.memory_stack.get(id)

            idxs = self.visit(node.lvalue.idxs)
            vec[tuple(idxs)] = expr

            self.memory_stack.set(id, vec)

    @when(AST.IfStmt)
    def visit(self, node: AST.IfStmt):
        self.memory_stack.push(Memory())
        if self.visit(node.cond):
            self.visit(node.stmt)
        self.memory_stack.pop()

    @when(AST.IfElseStmt)
    def visit(self, node: AST.IfElseStmt):
        self.memory_stack.push(Memory())
        if self.visit(node.cond):
            self.visit(node.stmt)
        else:
            self.visit(node.elseStmt)
        self.memory_stack.pop()

    @when(AST.WhileLoop)
    def visit(self, node: AST.WhileLoop):
        self.memory_stack.push(Memory())

        while self.visit(node.cond):
            try:
                self.visit(node.stmt)
            except BreakException:
                break
            except ContinueException:
                continue

        self.memory_stack.pop()

    @when(AST.ForLoop)
    def visit(self, node: AST.ForLoop):
        beg = self.visit(node.beg)
        end = self.visit(node.end)

        self.memory_stack.push(Memory())
        self.memory_stack.insert(node.id.id, beg)

        while (i := self.visit(node.id)) < end:
            try:
                self.visit(node.stmt)
                self.memory_stack.set(node.id.id, i + 1)
            except BreakException:
                break
            except ContinueException:
                self.memory_stack.set(node.id.id, i + 1)
                continue

        self.memory_stack.pop()

    @when(AST.Break)
    def visit(self, node: AST.Break):
        raise BreakException()

    @when(AST.Continue)
    def visit(self, node: AST.Continue):
        raise ContinueException()

    @when(AST.Print)
    def visit(self, node: AST.Print):
        for expr in node.expr_set:
            print(self.visit(expr))

    @when(AST.Return)
    def visit(self, node: AST.Return):
        raise ReturnValueException(list(map(self.visit, node.expr_set)))

    @when(AST.BinExpr)
    def visit(self, node: AST.BinExpr):
        isint = lambda x, y: (
            (
                isinstance(x, int) and isinstance(y, int)
            ) or (
                isinstance(x, np.ndarray) and x.dtype == int
                and
                isinstance(y, np.ndarray) and y.dtype == int
            )
        )

        operations = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': lambda x, y: (
                operator.floordiv(x, y) if isint(x, y)
                else operator.truediv(x, y))
        }
        left = self.visit(node.left)
        right = self.visit(node.right)
        return operations[node.op](left, right)

    @when(AST.MatMulBinExpr)
    def visit(self, node: AST.MatMulBinExpr):
        left = self.visit(node.left)
        right = self.visit(node.right)
        return np.matmul(left, right)

    @when(AST.UnExpr)
    def visit(self, node: AST.UnExpr):
        operations = {
            '+': lambda x: x,
            '-': operator.neg
        }
        child = self.visit(node.child)
        return operations[node.op](child)

    @when(AST.MatTransExpr)
    def visit(self, node: AST.MatTransExpr):
        child = self.visit(node.child)
        return child.T

    @when(AST.RelationExpr)
    def visit(self, node: AST.RelationExpr):
        operations = {
            '==': operator.eq,
            '!=': operator.ne,
            '<':  operator.lt,
            '<=': operator.le,
            '>':  operator.gt,
            '>=': operator.ge
        }
        left = self.visit(node.left)
        right = self.visit(node.right)
        return operations[node.op](left, right)

    @when(AST.Vector)
    def visit(self, node: AST.Vector):
        elements = list(map(self.visit, node.expr_set))

        if len(elements) == 0:
            return np.array([], dtype=int)

        if isinstance(elements[0], np.ndarray):
            return np.vstack(elements)

        return np.hstack(elements)

    @when(AST.Zeros)
    def visit(self, node: AST.Zeros):
        size = self.visit(node.size)
        return np.zeros(size)

    @when(AST.Ones)
    def visit(self, node: AST.Ones):
        size = self.visit(node.size)
        return np.ones(size)

    @when(AST.Eye)
    def visit(self, node: AST.Eye):
        n = self.visit(node.size)
        return np.eye(n, dtype=int)

    @when(AST.Ref)
    def visit(self, node: AST.Ref):
        term = self.visit(node.term)
        idxs = self.visit(node.idxs)
        return term[tuple(idxs)]

    @when(AST.Id)
    def visit(self, node: AST.Id):
        return self.memory_stack.get(node.id)

    @when(AST.IntNum)
    def visit(self, node: AST.IntNum):
        return node.n

    @when(AST.FloatNum)
    def visit(self, node: AST.FloatNum):
        return node.n

    @when(AST.String)
    def visit(self, node: AST.String):
        return node.s
