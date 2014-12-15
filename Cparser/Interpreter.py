import AST
from Memory import *
from Exceptions import *
from visit import *
from collections import defaultdict
from datetime import datetime
from random import Random


class Interpreter(object):
    def __init__(self):
        self.memory_stack = defaultdict(lambda: Memory(self.memory_stack["main"]))
        self.memory_stack["main"] = Memory()
        self.r = Random()

    def get_scope(self, scope):
        hash = datetime.now().__hash__() + int(self.r.random() * 10000)
        self.memory_stack[hash] = Memory(self.memory_stack[scope])
        return hash

    @on('node')
    def visit(self, node, scope="main"):
        pass

    @when(AST.Program)
    def visit(self, node, scope="main"):
        node.declarations.accept(self, scope)
        node.fundefs.accept(self, scope)
        node.instructions.accept(self, scope)

    @when(AST.List)
    def visit(self, node, scope="main"):
        r = []
        for element in node.elements:
            r.append(element.accept(self, scope))

        return tuple(r)

    @when(AST.Declaration)
    def visit(self, node, scope="main"):
        node.initList.accept(self, scope)

    @when(AST.Init)
    def visit(self, node, scope="main"):
        if node.left in self.memory_stack[scope].keys():
            raise Exception("Variable {0} already defined".format(node.left))
        value = node.right.accept(self, scope)
        self.memory_stack[scope][node.left] = value
        return value

    @when(AST.Function)
    def visit(self, node, scope="main"):
        def fun(*args):
            new_scope = self.get_scope(scope)
            if len(args) != node.arity():
                raise Exception("{0} takes {1} argument(s); {2} given".format(node.id, node.arity(), len(args)))

            for i in range(node.arity()):
                argument = node.arglist.elements[i]
                self.memory_stack[new_scope][argument.id] = args[i]

            try:
                node.body.accept(self, scope=new_scope)
            except ReturnValueException as e:
                return e.value

        self.memory_stack[scope][node.id] = fun

    @when(AST.CompoundInstruction)
    def visit(self, node, scope="main"):
        new_scope = self.get_scope(scope)
        node.decList.accept(self, new_scope)
        node.incList.accept(self, new_scope)

    @when(AST.Assignment)
    def visit(self, node, scope="main"):
        if node.left in self.memory_stack[scope].scope_keys():
            value = node.right.accept(self, scope)
            self.memory_stack[scope].scope_setitem(node.left, value)
            return value
        else:
            raise Exception("Undeclared variable {0}".format(node.left))

    @when(AST.BinExpr)
    def visit(self, node, scope="main"):
        left = node.left.accept(self, scope)
        right = node.right.accept(self, scope)

        if isinstance(left, str):
            left = "\"{}\"".format(left)
        if isinstance(right, str):
            right = "\"{}\"".format(right)

        return eval("{0} {1} {2}".format(left, node.op, right))

    @when(AST.Const)
    def visit(self, node, scope="main"):
        return eval(node.value)

    @when(AST.ID)
    def visit(self, node, scope="main"):
        return self.memory_stack[scope][node.id]

    @when(AST.WhileLoopInstruction)
    def visit(self, node, scope="main"):
        r = None
        try:
            while node.condition.accept(self, scope):
                try:
                    r = node.instructions.accept(self, scope)
                except ContinueException:
                    pass
        except BreakException:
            pass

        return r

    @when(AST.RepeatLoopInstruction)
    def visit(self, node, scope="main"):
        run = True
        r = None

        try:
            while run:
                try:
                    r = node.instructions.accept(self, scope)
                except ContinueException:
                    pass

                run = not node.condition.accept(self, scope)
        except BreakException:
            pass

        return r

    @when(AST.IfInstruction)
    def visit(self, node, scope="main"):
        if node.condition.accept(self, scope):
            node.instruction.accept(self, scope)

    @when(AST.IfElseInstruction)
    def visit(self, node, scope="main"):
        if node.condition.accept(self, scope):
            node.instruction.accept(self, scope)
        else:
            node.no_instruction.accept(self, scope)

    @when(AST.PrintInstruction)
    def visit(self, node, scope="main"):
        value = node.expr.accept(self, scope)
        print value
        return value

    @when(AST.LabeledInstruction)
    def visit(self, node, scope="main"):
        return node.instruction.accept(self, scope)

    @when(AST.ReturnInstruction)
    def visit(self, node, scope="main"):
        raise ReturnValueException(node.returns.accept(self, scope))

    @when(AST.ContinueInstruction)
    def visit(self, node, scope="main"):
        raise ContinueException()

    @when(AST.BreakInstruction)
    def visit(self, node, scope="main"):
        raise BreakException()

    @when(AST.FunctionCall)
    def visit(self, node, scope="main"):
        args = node.arglist.accept(self, scope)
        fun = node.id.accept(self, scope)

        return fun(*args)
