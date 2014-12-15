class Node(object):
    def __str__(self):
        return self.printTree()

    def setLineNo(self, line):
        self.lineno = line

    def accept(self, visitor, scope=0):
        return visitor.visit(self, scope)


class Program(Node):
    def __init__(self, decl, fundef, instr):
        self.declarations = decl
        self.fundefs = fundef
        self.instructions = instr


class FunctionCall(Node):
    def __init__(self, id, arglist):
        self.id = id
        self.arglist = arglist


class BinExpr(Node):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right


class RelExpr(BinExpr):
    pass


class Assignment(BinExpr):
    def __init__(self, left, right):
        BinExpr.__init__(self, '=', left, right)


class List(Node):
    def __init__(self, elements):
        self.elements = elements

    def __len__(self):
        return len(self.elements)

    def add(self, element):
        if isinstance(element, List):
            self.elements.extend(element.elements)
        else:
            self.elements.append(element)

        return self


class Declaration(Node):
    def __init__(self, type, initList):
        self.type = type
        self.initList = initList


class InitList(List):
    def addType(self, type):
        for e in self.elements:
            e.addType(type)


class Init(Assignment):
    def __init__(self, left, right):
        BinExpr.__init__(self, '=', left, right)

    def addType(self, type):
        self.type = type


class FunList(List):
    pass


class DeclarationList(List):
    pass


class InstructionList(List):
    pass


class Const(Node):
    def __init__(self, value):
        self.value = value


class Integer(Const):
    pass


class Float(Const):
    pass


class String(Const):
    pass


class ID(Node):
    def __init__(self, id):
        self.id = id


class ExpressionList(List):
    pass


class ArgumentList(List):
    pass


class Function(Node):
    def __init__(self, retType, id, arglist, body):
        self.body = body
        self.arglist = arglist
        self.id = id
        self.retType = retType

    def arity(self):
        return len(self.arglist)


class Variable(Node):
    def __init__(self, type, id):
        self.type = type
        self.id = id

        # ...


class Argument(Variable):
    pass


class Instruction(Node):
    pass


class CompoundInstruction(Instruction):
    def __init__(self, decList, incList):
        self.decList = decList
        self.incList = incList


class FlowInstruction(Instruction):
    pass


class BreakInstruction(FlowInstruction):
    pass


class ContinueInstruction(FlowInstruction):
    pass


class ReturnInstruction(Instruction):
    def __init__(self, returns):
        self.returns = returns


class LoopInstruction(Instruction):
    def __init__(self, condition, instructions):
        self.instructions = instructions
        self.condition = condition


class RepeatLoopInstruction(LoopInstruction):
    pass


class WhileLoopInstruction(LoopInstruction):
    pass


class IfInstruction(Instruction):
    def __init__(self, condition, instruction):
        self.condition = condition
        self.instruction = instruction


class IfElseInstruction(IfInstruction):
    def __init__(self, condition, yes_instruction, no_instruction):
        IfInstruction.__init__(self, condition, yes_instruction)
        self.no_instruction = no_instruction


class LabeledInstruction(Instruction):
    def __init__(self, label, instruction):
        self.label = label
        self.instruction = instruction


class PrintInstruction(Instruction):
    def __init__(self, expr):
        self.expr = expr