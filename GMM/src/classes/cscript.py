from ..structure import Structure
from .ccode import CCode

class CScript(Structure):
    def __init__(self, memory, address):
        super().__init__(memory, address)
    
    def get_name(self):
        return self.memory.read_string(self.memory.read_ptr(self + 0x28))
    
    def set_name(self, value):
        newptr = self.memory.read_ptr(self + 0x28)
        newlength = len(value.encode("utf-8", errors="ignore"))
        newptr = self.memory.executor.allocate(newlength + 1)

        result = self.memory.write_string(newptr, value)
        result = result and self.memory.write_ptr(self + 0x28, newptr)

        return result
    
    def get_code(self):
        ptr = self.memory.read_ptr(self + 0x8)
        return CCode(self.memory, ptr)
    
    def set_code(self, value):
        return self.memory.write_ptr(self + 0x8, value.address)
    
    def copy(self):
        size = 0x38
        vtable = self.memory.read_ptr(self.address)

        newaddress = self.memory.executor.allocate(size)
        self.memory.write_ptr(newaddress, vtable)

        newscript = CScript(self.memory, newaddress)

        return newscript