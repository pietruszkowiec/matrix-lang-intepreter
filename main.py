if __name__ == "__main__":
    import sys
    import os
    from matrix_lang_interpreter.scanner import Scanner
    from matrix_lang_interpreter.parser import Parser

    try:
        filename = sys.argv[1] if len(sys.argv) > 1 else os.path.join("tests", "simple_example.txt")
        file = open(filename, "r")
    except IOError:
        print("Cannot open {0} file".format(filename))
        sys.exit(0)

    text = file.read()
    lexer = Scanner()
    parser = Parser()
    
    parser.parse(lexer.tokenize(text))
