from ..structure import Structure

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

        flags = (self.get_codeindex() & 0x80000000) | 2 | 4 | 8
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
        vmbuffer = self.memory.read_ptr(self + 0x68)

        if not vmbuffer:
            vmbuffer = self.memory.executor.allocate_structure(0x30, "VMBuffer")
            self.memory.write_ptr(self + 0x68, vmbuffer)
        
        return vmbuffer
    
    def get_bytecode(self):
        vmbuffer = self.get_vmbuffer()

        size = self.memory.read_int(vmbuffer + 0x8)
        buffer = self.memory.read_ptr(vmbuffer + 0x18)

        return self.memory.read_bytes(buffer, size)
    
    def set_bytecode(self, bytecode):
        newsize = len(bytecode)
        newbuffer = self.memory.executor.allocate(newsize)

        vmbuffer = self.get_vmbuffer()

        success = self.memory.write_int(vmbuffer + 0x8, newsize)
        success = success and self.memory.write_bytes(newbuffer, bytecode)
        success = success and self.memory.write_ptr(vmbuffer + 0x18, newbuffer)

        return success
    
    def get_func(self):
        return self.memory.read_ptr(self.address + 0x90)
    
    def set_func(self, func):
        return self.memory.write_ptr(self.address + 0x90, func)