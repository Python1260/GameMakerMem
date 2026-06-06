from ..structure import Structure
from .structvarsmap import StructVarsMap
from ..settings.types import *

class ObjectBase(Structure):
    def __init__(self, memory, address):
        super().__init__(memory, address)
    
    def __str__(self):
        return str(self.get_elements())
    
    def get_structvarsmap(self):
        ptr = self.memory.read_ptr(self + self.memory.cinstance_structvarsmap)
        return StructVarsMap(self.memory, ptr)
    
    def get_variables(self):
        structvarsmap = self.get_structvarsmap()
        return sorted(structvarsmap.get_elements())
    
    def get_variable(self, name):
        if hasattr(self, name):
            return getattr(self, name)

        structvarsmap = self.get_structvarsmap()
        return structvarsmap.get(name)

    def set_variable(self, name, value):
        if hasattr(self, name):
            return setattr(self, name, value)

        structvarsmap = self.get_structvarsmap()
        return structvarsmap.set(name, value)
    
    def get_elements(self):
        elements = {}

        for name in self.get_variables():
            value = self.get_variable(name)

            elements[name] = value
        
        return elements