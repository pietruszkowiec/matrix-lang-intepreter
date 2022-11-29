from sly import Parser as SlyParser
from matrix_lang_interpreter import AST
from matrix_lang_interpreter.scanner import Scanner


class Parser(SlyParser):
    debugfile = 'parser.out'
    tokens = Scanner.tokens

    precedence = (
        ('left', '=', ADDASSIGN, SUBASSIGN, MULASSIGN, DIVASSIGN),
        ('nonassoc', IF, WHILE, FOR),
        ('nonassoc', ELSE),
        ('nonassoc', '<', '>', EQU, NEQ, LEQ, GEQ),
        ('left', '+', DOTADD, '-' , DOTSUB),
        ('left', '*', DOTMUL, '/', DOTDIV),
        ('right', UMINUS),
        ('left', '\''),
    )

    @_('stmt_set')
    def program(self, p):
        return AST.AST(p.stmt_set)

    @_('stmt ";"',
       'stmt \n',
       'block ";"',
       'block \n')
    def stmt_set(self, p):
       return [p[0]]

    @_('expr')
    def stmt(self, p):
        return p.expr

    @_('stmt_set stmt ";"',
       'stmt_set stmt \n',
       'stmt_set block ";"',
       'stmt_set block \n')
    def stmt_set(self, p):
        myset = p.stmt_set
        myset.append(p[1])
        return myset

    @_('IF "(" expr ")" block ELSE block')
    def stmt(self, p):
        return AST.IfElseStmt(p.expr, p.block0, p.block1)

    @_('IF "(" expr ")" block')
    def stmt(self, p):
        return AST.IfStmt(p.expr, p.block)

    @_('WHILE "(" expr ")" block')
    def stmt(self, p):
        return AST.WhileLoop(p.expr, p.block)

    @_('FOR ID "=" expr ":" expr block')
    def stmt(self, p):
        return AST.ForLoop(AST.Id(p.ID), p.expr0, p.expr1, p.block)

    @_('expr "=" expr')
    def stmt(self, p):
        return AST.AssignStmt(p.expr0, p.expr1)

    @_('ID ADDASSIGN expr',
       'ID SUBASSIGN expr',
       'ID MULASSIGN expr',
       'ID DIVASSIGN expr')
    def stmt(self, p):
        return AST.AssignStmt(AST.Id(p.ID), AST.BinExpr(p[1][0], AST.Id(p.ID), p.expr))

    @_('BREAK',
       'CONTINUE')
    def stmt(self, p):
        return AST.LoopKeyword(p[0])

    @_('PRINT innerlist')
    def stmt(self, p):
        return AST.Print(p.innerlist.expr_set)

    @_('RETURN innerlist')
    def stmt(self, p):
        return AST.Return(p.innerlist.expr_set)

    @_('"{" stmt_set "}"')
    def block(self, p):
        return AST.Block(p.stmt_set)

    @_('stmt \n',
       'stmt ";"')
    def block(self, p):
        return AST.Block([p.stmt])

    @_('expr "+" expr',
       'expr "-" expr',
       'expr "*" expr',
       'expr "/" expr',
       'expr DOTADD expr',
       'expr DOTSUB expr',
       'expr DOTMUL expr',
       'expr DOTDIV expr')
    def expr(self, p):
        return AST.BinExpr(p[1], p.expr0, p.expr1)

    @_('"-" expr %prec UMINUS')
    def expr(self, p):
        return AST.UnExpr(p[0], p.expr)

    @_('expr "\'"')
    def expr(self, p):
        return AST.UnExpr(p[1], p.expr)

    @_('"(" expr ")"')
    def expr(self, p):
        return p.expr

    @_('expr "<" expr',
       'expr ">" expr',
       'expr LEQ expr',
       'expr GEQ expr',
       'expr EQU expr',
       'expr NEQ expr')
    def expr(self, p):
        return AST.RelationExpr(p[1], p.expr0, p.expr1)

    @_('term')
    def expr(self, p):
        return p.term

    @_('"[" outerlist "]"')
    def expr(self, p):
        return p.outerlist

    @_('outerlist "," "[" innerlist "]"')
    def outerlist(self, p):
        return p.outerlist + AST.Matrix([p.innerlist])

    @_('"[" innerlist "]"')
    def outerlist(self, p):
        return AST.Matrix([p.innerlist])

    @_('innerlist "," expr')
    def innerlist(self, p):
        return p.innerlist + AST.Vector([p.expr])

    @_('expr')
    def innerlist(self, p):
        return AST.Vector([p.expr])

    @_('expr "[" expr "," expr "]"')
    def expr(self, p):
        return AST.Ref(p.expr0, p.expr1, p.expr2)

    @_('ZEROS "(" expr ")"',
       'ONES "(" expr ")"',
       'EYE "(" expr ")"')
    def term(self, p):
        return AST.SpecialMatrix(p[0], p.expr)

    @_('INTNUM')
    def term(self, p):
        return AST.IntNum(p.INTNUM)

    @_('FLOATNUM')
    def term(self, p):
        return AST.FloatNum(p.FLOATNUM)

    @_('STRING')
    def term(self, p):
        return AST.String(p.STRING)

    @_('ID')
    def term(self, p):
        return AST.Id(p.ID)
