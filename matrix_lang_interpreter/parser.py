from sly import Parser as SlyParser
from matrix_lang_interpreter.scanner import Scanner


class BinExpr:
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right
    
    def __eq__(self, other):
        return self.op == other.op \
            and self.left == other.left \
            and self.right == other.right

class UnExpr:
    def __init__(self, op, child):
        self.op = op
        self.child = child
    
    def __eq__(self, other):
        return self.op == other.op and self.child == other.child

class Parser(SlyParser):
    tokens = Scanner.tokens

    precedence = (
        ('left', '+', DOTADD, '-' , DOTSUB),
        ('left', '*', DOTMUL, '/', DOTDIV),
        ('right', UMINUS)
    )

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
        return (p.expr)

    @_('term')
    def expr(self, p):
        return p.term

    @_('"[" outerlist "]"')
    def term(self, p):
        return p.outerlist

    @_('outerlist "," "[" innerlist "]"')
    def outerlist(self, p):
        return p.outerlist + [p.innerlist]

    @_('"[" innerlist "]"')
    def outerlist(self, p):
        return [p.innerlist]

    @_('innerlist "," expr')
    def innerlist(self, p):
        return p.innerlist + [p.expr]

    @_('expr')
    def innerlist(self, p):
        return [p.expr]

    @_('ZEROS "(" INTNUM ")"')
    def term(self, p):
        return [[0 for _ in range(p.INTNUM)] for _ in range(p.INTNUM)]

    @_('ONES "(" INTNUM ")"')
    def term(self, p):
        return [[1 for _ in range(p.INTNUM)] for _ in range(p.INTNUM)]

    @_('EYE "(" INTNUM ")"')
    def term(self, p):
        return [[1 if i == j else 0
                 for j in range(p.INTNUM)]
                for i in range(p.INTNUM)]

    @_('FLOATNUM')
    def term(self, p):
        return p.FLOATNUM

    @_('INTNUM')
    def term(self, p):
        return p.INTNUM
