from ..structure import Structure
from .rvalue import RValue
from ..settings.types import *

class ArrayBase(Structure):
    def __init__(self, memory, address):
        super().__init__(memory, address)
    
    def __str__(self):
        return str(self.get_elements())
    
    __repr__ = __str__
    
    def get_size(self):
        return self.memory.read_int(self + self.memory.arraybase_size)
    
    def get_storage(self):
        return self.memory.read_ptr(self + self.memory.arraybase_storage)
    
    def get_flags(self, mask):
        flags = self.memory.read_int(self + self.memory.arraybase_flags)
        return (flags & mask) != 0x0
    
    def set_flags(self, mask, status):
        flags = self.memory.read_int(self + self.memory.arraybase_flags)
        flags = (flags | mask) if status else (flags & ~mask)

        return self.memory.write_int(self + self.memory.arraybase_flags, flags)

    def get_immutable(self):
        return self.get_flags(ARRAY_IMMUTABLE)
    
    def set_immutable(self, value):
        return self.set_flags(ARRAY_IMMUTABLE, value)

    def get_elements(self):
        elements = []

        storage = self.get_storage()

        for i in range(self.get_size()):
            element = storage + i * 0x10
            v = element + 0x0

            value = RValue(self.memory, v)

            elements.append(value.get_value())
        
        return elements
    
    def set_elements(self, elements):
        return all(self.set(index, value) for index, value in enumerate(elements))
    
    def get(self, index):
        storage = self.get_storage()

        if index < self.get_size():
            element = storage + index * 0x10
            v = element + 0x0

            value = RValue(self.memory, v)
            
            return value.get_value()

        return None
    
    def set(self, index, val):
        storage = self.get_storage()

        if index < self.get_size():
            element = storage + index * 0x10
            v = element + 0x0

            value = RValue(self.memory, v)
            
            return value.set_value(val)

        return None