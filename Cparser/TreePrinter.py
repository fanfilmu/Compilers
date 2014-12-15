import AST

# "| " + "\n| ".join(str.split('\n'))


def addToClass(cls):
    def decorator(func):
        setattr(cls, func.__name__, func)
        return func

    return decorator


class TreePrinter:
    @staticmethod
    def addLevel(object):
        return "| " + "\n| ".join(str(object).split('\n'))

    @addToClass(AST.Node)
    def printTree(self):
        raise Exception("printTree not defined in class " + self.__class__.__name__)

    @addToClass(AST.List)
    def printTree(self):
        return '\n'.join(map(str, self.elements))

    @addToClass(AST.Function)
    def printTree(self):
        result = "FUNDEF\n"
        result += TreePrinter.addLevel(self.id) + '\n'
        result += TreePrinter.addLevel(self.retType) + '\n'
        result += TreePrinter.addLevel(self.arglist) + '\n'
        result += TreePrinter.addLevel(self.body)
        return result

    @addToClass(AST.Program)
    def printTree(self):
        result = str(self.declarations)+ '\n'
        if  len(self.fundefs.elements):
            result += str(self.fundefs)+ '\n'
        if len(self.instructions.elements):
            result += str(self.instructions)+ '\n'
        return result

    @addToClass(AST.Argument)
    def printTree(self):
        return "ARG {0}".format(self.id)


    @addToClass(AST.CompoundInstruction)
    def printTree(self):
        result = str(self.decList)
        result += str(self.incList)
        return result

    @addToClass(AST.IfElseInstruction)
    def printTree(self):
        result = "IF\n"
        result += TreePrinter.addLevel(self.condition) + '\n'
        result += TreePrinter.addLevel(self.instruction)
        result += "\nELSE\n"
        result += TreePrinter.addLevel(self.no_instruction)
        return result

    @addToClass(AST.FunctionCall)
    def printTree(self):
        result = "FUNCALL\n"
        result += TreePrinter.addLevel(self.id) + '\n'
        result += TreePrinter.addLevel(self.arglist)
        return result

    @addToClass(AST.BinExpr)
    def printTree(self):
        result = self.op + '\n'
        result += TreePrinter.addLevel(self.left) + '\n'
        result += TreePrinter.addLevel(self.right)
        return result

    @addToClass(AST.PrintInstruction)
    def printTree(self):
        result = "PRINT\n"
        result += TreePrinter.addLevel(self.expr)
        return result

    @addToClass(AST.ReturnInstruction)
    def printTree(self):
        result = "RETURN\n"
        result += TreePrinter.addLevel(self.returns)
        return result

    @addToClass(AST.WhileLoopInstruction)
    def printTree(self):
        result = "WHILE\n"
        result += TreePrinter.addLevel(self.condition) +'\n'
        result += TreePrinter.addLevel(self.instructions)
        return result

    @addToClass(AST.RepeatLoopInstruction)
    def printTree(self):
        result = "REPEAT\n"
        result += TreePrinter.addLevel(self.instructions)+"\n"
        result += "UNTIL\n"
        result += TreePrinter.addLevel(self.condition)
        return result

    @addToClass(AST.Declaration)
    def printTree(self):
        result = "DECL\n"
        result += TreePrinter.addLevel(self.initList)
        return result

    @addToClass(AST.Const)
    def printTree(self):
        result = self.value
        return result

    @addToClass(AST.BreakInstruction)
    def printTree(self):
        return "BREAK\n"

    @addToClass(AST.ContinueInstruction)
    def printTree(self):
        return "CONTINUE\n"

    @addToClass(AST.IfInstruction)
    def printTree(self):
        result = "IF\n"
        result += TreePrinter.addLevel(self.condition) + '\n'
        result += TreePrinter.addLevel(self.instruction)
        return result

    @addToClass(AST.LabeledInstruction)
    def printTree(self):
        result = "LABEL "
        result += self.label+"\n"
        result += TreePrinter.addLevel(self.instruction)
        return result