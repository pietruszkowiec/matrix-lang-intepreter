from sly import Parser as SlyParser
from matrix_lang_interpreter import AST
from matrix_lang_interpreter.scanner import Scanner


class Parser(SlyParser):
    debugfile = 'parser.out'
    tokens = Scanner.tokens

    precedence = (
        ('nonassoc', IFX),
        ('nonassoc', ELSE),
        ('right', '=', ADDASSIGN, SUBASSIGN, MULASSIGN, DIVASSIGN),
        ('nonassoc', EQU, NEQ),
        ('nonassoc', '<', '>', LEQ, GEQ),
        ('left', '+', DOTADD, '-' , DOTSUB),
        ('left', '*', DOTMUL, '/', DOTDIV),
        ('right', UPLUS, UMINUS),
        ('left', '\''),
    )

    @_('stmt_set')
    def program(self, p):
        return AST.AST(p.stmt_set)

    @_('stmt')
    def stmt_set(self, p):
       return [p.stmt]

    @_('stmt_set stmt')
    def stmt_set(self, p):
        myset = p.stmt_set
        myset.append(p.stmt)
        return myset

    @_('"{" stmt_set "}"')
    def stmt(self, p):
        return AST.Block(p.stmt_set)

    @_('IF "(" expr ")" stmt ELSE stmt')
    def stmt(self, p):
        return AST.IfElseStmt(p.expr, p.stmt0, p.stmt1)

    @_('IF "(" expr ")" stmt %prec IFX')
    def stmt(self, p):
        return AST.IfStmt(p.expr, p.stmt)

    @_('WHILE "(" expr ")" stmt')
    def stmt(self, p):
        return AST.WhileLoop(p.expr, p.stmt)

    @_('FOR term "=" expr ":" expr stmt')
    def stmt(self, p):
        return AST.ForLoop(p.term, p.expr0, p.expr1, p.stmt)

    @_('term "=" expr ";"')
    def stmt(self, p):
        return AST.AssignStmt(p.term, p.expr)

    @_('term ADDASSIGN expr ";"',
       'term SUBASSIGN expr ";"',
       'term MULASSIGN expr ";"',
       'term DIVASSIGN expr ";"')
    def stmt(self, p):
        return AST.AssignStmt(p.term, AST.BinExpr(p[1][0], p.term, p.expr))

    @_('BREAK ";"')
    def stmt(self, p):
        return AST.Break(p.lineno, p.index)

    @_('CONTINUE ";"')
    def stmt(self, p):
        return AST.Continue(p.lineno,p.index)

    @_('PRINT vector ";"')
    def stmt(self, p):
        return AST.Print(p.vector.expr_set)

    @_('RETURN vector ";"')
    def stmt(self, p):
        return AST.Return(p.vector.expr_set)

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

    @_('"+" expr %prec UPLUS',
       '"-" expr %prec UMINUS')
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

    @_('"[" vector "]"')
    def expr(self, p):
        return p.vector

    @_('vector "," expr')
    def vector(self, p):
        return p.vector.append(p.expr)

    @_('expr')
    def vector(self, p):
        return AST.Vector([p.expr])

    @_('')
    def vector(self, p):
        return AST.Vector([])

    @_('term "[" vector "]"')
    def term(self, p):
        return AST.Ref(p.term, p.vector)

    @_('ZEROS "(" vector ")"')
    def term(self, p):
        return AST.Zeros(p.vector)

    @_('ONES "(" vector ")"')
    def term(self, p):
        return AST.Ones(p.vector)

    @_('EYE "(" expr ")"')
    def term(self, p):
        return AST.Eye(p.expr)

    @_('INTNUM')
    def term(self, p):
        return AST.IntNum(p.INTNUM, p.lineno, p.index)

    @_('FLOATNUM')
    def term(self, p):
        return AST.FloatNum(p.FLOATNUM, p.lineno, p.index)

    @_('STRING')
    def term(self, p):
        return AST.String(p.STRING, p.lineno, p.index)

    @_('ID')
    def term(self, p):
        return AST.Id(p.ID, p.lineno, p.index)
