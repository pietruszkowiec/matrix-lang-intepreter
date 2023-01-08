if __name__ == '__main__':
    import sys
    import os
    from matrix_lang_interpreter.scanner import Scanner
    from matrix_lang_interpreter.parser import Parser
    from matrix_lang_interpreter.print_tree import TreePrinter
    from matrix_lang_interpreter.type_checker import TypeChecker

if __name__ == '__main__':
    if len(sys.argv) > 1:
        argv = sys.argv[1:]
    else:
        argv = [
            "tests/example_type_checker1.txt", 
            "tests/example_type_checker2.txt", 
            "tests/example_type_checker3.txt"
        ]
    for filename in argv:
        try:
            file = open(filename, "r")
        except IOError:
            print("Cannot open {0} file".format(filename))
            continue
        
        text = file.read()
        ast = Parser().parse(Scanner().tokenize(text))

        print(filename)

        typeChecker = TypeChecker(debug=False)
        typeCheckingRes = typeChecker.visit(ast)
        print(typeCheckingRes.log)
        print(typeCheckingRes)
        print()
