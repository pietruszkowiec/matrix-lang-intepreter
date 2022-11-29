if __name__ == '__main__':
    import sys
    import os
    from matrix_lang_interpreter.scanner import Scanner
    from matrix_lang_interpreter.parser import Parser
    from matrix_lang_interpreter.print_tree import TreePrinter

    for i in range(1, 4):
        try:
            filename = sys.argv[1] if len(sys.argv) > 1 else os.path.join("tests", f"example_parser{i}.txt")
            file = open(filename, "r")
        except IOError:
            print("Cannot open {0} file".format(filename))
            sys.exit(0)

        text = file.read()
        scanner = Scanner()
        parser = Parser()

        print(filename)
        ast = parser.parse(scanner.tokenize(text))

        ast.printTree()