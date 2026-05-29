class Structure():
    def __init__(self, memory, address):
        self.memory = memory
        self.address = address
    
    def __bool__(self):
        return self.address > 0x0
    
    def __eq__(self, value):
        return self.address == (value.address if isinstance(value, Structure) else value)
    
    def __str__(self):
        return f"{self.__class__.__name__} at {hex(self.address)}"
    
    __repr__ = __str__

    def __add__(self, other):
        return self.address + other
    
    def destroy(self):
        self.memory.free(self.address)
    
    @staticmethod
    def any_prop(func, offset, readonly=False):
        offsetresolver = lambda self, offset : getattr(self.memory, offset) if isinstance(offset, str) else offset
        getter = lambda self : getattr(self.memory, f"read_{func}")(self + offsetresolver(self, offset))
        setter = lambda self, value : getattr(self.memory, f"write_{func}")(self + offsetresolver(self, offset), value)

        return property(getter) if readonly else property(getter, setter)
    
    @staticmethod
    def int_prop(offset, readonly=False):
        return Structure.any_prop("int", offset, readonly)
    
    @staticmethod
    def float_prop(offset, readonly=False):
        return Structure.any_prop("float", offset, readonly)
    
    @staticmethod
    def bool_prop(offset, readonly=False):
        return Structure.any_prop("bool", offset, readonly)