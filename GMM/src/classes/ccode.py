from ..structure import Structure
from ..settings.types import *
from .vm import VMBuffer

class CCode(Structure):
    def __init__(self, memory, address):
        super().__init__(memory, address)
    
    @property
    def offset(self):
        return self.memory.read_int(self + 0x9C)
    
    @offset.setter
    def offset(self, value):
        return self.memory.write_int(self + 0x9C, value)
    
    @property
    def locals(self):
        return self.memory.read_int(self + 0xA0)
    
    @locals.setter
    def locals(self, value):
        vmbuffer = self.memory.read_ptr(self + 0x68)

        self.memory.write_int(self + 0xA0, value)
        self.memory.write_int(vmbuffer + 0xC, value)

        # set some flags so it doesnt try to free nonexisting variables
        flags = (self.get_codeindex() & CODE_ISCONSTRUCTOR) | CODE_FREELOCALS
        self.memory.write_int(self + 0xA8, flags)
    
    @property
    def args(self):
        return self.memory.read_int(self + 0xA4)
    
    @args.setter
    def args(self, value):
        vmbuffer = self.memory.read_ptr(self + 0x68)

        self.memory.write_int(self + 0xA4, value & 0x1FFF)
        self.memory.write_int(vmbuffer + 0x10, value)

    @property
    def flags(self):
        return self.memory.read_int(self + 0xA8)

    def get_name(self):
        return self.memory.read_string(self.memory.read_ptr(self + 0x80))
    
    def get_codeindex(self):
        return self.memory.read_int(self + 0x88)
    
    def get_vmbuffer(self):
        ptr = self.memory.read_ptr(self + 0x68)
        vmbuffer = VMBuffer(self.memory, ptr)

        if not vmbuffer:
            vmbuffer = VMBuffer.new(self.memory)
            self.memory.write_ptr(self + 0x68, vmbuffer)

        return VMBuffer(self.memory, ptr)
    
    def get_bytecode(self):
        vmbuffer = self.get_vmbuffer()

        return vmbuffer.get_buffer()
    
    def set_bytecode(self, bytecode):
        vmbuffer = self.get_vmbuffer()

        return vmbuffer.set_buffer(bytecode)
    
    def get_func(self):
        return self.memory.read_ptr(self + 0x90)
    
    def set_func(self, func):
        return self.memory.write_ptr(self + 0x90, func)