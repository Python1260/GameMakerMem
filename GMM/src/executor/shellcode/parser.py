import struct

class Parser():
    def __init__(self, handler):
        self.handler = handler

        self.tofree = []

    def parse(self, value):
        if value is None: value = 0

        if isinstance(value, str):
            value = value.encode("utf-8", errors="ignore") + b"\x00"

        if isinstance(value, bytes):
            address = self.handler.memory.allocate(len(value))
            self.handler.memory.write_bytes(address, value)

            value = address

            self.tofree.append(value)

        if isinstance(value, bool):
            value = struct.pack("<Q", 1 if value else 0)
        elif isinstance(value, float):
            value = struct.pack("<d", value)
        elif isinstance(value, int):
            value = struct.pack("<Q", value)
        else:
            value = struct.pack("<Q", value.address)
            
        return value
    
    def unparse(self, value, value_type):
        if value_type == int or value_type == bytes or value_type == str:
            value = struct.unpack("<Q", value)[0]
        elif value_type == float:
            value = struct.unpack("<d", value)[0]
        elif value_type == bool:
            value = True if struct.unpack("<Q", value)[0] else False
        else:
            value = None

        if value_type == bytes:
            value = self.handler.memory.read_string(value).encode("utf-8", errors="ignore")
        elif value_type == str:
            value = self.handler.memory.read_string(value)
        
        return value
    
    def begin(self):
        self.tofree.clear()

    def free(self):
        for address in self.tofree:
            self.handler.memory.free(address)