import AST
from Memory import *
from Exceptions import *
from visit import *
from collections import defaultdict

optype = {}
optype["+"] = lambda x, y: x + y
optype["-"] = lambda x, y: x - y
optype["*"] = lambda x, y: x * y
optype["/"] = lambda x, y: x / y
optype["%"] = lambda x, y: x % y
optype["|"] = lambda x, y: x | y
optype["&"] = lambda x, y: x & y
optype["^"] = lambda x, y: x ^ y
optype["SHL"] = lambda x, y: x << y
optype["SHR"] = lambda x, y: x >> y
optype["<"] = lambda x, y: 1 if x < y else 0
optype[">"] = lambda x, y: 1 if x > y else 0
optype["<="] = lambda x, y: 1 if x <= y else 0
optype[">="] = lambda x, y: 1 if x >= y else 0
optype["=="] = lambda x, y: 1 if x == y else 0
optype["!="] = lambda x, y: 1 if x != y else 0
optype["&&"] = lambda x, y: 1 if (x and y) else 0
optype["||"] = lambda x, y: 1 if (x or y) else 0

class Interpreter(object):
    def __init__(self):
        self.memory_stack = defaultdict(lambda: Memory(self.memory_stack[0]))
        self.memory_stack[0] = Memory()

    def get_scope(self, scope):
        hash = self.memory_stack.keys()[-1]

        while hash in self.memory_stack.keys():
            hash = hash + 1

        self.memory_stack[hash] = Memory(self.memory_stack[scope])
        return hash

    @on('node')
    def visit(self, node, scope=0):
        pass

    @when(AST.Program)
    def visit(self, node, scope=0):
        node.declarations.accept(self, scope)
        node.fundefs.accept(self, scope)
        node.instructions.accept(self, scope)

    @when(AST.List)
    def visit(self, node, scope=0):
        r = []
        for element in node.elements:
            r.append(element.accept(self, scope))

        return tuple(r)

    @when(AST.Declaration)
    def visit(self, node, scope=0):
        node.initList.accept(self, scope)

    @when(AST.Init)
    def visit(self, node, scope=0):
        if node.left in self.memory_stack[scope].keys():
            raise Exception("Variable {0} already defined".format(node.left))
        value = node.right.accept(self, scope)
        self.memory_stack[scope][node.left] = value
        return value

    @when(AST.Function)
    def visit(self, node, scope=0):
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
    def visit(self, node, scope=0):
        new_scope = self.get_scope(scope)
        node.decList.accept(self, new_scope)
        node.incList.accept(self, new_scope)

    @when(AST.Assignment)
    def visit(self, node, scope=0):
        if node.left in self.memory_stack[scope].scope_keys():
            value = node.right.accept(self, scope)
            self.memory_stack[scope].scope_setitem(node.left, value)
            return value
        else:
            raise Exception("Undeclared variable {0}".format(node.left))

    @when(AST.BinExpr)
    def visit(self, node, scope=0):
        left = node.left.accept(self, scope)
        right = node.right.accept(self, scope)

        return optype[node.op](left, right)
        #eval("{0} {1} {2}".format(left, node.op, right))

    @when(AST.Integer)
    def visit(self, node, scope=0):
        return int(node.value)

    @when(AST.Float)
    def visit(self, node, scope=0):
        return float(node.value)

    @when(AST.String)
    def visit(self, node, scope=0):
        return node.value[1:-1]

    @when(AST.ID)
    def visit(self, node, scope=0):
        return self.memory_stack[scope][node.id]

    @when(AST.WhileLoopInstruction)
    def visit(self, node, scope=0):
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
    def visit(self, node, scope=0):
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
    def visit(self, node, scope=0):
        if node.condition.accept(self, scope):
            node.instruction.accept(self, scope)

    @when(AST.IfElseInstruction)
    def visit(self, node, scope=0):
        if node.condition.accept(self, scope):
            node.instruction.accept(self, scope)
        else:
            node.no_instruction.accept(self, scope)

    @when(AST.PrintInstruction)
    def visit(self, node, scope=0):
        value = node.expr.accept(self, scope)
        print value
        return value

    @when(AST.LabeledInstruction)
    def visit(self, node, scope=0):
        return node.instruction.accept(self, scope)

    @when(AST.ReturnInstruction)
    def visit(self, node, scope=0):
        raise ReturnValueException(node.returns.accept(self, scope))

    @when(AST.ContinueInstruction)
    def visit(self, node, scope=0):
        raise ContinueException()

    @when(AST.BreakInstruction)
    def visit(self, node, scope=0):
        raise BreakException()

    @when(AST.FunctionCall)
    def visit(self, node, scope=0):
        args = node.arglist.accept(self, scope)
        fun = node.id.accept(self, scope)

        return fun(*args)
