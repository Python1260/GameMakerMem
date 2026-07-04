from ...structure import Structure

class VMBuffer(Structure):
    def __init__(self, memory, address):
        super().__init__(memory, address)
    
    @classmethod
    def new(cls, memory):
        address = memory.executor.allocate_structure(0x30, cls.__name__)
        vmbuffer = cls(memory, address)
        
        return vmbuffer
    
    def get_buffer(self):
        size = self.memory.read_int(self + 0x8)
        buffer = self.memory.read_ptr(self + 0x18)

        return self.memory.read_bytes(buffer, size)

    def set_buffer(self, buffer):
        newsize = len(buffer)
        newbuffer = self.memory.executor.allocate(newsize)

        success = self.memory.write_bytes(newbuffer, buffer)
        success = success and self.memory.write_ptr(self + 0x18, newbuffer)
        success = success and self.memory.write_int(self + 0x8, newsize)

        return success