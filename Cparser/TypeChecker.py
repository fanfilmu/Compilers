#!/usr/bin/python
import AST
import SymbolTable
from collections import defaultdict
from random import Random

ttype = defaultdict(lambda: defaultdict(lambda: defaultdict(None)))
ttype['+']['int']['int'] = 'int'
ttype['-']['int']['int'] = 'int'
ttype['*']['int']['int'] = 'int'
ttype['/']['int']['int'] = 'int'
ttype['%']['int']['int'] = 'int'
ttype['|']['int']['int'] = 'int'
ttype['&']['int']['int'] = 'int'
ttype['^']['int']['int'] = 'int'
ttype['SHL']['int']['int'] = 'int'
ttype['SHR']['int']['int'] = 'int'

ttype['+']['int']['float'] = 'float'
ttype['+']['float']['int'] = 'float'
ttype['-']['int']['float'] = 'float'
ttype['-']['float']['int'] = 'float'
ttype['*']['int']['float'] = 'float'
ttype['*']['float']['int'] = 'float'
ttype['/']['int']['float'] = 'float'
ttype['/']['float']['int'] = 'float'

ttype['+']['float']['float'] = 'float'
ttype['-']['float']['float'] = 'float'
ttype['*']['float']['float'] = 'float'
ttype['/']['float']['float'] = 'float'

ttype['+']['string']['string'] = 'string'

ttype['*']['string']['int'] = 'string'

ttype['=']['float']['int'] = 'float'
ttype['=']['float']['float'] = 'float'
ttype['=']['int']['int'] = 'int'
ttype['=']['string']['string'] = 'string'

for y in ('<', '>', '<=', '>=', '==', '!=', '&&', '||'):
    for x in ('float', 'int'):
        for z in ('float', 'int'):
            ttype[y][x][z] = 'int'
    ttype[y]['string']['string'] = 'int'


class NodeVisitor(object):
    def visit(self, node, symbols):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node, symbols)


    def generic_visit(self, node, symbols):  # Called if no explicit visitor function exists for a node.
        return True
        # if isinstance(node, list):
        # for elem in node:
        #         self.visit(elem,symbols)
        # else:
        #     for child in node.children:
        #         if isinstance(child, list):
        #             for item in child:
        #                 if isinstance(item, AST.Node):
        #                     self.visit(item,symbols)
        #         elif isinstance(child, AST.Node):
        #             self.visit(child,symbols)

        # simpler version of generic_visit, not so general
        # def generic_visit(self, node):
        #    for child in node.children:
        #        self.visit(child)


