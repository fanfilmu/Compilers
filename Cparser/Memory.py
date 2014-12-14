

class Memory(dict):

    def __init__(self, parent_scope=None):
        self.parent_scope = parent_scope

    def __getitem__(self, item):
        try:
            value = super(Memory, self).__getitem__(item)
        except KeyError:
            if self.parent_scope:
                value = self.parent_scope[item]
                if value:
                    self.__setitem__(item, value)
            else:
                value = None
                self.__setitem__(item, None)

        return value


class MemoryStack(dict):
    pass


