from ..structure import Structure
from .structvarsmap import StructVarsMap

class ObjectBase(Structure):
    def __init__(self, memory, address):
        super().__init__(memory, address)
    
    def __str__(self):
        prototype = self.get_prototype()

        if prototype.get_variable("toString"):
            return "method ref"
        return str(self.get_elements())
    
    __repr__ = __str__
    
    def get_structvarsmap(self):
        ptr = self.memory.read_ptr(self + self.memory.objectbase_structvarsmap)
        return StructVarsMap(self.memory, ptr)
    
    def get_prototype(self):
        ptr = self.memory.read_ptr(self + 0x20)
        return ObjectBase(self.memory, ptr)
    
    def get_script(self):
        from ..classes import CScript

        ptr = self.memory.read_ptr(self + self.memory.objectbase_script)
        return CScript(self.memory, ptr)

    def set_script(self, script):
        from ..classes import CScript

        return self.memory.write_ptr(self + self.memory.objectbase_script, script.address)
    
    def get_variable(self, name):
        if hasattr(self, name):
            return getattr(self, name)

        structvarsmap = self.get_structvarsmap()
        return structvarsmap.get(name)
    
    def get_variables(self):
        structvarsmap = self.get_structvarsmap()
        return sorted(structvarsmap.get_elements())

    def set_variable(self, name, value):
        if hasattr(self, name):
            return setattr(self, name, value)

        structvarsmap = self.get_structvarsmap()
        return structvarsmap.set(name, value)
    
    def set_variables(self, variables):
        return all(self.set_variable(key, value) for key, value in variables.items())
    
    def get_elements(self):
        elements = {}

        for name in self.get_variables():
            value = self.get_variable(name)

            elements[name] = value
        
        return elements