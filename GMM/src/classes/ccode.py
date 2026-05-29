from ..structure import Structure

class CCode(Structure):
    def __init__(self, memory, address):
        super().__init__(memory, address)

        self.saved_length = 0
        self.saved_ptr = 0x0
    
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

        flags = self.get_codeindex() & 0x80000000 | ((4 if value == 0 else 0) >> 13)
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
    
    def save_bytecode(self):
        if self.saved_ptr: return

        vmbuffer = self.memory.read_ptr(self + 0x68)

        size = self.memory.read_int(vmbuffer + 0x8)
        buffer = self.memory.read_ptr(vmbuffer + 0x18)

        self.saved_length = size
        self.saved_ptr = buffer

    def reset_bytecode(self):
        if not self.saved_ptr: return

        vmbuffer = self.memory.read_ptr(self + 0x68)

        buffer = self.memory.read_ptr(vmbuffer + 0x18)
        self.memory.free(buffer)

        success = self.memory.write_int(vmbuffer + 0x8, self.saved_length)
        success = success and self.memory.write_ptr(vmbuffer + 0x18, self.saved_ptr)

        return success
    
    def get_bytecode(self):
        vmbuffer = self.memory.read_ptr(self + 0x68)

        size = self.memory.read_int(vmbuffer + 0x8)
        buffer = self.memory.read_ptr(vmbuffer + 0x18)

        return self.memory.read_bytes(buffer, size)
    
    def set_bytecode(self, bytecode):
        newsize = len(bytecode)
        newbuffer = self.memory.executor.allocate(newsize)

        self.save_bytecode()

        vmbuffer = self.memory.read_ptr(self + 0x68)

        success = self.memory.write_int(vmbuffer + 0x8, newsize)
        success = success and self.memory.write_bytes(newbuffer, bytecode)
        success = success and self.memory.write_ptr(vmbuffer + 0x18, newbuffer)

        return success