from ..structure import Structure
from ..structures import LinkedList
from .cinstance import CInstance

class CRoom(Structure):
    def __init__(self, memory, address):
        super().__init__(memory, address)
    
    width = Structure.int_prop("room_width")
    height = Structure.int_prop("room_height")
    persistent = Structure.bool_prop("room_persistent")

    def get_active(self):
        ptr = self + self.memory.croom_active
        return LinkedList(self.memory, ptr, CInstance)

    def get_deactive(self):
        ptr = self + self.memory.croom_active + 0x18
        return LinkedList(self.memory, ptr, CInstance)
    
    def get_instances(self):
        active = self.get_active()
        deactive = self.get_deactive()

        instances = active.get_elements() + deactive.get_elements()
        instances = list(filter(lambda i : not i.get_destroyed(), instances))

        return instances