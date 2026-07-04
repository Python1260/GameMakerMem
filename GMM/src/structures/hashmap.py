from ..structure import Structure

class HashMap(Structure):
    def __init__(self, memory, address):
        super().__init__(memory, address)
    
    def get_size(self):
        return self.memory.read_int(self + 0x0)
    
    def get_storage(self):
        return self.memory.read_ptr(self + 0x10)

    def get_elements(self):
        elements = {}

        storage = self.get_storage()

        for i in range(self.get_size()):
            element = storage + i * 0x18
            h = self.memory.read_int(element + 0x10)
            if h == 0: continue
            
            v = self.memory.read_int(element + 0x0)
            k = self.memory.read_string(self.memory.read_ptr(element + 0x8))

            elements[k] = v
        
        return elements