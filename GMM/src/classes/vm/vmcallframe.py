from ...structure import Structure
from ...structures import ObjectBase

FRAME_MAGIC = 0xAABBCCDD

class VMCallFrame(Structure):
    def __init__(self, memory, address):
        super().__init__(memory, address)
    
    def __bool__(self):
        return super().__bool__() and self.memory.read_int(self.address) == FRAME_MAGIC
    
    def get_previous(self):
        return self.memory.read_int(self + 0x10)

    def get_self(self):
        ptr = self.memory.read_ptr(self + 0x20)
        return ObjectBase(self.memory, ptr)
    
    def get_other(self):
        ptr = self.memory.read_ptr(self + 0x28)
        return ObjectBase(self.memory, ptr)
    
    def get_code(self):
        from .. import CCode
        
        ptr = self.memory.read_ptr(self + 0x30)
        return CCode(self.memory, ptr)
    
    def get_locals(self):
        ptr = self.memory.read_ptr(self + 0x60)
        return ObjectBase(self.memory, ptr)