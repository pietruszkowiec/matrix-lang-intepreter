from sly import Parser as SlyParser
from matrix_lang_interpreter import *
from matrix_lang_interpreter.scanner import Scanner


class Parser(SlyParser):
    debugfile = 'parser.out'
    tokens = Scanner.tokens

    precedence = (
        ('left', '=', ADDASSIGN, SUBASSIGN, MULASSIGN, DIVASSIGN),
        ('left', '+', DOTADD, '-' , DOTSUB),
        ('left', '*', DOTMUL, '/', DOTDIV),
        ('right', UMINUS)
    )

    @_('expr_set expr ";"',
       'expr_set expr \n',)
    def expr_set(self, p):
        myset = p.expr_set
        myset.append(p.expr)
        return myset

    @_('expr ";"',
       'expr \n')
    def expr_set(self, p):
        return [p.expr]

    @_('ID "=" expr')
    def expr(self, p):
        return AssignExpr(Id(p.ID), p.expr)

    @_('ID ADDASSIGN expr',
       'ID SUBASSIGN expr',
       'ID MULASSIGN expr',
       'ID DIVASSIGN expr')
    def expr(self, p):
        return AssignExpr(Id(p.ID), BinExpr(p[1][0], Id(p.ID), p.expr))

    @_('expr "+" expr',
       'expr "-" expr',
       'expr "*" expr',
       'expr "/" expr',
       'expr DOTADD expr',
       'expr DOTSUB expr',
       'expr DOTMUL expr',
       'expr DOTDIV expr')
    def expr(self, p):
        return BinExpr(p[1], p.expr0, p.expr1)

    @_('"-" expr %prec UMINUS')
    def expr(self, p):
        return UnExpr(p[0], p.expr)

    @_('"(" expr ")"')
    def expr(self, p):
        return p.expr

    @_('ID')
    def expr(self, p):
        return Id(p.ID)

    @_('term')
    def expr(self, p):
        return p.term

    @_('"[" outerlist "]"')
    def term(self, p):
        return p.outerlist

    @_('outerlist "," "[" innerlist "]"')
    def outerlist(self, p):
        return p.outerlist.append(p.innerlist)

    @_('"[" innerlist "]"')
    def outerlist(self, p):
        return Matrix().append(p.innerlist)

    @_('innerlist "," expr')
    def innerlist(self, p):
        return p.innerlist + [p.expr]

    @_('expr')
    def innerlist(self, p):
        return [p.expr]

    @_('ZEROS "(" expr ")"')
    def term(self, p):
        return Zeros(p.expr)

    @_('ONES "(" expr ")"')
    def term(self, p):
        return Ones(p.expr)

    @_('EYE "(" expr ")"')
    def term(self, p):
        return Eye(p.expr)

    @_('FLOATNUM')
    def term(self, p):
        return p.FLOATNUM

    @_('INTNUM')
    def term(self, p):
        return p.INTNUM
