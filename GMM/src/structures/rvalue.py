from ..structure import Structure
from ..settings.types import *

class RValue(Structure):
    def __init__(self, memory, address):
        super().__init__(memory, address)
    
    def __str__(self):
        return str(self.get_value())

    __repr__ = __str__

    @classmethod
    def new(cls, memory, value=None):
        address = memory.executor.allocate(0x10)
        rvalue = cls(memory, address)

        rvalue.set_value(value)

        return rvalue
    
    def get_value(self, kind=None):
        from . import ObjectBase, ArrayBase

        value = None

        if kind is None:
            kind = self.get_kind() & 0xFFFFFF

        if kind == RVALUE_REAL:
            value = self.memory.read_double(self + 0x0)
            
        elif kind == RVALUE_STRING:
            ptr = self.memory.read_ptr(self + 0x0)
            length = self.memory.read_int(ptr + 0xC) & 0x7FFFFFFF
            value = self.memory.read_string(self.memory.read_ptr(ptr), length=length)

        elif kind == RVALUE_ARRAY:
            ptr = self.memory.read_ptr(self + 0x0)
            value = ArrayBase(self.memory, ptr)
            
        elif kind == RVALUE_POINTER:
            value = self.memory.read_ptr(self + 0x0)
        
        elif kind == RVALUE_UNDEFINED:
            value = None
        
        elif kind == RVALUE_STRUCT:
            ptr = self.memory.read_ptr(self + 0x0)
            value = ObjectBase(self.memory, ptr)

        elif kind == RVALUE_INT32:
            value = self.memory.read_int(self + 0x0)
        
        elif kind == RVALUE_INT64:
            value = self.memory.read_number(self + 0x0)
        
        elif kind == RVALUE_BOOL:
            value = self.memory.read_double(self + 0x0) != 0
        
        elif kind == RVALUE_REF:
            ptr = self.memory.read_number(self + 0x0)
            rid = ptr & 0xFFFFFF
            rtype = ptr >> 32

            value = (rtype, rid)

        return value
    
    def set_value(self, value, kind=None):
        from . import ObjectBase, ArrayBase

        result = False
        prevkind = self.get_kind()

        if kind is None:
            kind = RVALUE_UNDEFINED

            if isinstance(value, bool):
                kind = RVALUE_BOOL
            elif isinstance(value, float):
                kind = RVALUE_REAL
            elif isinstance(value, int):
                kind = RVALUE_INT64
            elif isinstance(value, str):
                kind = RVALUE_STRING
            elif isinstance(value, list):
                kind = RVALUE_ARRAY
            elif isinstance(value, tuple):
                kind = RVALUE_REF
            elif isinstance(value, dict):
                kind = RVALUE_STRUCT
            elif hasattr(value, "address"):
                kind = RVALUE_STRUCT

        if kind == RVALUE_REAL:
            result = self.memory.write_double(self + 0x0, value)
            
        elif kind == RVALUE_STRING:
            if prevkind == RVALUE_STRING:
                ptr = self.memory.read_ptr(self + 0x0)
            else:
                ptr = self.memory.executor.allocate(0x10)
                self.memory.write_int(ptr + 0x8, 1) # i kinda forgot why...

                self.memory.write_ptr(self + 0x0, ptr)

            newptr = self.memory.read_ptr(ptr)
            newlength = len(value.encode("utf-8", errors="ignore"))
            newptr = self.memory.executor.allocate(newlength + 1)

            result = self.memory.write_string(newptr, value)
            result = result and self.memory.write_ptr(ptr + 0x0, newptr)
            result = result and self.memory.write_int(ptr + 0xC, newlength)

        elif kind == RVALUE_ARRAY:
            if isinstance(value, list):
                if prevkind == RVALUE_ARRAY:
                    ptr = self.memory.read_ptr(self + 0x0)
                    prevvalue = ArrayBase(self.memory, ptr)
                    
                    result = prevvalue.set_all(value)
                else:
                    result = False # nuh uh
            else:
                result = self.memory.write_ptr(self + 0x0, value.address)
            
        elif kind == RVALUE_POINTER:
            result = self.memory.write_ptr(self + 0x0, value)
        
        elif kind == RVALUE_UNDEFINED:
            result = True
        
        elif kind == RVALUE_STRUCT:
            if isinstance(value, dict):
                if prevkind == RVALUE_STRUCT:
                    ptr = self.memory.read_ptr(self + 0x0)
                    prevvalue = ObjectBase(self.memory, ptr)

                    result = prevvalue.set_variables(value)
                else:
                    result = False # nuh uh again
            else:
                result = self.memory.write_ptr(self + 0x0, value.address)

        elif kind == RVALUE_INT32:
            result = self.memory.write_int(self + 0x0, value)
        
        elif kind == RVALUE_INT64:
            result = self.memory.write_number(self + 0x0, value)
        
        elif kind == RVALUE_BOOL:
            result = self.memory.write_double(self + 0x0, 1.0 if value else 0.0)
        
        elif kind == RVALUE_REF:
            rtype, rid = value
            number = rid | (rtype << 32)

            result = self.memory.write_number(self + 0x0, number)
        
        if result:
            self.set_kind(kind)

        return result
    
    def get_flags(self):
        return self.memory.read_int(self + 0x8)
    
    def set_flags(self, value):
        return self.memory.write_int(self + 0x8, value)
    
    def get_kind(self):
        return self.memory.read_int(self + 0xC)
    
    def set_kind(self, value):
        return self.memory.write_int(self + 0xC, value)