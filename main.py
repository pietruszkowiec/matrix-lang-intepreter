if __name__ == '__main__':
    import sys
    import os
    from matrix_lang_interpreter.scanner import Scanner
    from matrix_lang_interpreter.parser import Parser
    from matrix_lang_interpreter.print_tree import TreePrinter
    from matrix_lang_interpreter.type_checker import TypeChecker

    text = '''b = 3 < 3;
            c = -+-2;
            while (b == 3) {
                if (c == 0) {
                    c = 5 > b;
                } else {
                    c = 2 + 3;
                }
            }
            for x = (c+3.0):5 {
                continue;
                b = x;
            }
            break;
            x = [[1,2,3], [[1,2],[3,4]]];
            y = [] + [1,2,3];
            b = 'ola' + ['ala'];
            x = ones(2, 2) + [[1],[2]];
            y = ones(3, 2, 1) + zeros(1, 2, 3);
            z = eye(2) + [[1,2]];
            x = [[1,2,3], [0,1,2]];
            v = x[2];
            v = x[1][3];
            v = x[1] + [1.0, 2.0, 1.0];
            x[1, 1] = 1.0;
            c = 'ala';
            # x[1] = 1;
            x[1] = [12, 1];
            u = zeros(3,5);
            z = u[7,10];
            v = u[2,3,4];
    '''

    ast = Parser().parse(Scanner().tokenize(text))
    ast.printTree()

    typeChecker = TypeChecker(debug=False)
    typeCheckingRes = typeChecker.visit(ast)
    print(typeCheckingRes)
    print(typeCheckingRes.log)


    # for i in range(1, 4):
    #     try:
    #         filename = sys.argv[1] if len(sys.argv) > 1 else os.path.join("tests", f"example_parser{i}.txt")
    #         file = open(filename, "r")
    #     except IOError:
    #         print("Cannot open {0} file".format(filename))
    #         sys.exit(0)

    #     text = file.read()
    #     scanner = Scanner()
    #     parser = Parser()

    #     print(filename)
    #     ast = parser.parse(scanner.tokenize(text))

    #     ast.printTree()