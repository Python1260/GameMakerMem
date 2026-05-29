from ..structure import Structure

class LinkedList(Structure):
    def __init__(self, memory, address, etype):
        super().__init__(memory, address)

        self.etype = etype
    
    def __len__(self):
        return self.get_length()
    
    def __iter__(self):
        return iter(self.get_elements())
    
    def __getitem__(self, key):
        return self.get_elements()[key]
    
    def get_first(self):
        return self.etype(self.memory, self.memory.read_ptr(self + 0x0))

    def get_last(self):
        return self.etype(self.memory, self.memory.read_ptr(self + 0x8))

    def get_length(self):
        return self.memory.read_int(self + 0x10)
    
    def get_elements(self):
        elements = []
        element = self.get_first()

        for i in range(self.get_length()):
            elements.append(element)
            element = element.get_next()

        return elements