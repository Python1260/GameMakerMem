from ...structure import Structure
from .vmcallframe import VMCallFrame

class VMExec(Structure):
    def __init__(self, memory, address):
        super().__init__(memory, address)
    
    def get_prev(self):
        ptr = self.memory.read_ptr(self + 0x0)
        return VMExec(self.memory, ptr)

    def get_next(self):
        ptr = self.memory.read_ptr(self + 0x8)
        return VMExec(self.memory, ptr)

    def get_stack(self):
        return self.memory.read_ptr(self + 0x10)
    
    def get_stacksize(self):
        return self.memory.read_int(self + 0x88)

    def get_retcount(self):
        return self.memory.read_int(self + 0x94)
    
    def get_callframe(self, index=0):
        if index < 0 or index > self.get_retcount():
            return None

        ptr = self.memory.read_ptr(self + 0x58)
        frame = VMCallFrame(self.memory, ptr)

        stacktop = self.get_stack() + self.get_stacksize()

        for i in range(index):
            if not frame:
                return None

            ptr = stacktop - frame.get_previous()
            frame = VMCallFrame(self.memory, ptr)
        
        return frame if frame else None