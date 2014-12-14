
import sys
import ply.yacc as yacc
# from Cparser.TreePrinter import TreePrinter
from Cparser.Cparser import Cparser
from Cparser.TypeChecker import TypeChecker
from Cparser.Interpreter import Interpreter


if __name__ == '__main__':

    try:
        filename = sys.argv[1] if len(sys.argv) > 1 else "example.txt"
        sourcefile = open(filename, "r")
    except IOError:
        print("Cannot open {0} file".format(filename))
        sys.exit(0)

    c_parser = Cparser()
    parser = yacc.yacc(module=c_parser)
    text = sourcefile.read()
    result = parser.parse(text, lexer=c_parser.scanner)

    typeChecker = TypeChecker()
    typeChecker.visit(result)   # or alternatively ast.accept(typeChecker)

    result.accept(Interpreter())


