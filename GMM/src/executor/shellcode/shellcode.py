from .parser import Parser

class ShellcodeHandler():
    def __init__(self, memory):
        self.memory = memory
        self.parser = Parser(self)

        self.shellcode = bytearray()

        self.shellcode_address = 0x0
        self.result_address = 0x0
        self.flag_address = 0x0
    
    def begin(self):
        self.parser.begin()

        self.shellcode = bytearray()

        self.shellcode_address = 0x0
        self.result_address = 0x0
        self.flag_address = 0x0
    
    def submit(self):
        code_start = self.memory.allocate(len(self.shellcode))
        self.memory.write_bytes(code_start, bytes(self.shellcode))

        self.shellcode_address = code_start

        return code_start
    
    def wait(self, return_type=int, freeparsed=True):
        while self.flag_address and not self.memory.read_char(self.flag_address): pass
        result = self.memory.read_bytes(self.result_address, 0x8)

        self.free(freeparsed)

        return self.parser.unparse(result, return_type)
    
    def free(self, freeparsed=True):
        if self.shellcode_address: self.memory.free(self.shellcode_address)
        if self.result_address: self.memory.free(self.result_address)
        if self.flag_address: self.memory.free(self.flag_address)

        if freeparsed:
            self.parser.free()
    
    def instr_call(self, function, *args):
        function = self.parser.parse(function)

        arg_size = max(0x20, len(args) * 0x8)
        if (arg_size % 0x10) != 0x8: arg_size += 0x8

        self.shellcode += b"\x48\x81\xEC" + arg_size.to_bytes(4, "little")

        for idx, arg in enumerate(args):
            arg = self.parser.parse(arg)

            if idx == 0:
                self.shellcode += b"\x48\xB9" + arg
            elif idx == 1:
                self.shellcode += b"\x48\xBA" + arg
            elif idx == 2:
                self.shellcode += b"\x49\xB8" + arg
            elif idx == 3:
                self.shellcode += b"\x49\xB9" + arg
            else:
                offset = idx * 0x8

                self.shellcode += b"\x48\xB8" + arg
                self.shellcode += b"\x48\x89\x84\x24" + offset.to_bytes(4, "little")
        
        self.shellcode += b"\x48\xB8" + function
        self.shellcode += b"\xFF\xD0"
        self.shellcode += b"\x48\x81\xC4" + arg_size.to_bytes(4, "little")
    
    def instr_release(self):
        self.result_address = self.memory.allocate(0x8)
        self.flag_address = self.memory.allocate(0x1)

        result_address = self.parser.parse(self.result_address)
        flag_address = self.parser.parse(self.flag_address)

        self.shellcode += b"\x48\xBB" + result_address
        self.shellcode += b"\x48\x89\x03"
        self.shellcode += b"\x48\xB8" + flag_address
        self.shellcode += b"\xC6\x00\x01"
    
    def instr_return(self):
        self.shellcode += b"\xC3"
    
    def instr_jump(self, address):
        address = self.parser.parse(address)

        self.shellcode += b"\x48\xB8" + address
        self.shellcode += b"\xFF\xE0"