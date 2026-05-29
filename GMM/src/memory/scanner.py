import re
import pymem.pattern

class Scanner():
    def __init__(self, memory):
        self.memory = memory

    def scan(self, pattern, module=None, return_multiple=False):
        isstr = isinstance(pattern, str)

        if isstr:
            pattern = "".join(pattern.lower().split())
            bpattern = [pattern[i:i+2] for i in range(0, len(pattern), 2)]
            bpattern = b"".join(b"." if c in ("??", "xx") else re.escape(bytes.fromhex(c)) for c in bpattern)
        else:
            bpattern = pattern
        
        if module is not None:
            if isinstance(module, tuple):
                current, end = module

                matches = []

                while current < end:
                    next_region, found = pymem.pattern.scan_pattern_page(
                        self.memory.handle,
                        current,
                        bpattern,
                        return_multiple=return_multiple
                    )

                    if return_multiple:
                        matches += found
                    else:
                        matches = found
                        break

                    current = next_region
            else:
                matches = pymem.pattern.pattern_scan_module(
                    self.memory.handle,
                    module,
                    bpattern,
                    return_multiple=return_multiple
                )
        else:
            matches = pymem.pattern.pattern_scan_all(
                self.memory.handle,
                bpattern,
                return_multiple=return_multiple
            )
        
        if not isstr:
            return matches
        
        if not return_multiple: matches = [matches]

        start = pattern.find("x") // 2
        end = (pattern.rfind("x") + 1) // 2

        if start and end:
            results = []

            for match in matches:
                data = self.memory.read_bytes(match + start, end - start)
                result = int.from_bytes(data, "little")

                results.append(result)
        else:
            results = matches

        return results[0] if not return_multiple else results
    
    def get_module(self, name, prop=None):
        if isinstance(name, int):
            for mdl in self.memory.process.list_modules():
                if mdl.lpBaseOfDll <= name < (mdl.lpBaseOfDll + mdl.SizeOfImage):
                    module = mdl
                    break
            else:
                return None
        else:
            module = pymem.process.module_from_name(self.memory.handle, name)
        
        return getattr(module, prop) if prop is not None else module
    
    def get_module_section(self, module, section):
        e_magic = self.memory.read_short(module.lpBaseOfDll)
        e_lfanew = self.memory.read_int(module.lpBaseOfDll + 0x3c)

        nt_base = module.lpBaseOfDll + e_lfanew
        signature = self.memory.read_int(nt_base)

        number_of_sections = self.memory.read_short(nt_base + 0x6)
        size_of_optional_header = self.memory.read_short(nt_base + 0x14)

        section_headers_base = (
            nt_base
            + 0x4
            + 0x14
            + size_of_optional_header
        )
        section_size = 0x28

        for i in range(number_of_sections):
            addr = section_headers_base + i * section_size

            name = self.memory.read_string(addr, length=0x8)

            if name == section:
                virtual_size = self.memory.read_int(addr + 0x8)
                virtual_address = self.memory.read_int(addr + 0xC)

                start = module.lpBaseOfDll + virtual_address
                size = virtual_size

                return start, size
        
        return 0, 0
    
    def get_version(self):
        codestart, codesize = self.get_module_section(self.memory.module, ".text")

        occurence = self.scan(
            "41 B9 ?? ?? ?? ?? C7 44 24 20 ?? ?? ?? ?? BA ?? ?? ?? ?? 48 8D 0D ?? ?? ?? ?? 45 8D 41 ?? E8 ?? ?? ?? ?? 48 8B 15 ?? ?? ?? ?? 48 85 D2 0F 84 ?? ?? ?? ??",
            module=(codestart, codestart + codesize)
        )

        if occurence:
            data = self.memory.read_bytes(occurence, 51)

            a = int.from_bytes(data[2:6], "little")
            b = int.from_bytes(data[10:14], "little")
            c = int.from_bytes(data[15:19], "little")
            d = a + data[29]

            return f"{c}.{d}.{a}.{b}"
        
        occurence = self.scan(
            "48 8D 05 ?? ?? ?? ?? 48 89 44 24 38 C7 44 24 30 ?? ?? ?? ?? 48 89 5C 24 28 C7 44 24 20 ?? ?? ?? ?? E8 ?? ?? ?? ?? 48 8B 05 ?? ?? ?? ?? 48 85 C0 74",
            module=(codestart, codestart + codesize)
        )

        if occurence:
            data = self.memory.read_bytes(occurence, 49)

            a = int.from_bytes(data[16:20], "little")
            b = int.from_bytes(data[29:33], "little")

            return f"{b}.{a}"
        
        return "0"