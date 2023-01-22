import sys
from matrix_lang_interpreter.scanner import Scanner
from matrix_lang_interpreter.parser import Parser
from matrix_lang_interpreter.print_tree import TreePrinter
from matrix_lang_interpreter.type_checker import TypeChecker
from matrix_lang_interpreter.interpreter import Interpreter


if __name__ == '__main__':
    if len(sys.argv) > 1:
        argv = sys.argv[1:]
    else:
        argv = [
            "examples/interpreter/fibonacci.m",
            "examples/interpreter/matrix.m",
            "examples/interpreter/pi.m",
            "examples/interpreter/primes.m",
            "examples/interpreter/sqrt.m",
            "examples/interpreter/triangle.m",
            "examples/interpreter/matrix_multiply.m",
        ]
    for filename in argv:
        try:
            file = open(filename, "r")
        except IOError:
            print("Cannot open {0} file".format(filename))
            continue

        print(filename)

        text = file.read()
        tokens = Scanner().tokenize(text)
        ast = Parser().parse(tokens)


        typeChecker = TypeChecker(debug=False)
        if (res := typeChecker.visit(ast)).is_nothing():
            print(res.log)
            continue

        interpreter = Interpreter()
        interpreter.visit(ast)
