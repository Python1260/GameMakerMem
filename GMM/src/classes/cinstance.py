from ..structure import Structure
from ..structures import ObjectBase
from ..settings.types import *

class CInstance(ObjectBase):
    def __init__(self, memory, address):
        super().__init__(memory, address)

        self.base_variables = [
            "id", "object_index", "sprite_index",
            "x", "y",
            "image_index", "image_speed", "image_xscale", "image_yscale", "image_angle", "image_blend", "image_alpha",
            "visible", "depth"
        ]
    
    def get_next(self):
        ptr = self.memory.read_ptr(self + 0x198)
        return CInstance(self.memory, ptr)
    
    def get_flags(self, mask):
        flags = self.memory.read_int(self + 0xB0)
        return (flags & mask) != 0x0
    
    def set_flags(self, mask, status):
        flags = self.memory.read_int(self + 0xB0)
        flags = (flags | mask) if status else (flags & ~mask)

        return self.memory.write_int(self + 0xB0, flags)

    def get_deactive(self):
        return self.get_flags(IFLAGS_DEACTIVE)
    
    def get_destroyed(self):
        return self.get_flags(IFLAGS_DESTROYED)
    
    def set_variable(self, name, value):
        self.set_flags(IFLAGS_SIMPLEDRAW, False)

        return super().set_variable(name, value)
    
    def get_variables(self):
        return super().get_variables() + self.base_variables
    
    id = Structure.int_prop(0xB4, True)

    @property
    def object_index(self):
        return (REF_OBJECT, self.memory.read_int(self.address + 0xB8))

    @property
    def sprite_index(self):
        return (REF_SPRITE, self.memory.read_int(self.address + 0xBC))
    
    @property
    def visible(self):
        return self.get_flags(IFLAGS_VISIBLE)
    
    @visible.setter
    def visible(self, value):
        return self.set_flags(IFLAGS_VISIBLE, value)

    image_index = Structure.float_prop("image_index")
    image_speed = Structure.float_prop("image_speed")
    image_xscale = Structure.float_prop("image_xscale")
    image_yscale = Structure.float_prop("image_yscale")
    image_angle = Structure.float_prop("image_angle")
    image_alpha = Structure.float_prop("image_alpha")
    image_blend = Structure.int_prop("image_blend")

    x = Structure.float_prop("x")
    y = Structure.float_prop("y")

    depth = Structure.float_prop("depth")