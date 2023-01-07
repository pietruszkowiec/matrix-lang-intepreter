from matrix_lang_interpreter import AST
from matrix_lang_interpreter.add_to_class import addToClass


class TreePrinter:
    @staticmethod
    def printIndent(indent):
        print(' | ' * indent, end='')

    @addToClass(AST.AST)
    def printTree(self, indent=0):
        for stmt in self.stmt_set:
            stmt.printTree(indent)

    @addToClass(AST.Block)
    def printTree(self, indent):
        for stmt in self.stmt_set:
            stmt.printTree(indent)

    @addToClass(AST.AssignStmt)
    def printTree(self, indent):
        TreePrinter.printIndent(indent)
        print('=')
        self.lvalue.printTree(indent+1)
        self.expr.printTree(indent+1)

    @addToClass(AST.IfStmt)
    def printTree(self, indent):
        TreePrinter.printIndent(indent)
        print('IF')
        self.cond.printTree(indent+1)

        TreePrinter.printIndent(indent)
        print('THEN')
        self.stmt.printTree(indent+1)

    @addToClass(AST.IfElseStmt)
    def printTree(self, indent):
        TreePrinter.printIndent(indent)
        print('IF')
        self.cond.printTree(indent+1)

        TreePrinter.printIndent(indent)
        print('THEN')
        self.stmt.printTree(indent+1)

        TreePrinter.printIndent(indent)
        print('ELSE')
        self.elseStmt.printTree(indent+1)

    @addToClass(AST.WhileLoop)
    def printTree(self, indent):
        TreePrinter.printIndent(indent)
        print('WHILE')
        self.cond.printTree(indent+1)

        self.stmt.printTree(indent+1)

    @addToClass(AST.ForLoop)
    def printTree(self, indent):
        TreePrinter.printIndent(indent)
        print('FOR')
        self.id.printTree(indent+1)

        TreePrinter.printIndent(indent+1)
        print('RANGE')

        self.beg.printTree(indent+2)
        self.end.printTree(indent+2)

        self.stmt.printTree(indent+1)

    @addToClass(AST.Break)
    def printTree(self, indent):
        TreePrinter.printIndent(indent)
        print('BREAK')

    @addToClass(AST.Continue)
    def printTree(self, indent):
        TreePrinter.printIndent(indent)
        print('CONTINUE')

    @addToClass(AST.Print)
    def printTree(self, indent):
        TreePrinter.printIndent(indent)
        print('PRINT')

        for expr in self.expr_set:
            expr.printTree(indent+1)

    @addToClass(AST.Return)
    def printTree(self, indent):
        TreePrinter.printIndent(indent)
        print('RETURN')

        for expr in self.expr_set:
            expr.printTree(indent+1)

    @addToClass(AST.BinExpr)
    def printTree(self, indent):
        TreePrinter.printIndent(indent)
        print(self.op)

        self.left.printTree(indent+1)
        self.right.printTree(indent+1)

    @addToClass(AST.UnExpr)
    def printTree(self, indent):
        TreePrinter.printIndent(indent)
        print(self.op)

        self.child.printTree(indent+1)

    @addToClass(AST.RelationExpr)
    def printTree(self, indent):
        TreePrinter.printIndent(indent)
        print(self.op)

        self.left.printTree(indent+1)
        self.right.printTree(indent+1)

    @addToClass(AST.Vector)
    def printTree(self, indent):
        TreePrinter.printIndent(indent)
        print('VECTOR')

        for expr in self.expr_set:
            expr.printTree(indent+1)

    @addToClass(AST.SpecialMatrix)
    def printTree(self, indent):
        TreePrinter.printIndent(indent)
        print(self.__class__.__name__.upper())

        self.size.printTree(indent+1)

    @addToClass(AST.Ref)
    def printTree(self, indent):
        TreePrinter.printIndent(indent)
        print('REF')

        self.term.printTree(indent+1)
        self.idxs.printTree(indent+1)

    @addToClass(AST.Id)
    def printTree(self, indent):
        TreePrinter.printIndent(indent)
        print(self.id)

    @addToClass(AST.IntNum)
    def printTree(self, indent):
        TreePrinter.printIndent(indent)
        print(self.n)

    @addToClass(AST.FloatNum)
    def printTree(self, indent):
        TreePrinter.printIndent(indent)
        print(self.n)

    @addToClass(AST.String)
    def printTree(self, indent):
        TreePrinter.printIndent(indent)
        print(self.s)
