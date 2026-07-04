from ..structure import Structure
from .rvalue import RValue

class StructVarsMap(Structure):
    def __init__(self, memory, address):
        super().__init__(memory, address)
    
    def __str__(self):
        return str(self.get_elements())
    
    __repr__ = __str__
    
    def get_size(self):
        return self.memory.read_int(self + 0x0)
    
    def get_storage(self):
        return self.memory.read_ptr(self + 0x10)

    def get_elements(self):
        elements = []

        storage = self.get_storage()

        for i in range(self.get_size()):
            element = storage + i * 0x10

            h = self.memory.read_int(element + 0xC)
            if h == 0: continue

            k = self.memory.read_int(element + 0x8)
            name = self.memory.context.get_codevariablename(k)

            elements.append(name)
        
        return elements
    
    def get(self, key):
        storage = self.get_storage()

        for i in range(self.get_size()):
            element = storage + i * 0x10

            h = self.memory.read_int(element + 0xC)
            if h == 0: continue

            k = self.memory.read_int(element + 0x8)
            name = self.memory.context.get_codevariablename(k)

            if name == key:
                v = self.memory.read_ptr(element + 0x0)
                value = RValue(self.memory, v)

                return value.get_value()
        
        return None
    
    def set(self, key, val):
        storage = self.get_storage()

        for i in range(self.get_size()):
            element = storage + i * 0x10
            h = self.memory.read_int(element + 0xC)
            if h == 0: continue

            k = self.memory.read_int(element + 0x8)
            name = self.memory.context.get_codevariablename(k)

            if name == key:
                v = self.memory.read_ptr(element + 0x0)
                value = RValue(self.memory, v)

                return value.set_value(val)
        
        return False