#!/usr/bin/python


class Symbol(object):
    def __init__(self, name, type):
        self.name = name
        self.type = type


class VariableSymbol(Symbol):
    pass


class FunctionSymbol(Symbol):
    def __init__(self, name, type, arguments):
        Symbol.__init__(self, name, type)
        self.arguments = arguments


class SymbolTable(object):
    def __init__(self, parent, name):  # parent scope and symbol table name
        self.parent = parent
        self.name = name
        self.symbols = {}

    def put(self, name, symbol):  # put variable symbol or fundef under <name> entry
        self.symbols[name] = symbol

    def get(self, name):  # get variable symbol or fundef from <name> entry
        try:
            return self.symbols[name]
        except KeyError:
            return self.parent and self.parent.get(name)

    def getFunctionType(self):
        if "function" in self.name:
            return self.name.split('_')[1]
        elif self.parent:
            return self.parent.getFunctionType()
        else:
            return None

    def checkIfLoop(self):
        if "loop" in self.name:
            return True
        elif self.parent:
            return self.parent.checkIfLoop()
        else:
            return False





