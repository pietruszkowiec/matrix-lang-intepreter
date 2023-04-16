import os
import glob
import argparse
from matrix_lang_interpreter.scanner import Scanner
from matrix_lang_interpreter.parser import Parser
from matrix_lang_interpreter.print_tree import TreePrinter
from matrix_lang_interpreter.type_checker import TypeChecker
from matrix_lang_interpreter.interpreter import Interpreter


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        prog="python3 main.py",
        description="Interpreter of your newest favorite language."
    )
    argparser.add_argument(
        "filename", help="source code filename", nargs="*",
        default=glob.glob(os.path.join("examples", "*.m"))
    )
    argparser.add_argument(
        "-s", "--show", dest="show", action="store_true", 
        help="show AST tree"
    )
    args = argparser.parse_args()

    for filename in args.filename:
        try:
            file = open(filename, "r")
        except IOError:
            print("Cannot open {0} file".format(filename))
            continue

        print(filename)

        text = file.read()
        tokens = Scanner().tokenize(text)
        ast = Parser().parse(tokens)

        if args.show:
            ast.printTree()

        typeChecker = TypeChecker(debug=False)
        if (res := typeChecker.visit(ast)).is_nothing():
            print(res.log)
            continue

        interpreter = Interpreter()
        interpreter.visit(ast)