class TypeChecker(NodeVisitor):
    def visit_Program(self, node, symbols):
        symbolscope = SymbolTable.SymbolTable(None, 'program')
        self.visit(node.declarations, symbolscope)
        self.visit(node.fundefs, symbolscope)
        self.visit(node.instructions, symbolscope)

    def visit_BinExpr(self, node, symbols):
        # alternative usage,
        # requires definition of accept method in class Node
        type1 = self.visit(node.left, symbols)  # type1 = node.left.accept(self)
        type2 = self.visit(node.right, symbols)  # type2 = node.right.accept(self)
        op = node.op
        try:
            return ttype[op][type1][type2]
        except KeyError:
            error_str = "Semantic error at line {0} - wrong binary expression"
            print(error_str.format(node.lineno))
            return None

    def visit_RelExpr(self, node, symbols):
        type1 = self.visit(node.left, symbols)  # type1 = node.left.accept(self)
        type2 = self.visit(node.right, symbols)  # type2 = node.right.accept(self)
        op = node.op
        try:
            return ttype[op][type1][type2]
        except KeyError:
            error_str = "Semantic error at line {0} - wrong relational expression"
            print(error_str.format(node.lineno))
            return None

    def visit_DeclarationList(self, node, symbols):
        for declaration in node.elements:
            self.visit(declaration, symbols)

    def visit_Declaration(self, node, symbols):
        for init in node.initList.elements:
            self.visit(init, symbols)

    def visit_Init(self, node, symbols):
        if node.left in symbols.symbols.keys():
            error_str = "Semantic error at line {0} - already defined {1}"
            print(error_str.format(node.lineno,node.left))
        else:
            symbol = SymbolTable.Symbol(node.left, node.type)
            symbols.put(node.left, symbol)

        try:
            ttype['='][node.type][self.visit(node.right, symbols)]
        except KeyError:
            error_str = "Semantic error at line {0} - invalid initialization"
            print(error_str.format(node.lineno))
            return None


    def visit_FunList(self, node, symbols):
        for fun in node.elements:
            self.visit(fun, symbols)

    def visit_Function(self, node, symbols):
        argList = []
        funSymbols = SymbolTable.SymbolTable(symbols, "function_"+node.retType)
        for arg in node.arglist.elements:
            a = self.visit(arg, funSymbols)
            argList.append(a)

        if node.id in symbols.symbols.keys():
            error_str = "Semantic error at line {0} - function {1} already declared"
            print(error_str.format(node.lineno,node.id))
        else:
            symbol = SymbolTable.FunctionSymbol(node.id, node.retType, dict(argList))
            symbols.put(node.id, symbol)

        self.visit(node.body, funSymbols)

    def visit_Argument(self, node, symbols):
        symbol = SymbolTable.Symbol(node.id, node.type)
        symbols.put(node.id, symbol)
        return node.id, node.type

    def visit_CompoundInstruction(self, node, symbols):
        if "function" in  symbols.name or "loop" in symbols.name:
            symbolscope = symbols
        else:
            symbolscope = SymbolTable.SymbolTable(symbols, "compinst")

        self.visit(node.decList, symbolscope)
        self.visit(node.incList, symbolscope)

    def visit_InstructionList(self, node, symbols):
        for inst in node.elements:
            self.visit(inst, symbols)

    def visit_BreakInstruction(self,node,symbols):
        if symbols.checkIfLoop():
            return True
        else:
            error_str = "Semantic error at line {0} - break instruction called outside of loop"
            print(error_str.format(node.lineno))
            return None

    def visit_ContinueInstruction(self,node,symbols):
        if symbols.checkIfLoop():
            return True
        else:
            error_str = "Semantic error at line {0} - continue instruction called outside of loop"
            print(error_str.format(node.lineno))
            return None

    def visit_PrintInstruction(self, node, symbols):
        self.visit(node.expr, symbols)

    def visit_ReturnInstruction(self, node, symbols):
        try:
            ttype['='][symbols.getFunctionType()][self.visit(node.returns, symbols)]
        except KeyError:
            error_str = "Semantic error at line {0} - wrong type in return statement"
            print(error_str.format(node.lineno))
            return None

    def visit_WhileLoopInstruction(self, node, symbols):
        loopSymbols = SymbolTable.SymbolTable(symbols, "loop")
        self.visit(node.condition, symbols)
        self.visit(node.instructions, loopSymbols)

    def visit_RepeatLoopInstruction(self, node, symbols):
        loopSymbols = SymbolTable.SymbolTable(symbols, "loop")
        self.visit(node.condition, symbols)
        self.visit(node.instructions, loopSymbols)

    def visit_IfInstruction(self, node, symbols):
        new_scope = SymbolTable.SymbolTable(symbols, "compinst")
        self.visit(node.condition, symbols)
        self.visit(node.instruction, new_scope)

    def visit_IfElseInstruction(self, node, symbols):
        #node.condition.lineno = node.lineno
        new_scope = SymbolTable.SymbolTable(symbols, "compinst")
        self.visit(node.condition, symbols)
        self.visit(node.instruction, new_scope)
        self.visit(node.no_instruction, new_scope)

    def visit_Assignment(self, node, symbols):
        try:
            ttype['='][symbols.get(node.left).type][self.visit(node.right, symbols)]
        except KeyError:
            error_str = "Semantic error at line {0} - wrong assignement"
            print(error_str.format(node.lineno))
            return None

    def visit_ID(self, node, symbols):
        if symbols.get(node.id):
            return symbols.get(node.id).type
        else:
            error_str = "Semantic error at line {0} - variable not defined"
            print(error_str.format(node.lineno))
            return None

    def visit_FunctionCall(self, node, symbols):
        symbol = symbols.get(str(node.id))
        if symbol:
            expected = len(node.arglist.elements)
            given = len(symbol.arguments)
            if expected != given:
                print("Incorrect amount of arguments. Expected: {0}, given: {1} in line: {2}".format(expected, given, node.lineno))
            else:
                for argtype, arg in zip(symbol.arguments, node.arglist.elements):
                    try:
                        ttype['='][symbol.arguments[argtype]][self.visit(arg, symbols)]
                    except KeyError:
                        error_str = "Semantic error at line {0} - wrong argument type"
                        print(error_str.format(node.lineno))

            return symbols.get(str(node.id)).type
        else:
            print("Function not defined")
            return False

    def visit_Integer(self, node, symbols):
        return 'int'

    def visit_Float(self, node, symbols):
        return 'float'

    def visit_String(self, node, symbols):
        return 'string'
