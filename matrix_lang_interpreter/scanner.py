from sly import Lexer


class Scanner(Lexer):
    tokens = {
        ADDASSIGN, SUBASSIGN, MULASSIGN, DIVASSIGN,
        LEQ, GEQ, NEQ, EQU, TRANSPOSE,
        IF, ELSE, FOR, WHILE, BREAK, CONTINUE,
        RETURN, EYE, ZEROS, ONES, PRINT,
        ID, INTNUM, FLOATNUM, STRING
    }

    literals = {
        '=', '+', '-', '*', '/', '@',
        '(', ')', '[', ']', '{', '}',
        ':', ',', ';', '<', '>'
    }

    ADDASSIGN = r'\+='
    SUBASSIGN = r'-='
    MULASSIGN = r'\*='
    DIVASSIGN = r'/='

    TRANSPOSE = r'.T'

    LEQ = r'<='
    GEQ = r'>='
    NEQ = r'!='
    EQU = r'=='

    ID = r'[a-zA-Z_]\w*'
    ID['if'] = IF
    ID['else'] = ELSE
    ID['for'] = FOR
    ID['while'] = WHILE
    ID['break'] = BREAK
    ID['continue'] = CONTINUE
    ID['return'] = RETURN
    ID['eye'] = EYE
    ID['zeros'] = ZEROS
    ID['ones'] = ONES
    ID['print'] = PRINT

    @_(r'(\d*(\.\d+)?[Ee][+-]?\d+)|(\d+\.\d*)|(\d*\.\d+)')
    def FLOATNUM(self, t):
        t.value = float(t.value)
        return t

    @_(r'\d+')
    def INTNUM(self, t):
        t.value = int(t.value)
        return t

    @_(r'(\".*?\")|(\'.*?\')')
    def STRING(self, t):
        t.value = t.value[1:-1]
        return t

    ignore = ' \t'
    ignore_comment = r'\#.*'

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += len(t.value)

    def error(self, t):
        print(f"Line {t.lineno:3}: Scanner: Bad character: {t.value[0]}")
        self.index += 1


if __name__ == "__main__":
    import sys
    import os

    try:
        filename = sys.argv[1] if len(sys.argv) > 1 else os.path.join("tests", "example_scanner.txt")
        file = open(filename, "r")
    except IOError:
        print("Cannot open {0} file".format(filename))
        sys.exit(0)

    text = file.read()
    lexer = Scanner()

    for token in lexer.tokenize(text):
        print(f"({token.lineno}): {token.type}({token.value})")
