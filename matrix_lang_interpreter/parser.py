from sly import Parser as SlyParser
from matrix_lang_interpreter.scanner import Scanner


class Parser(SlyParser):
    tokens = Scanner.tokens

    precedence = (
        ('left', '+', DOTADD, '-' , DOTSUB),
        ('left', '*',  DOTMUL, '/', DOTDIV),
        ('right', UMINUS)
    )

    @_('expr "+" expr')
    def expr(self, p):
        return p.expr0 + p.expr1

    @_('expr "-" expr')
    def expr(self, p):
        return p.expr0 - p.expr1

    @_('expr "*" expr')
    def expr(self, p):
        return p.expr0 * p.expr1

    @_('expr "/" expr')
    def expr(self, p):
        return p.expr0 / p.expr1

    @_('"-" expr %prec UMINUS')
    def expr(self, p):
        return -p.expr

    @_('expr DOTADD expr')
    def expr(self, p):
        n = len(p.expr0)
        m = len(p.expr0[0])
        temp = [[0 for _ in range(m)] for _ in range(n)]
        for i in range(n):
            for j in range(m):
                temp[i][j] = p.expr0[i][j] + p.expr1[i][j]
        return temp

    @_('expr DOTSUB expr')
    def expr(self, p):
        n = len(p.expr0)
        m = len(p.expr0[0])
        temp = [[0 for _ in range(m)] for _ in range(n)]
        for i in range(n):
            for j in range(m):
                temp[i][j] = p.expr0[i][j] - p.expr1[i][j]
        return temp

    @_('expr DOTMUL expr')
    def expr(self, p):
        n = len(p.expr0)
        m = len(p.expr0[0])
        temp = [[0 for _ in range(m)] for _ in range(n)]
        for i in range(n):
            for j in range(m):
                temp[i][j] = p.expr0[i][j] * p.expr1[i][j]
        return temp

    @_('expr DOTDIV expr')
    def expr(self, p):
        n = len(p.expr0)
        m = len(p.expr0[0])
        temp = [[0 for _ in range(m)] for _ in range(n)]
        for i in range(n):
            for j in range(m):
                temp[i][j] = p.expr0[i][j] / p.expr1[i][j]
        return temp

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
