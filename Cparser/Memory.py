class Memory(dict):
    def __init__(self, parent_scope=None):
        self.parent_scope = parent_scope

    def __getitem__(self, item):
        if item in self.full_scope().keys():
            return self.full_scope()[item]
        else:
            return None

    def scope_setitem(self, key, value):
        if key in self.keys():
            self[key] = value
        elif self.parent_scope is not None:
            self.parent_scope.scope_setitem(key, value)
        else:
            self[key] = value

    def full_scope(self):
        parent_full_scope = ((self.parent_scope is not None) and self.parent_scope.full_scope().items()) or []
        return dict(parent_full_scope + self.items())


    def scope_keys(self):
        return self.full_scope().keys()


class MemoryStack(dict):
    pass


