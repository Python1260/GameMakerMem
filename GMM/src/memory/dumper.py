class Dumper():
    def __init__(self, memory):
        self.memory = memory

        self.offsets = {}
        self.code_start = 0
        self.code_end = 0
    
    def init(self):
        cstart, csize = self.memory.scanner.get_module_section(self.memory.module, ".text")

        self.offsets.clear()
        self.code_start = cstart
        self.code_end = cstart + csize

    def dump(self):
        self.init()

        # ARG0 = GMS 2022 YYC, ARG1 = GMS 2024 YYC, ARG2 = GMS 2024 VM
        self.dump_basic()
        self.dump_data()
        self.dump_thefunctions()
        self.dump_execution()
        self.dump_other()

        return self.offsets
    
    def dump_basic(self):
        self.offsets["RunRoom"] =               self.scan_rel32("48 8B 15 XX XX XX XX 48 85 D2 41 0F 95 ??", "48 89 0D XX XX XX XX 48 89 8D C0 03 00 00")
        self.offsets["CurrentRoom"] =           self.scan_rel32("48 63 0D XX XX XX XX 48 3B 0D ?? ?? ?? ?? 73 0D", "89 3D XX XX XX XX 48 3B D8 0F 83 ?? ?? ?? ??")
        self.offsets["NewRoom"] =               self.scan_rel32("89 1D ?? ?? ?? ?? 89 0D XX XX XX XX E8 ?? ?? ?? ??", "33 D2 89 0D XX XX XX XX 89 15 ?? ?? ?? ?? 85 C9")
        self.offsets["Fps"] =                   self.scan_rel32("8B ?? XX XX XX XX 83 ?? 1E 7E 3C F3 0F 10 05 ?? ?? ?? ??")
        self.offsets["builtinVarLookup"] =      self.scan_rel32("42 88 44 31 18 48 8B 0D XX XX XX XX E8 ?? ?? ?? ??")
        self.offsets["instanceVarLookup"] =     self.scan_rel32("4C 8B 35 XX XX XX XX 41 8B 6E 04 44 8D 4D FF")
        self.offsets["VarNamesInstance"] =      self.scan_rel32("48 8B 05 XX XX XX XX 48 8B 74 24 ?? 48 8B 7C 24 ??")
        self.offsets["name2ref"] =              self.scan_rel32("48 8D 05 XX XX XX XX 0F 1F 80 00 00 00 00 39 48 08", default=-1) # this doesnt exist in older versions
        self.offsets["markedCount"] =           self.scan_rel32("83 8B B0 00 00 00 01 FF 05 XX XX XX XX", "")
        self.offsets["deactiveListDirty"] =     self.scan_rel32("74 0E C6 05 XX XX XX XX 01 C6 05 ?? ?? ?? ?? 01")
        self.offsets["activeListDirty"] =       self.scan_rel32("74 0E C6 05 ?? ?? ?? ?? 01 C6 05 XX XX XX XX 01")

    def dump_data(self):
        self.offsets["WADBase"] =               self.scan_rel32("48 89 0D XX XX XX XX 48 89 05 ?? ?? ?? ?? 41 8D 47 F8", "4C 89 35 XX XX XX XX 45 8B 46 04 4B 8D 04 26 48 89 05 ?? ?? ?? ??")
        self.offsets["WADEnd"] =                self.scan_rel32("48 89 0D ?? ?? ?? ?? 48 89 05 XX XX XX XX 41 8D 47 F8", "4C 89 35 ?? ?? ?? ?? 45 8B 46 04 4B 8D 04 26 48 89 05 XX XX XX XX")
        self.offsets["YYHeader"] =              self.scan_rel32("48 89 0D XX XX XX XX 48 8B F9 8B 01 C1 F8 08", "48 89 0D XX XX XX XX 89 15 ?? ?? ?? ?? 83 FA 08")
        self.offsets["YYString"] =              self.scan_rel32("48 89 0D XX XX XX XX 8B 0C 2E 89 0D ?? ?? ?? ??", "48 89 0D XX XX XX XX 43 8B 0C 37 89 0D ?? ?? ?? ??")
        self.offsets["YYStringCount"] =         self.scan_rel32("48 89 0D ?? ?? ?? ?? 8B 0C 2E 89 0D XX XX XX XX", "48 89 0D ?? ?? ?? ?? 43 8B 0C 37 89 0D XX XX XX XX")
        self.offsets["ScriptMainNumber"] =      self.scan_rel32("3B 3D XX XX XX XX 7D ?? 48 8B 0D ?? ?? ?? ?? 49 39 1C 0E", "3B 35 XX XX XX XX 7D ?? 48 8B 05 ?? ?? ?? ?? 48 8B 8D ?? ?? ?? ??")
        self.offsets["ScriptMainItemsArray"] =  self.scan_rel32("3B 3D ?? ?? ?? ?? 7D ?? 48 8B 0D XX XX XX XX 49 39 1C 0E", "3B 35 ?? ?? ?? ?? 7D ?? 48 8B 05 XX XX XX XX 48 8B 8D ?? ?? ?? ??")
        self.offsets["ScriptMainNames"] =       self.scan_rel32("48 8B 05 XX XX XX XX 48 8D 0D ?? ?? ?? ?? 41 B8 0B 00 00 00", "48 8B 3D XX XX XX XX 4C 63 DB 4D 8B D3 49 C1 E2 05", default=-1) # and this is different in newer versions
        self.offsets["StartGlobalVariables"] =  self.scan_rel32("77 ?? 83 79 ?? 01 75 ?? 3B 2D XX XX XX XX 7D ??", "81 FE 0F 27 00 00 77 ?? 3B 35 XX XX XX XX 7D ??")

    def dump_thefunctions(self):
        self.offsets["the_functions"] =         self.scan_rel32("33 C0 48 89 05 XX XX XX XX 89 05 ?? ?? ?? ?? 89 05 ?? ?? ?? ??", "4C 89 3D XX XX XX XX 44 89 3D ?? ?? ?? ?? 44 89 3D ?? ?? ?? ??")
        self.offsets["the_numb"] =              self.scan_rel32("33 C0 48 89 05 ?? ?? ?? ?? 89 05 XX XX XX XX 89 05 ?? ?? ?? ??", "4C 89 3D ?? ?? ?? ?? 44 89 3D XX XX XX XX 44 89 3D ?? ?? ?? ??")

        a = self.scan_value("41 B9 ?? ?? ?? ?? 48 8D 14 XX 48 C1 E2 ?? E8 ?? ?? ?? ??", "48 8D 14 XX 48 C1 E2 ?? 41 B9 ?? ?? ?? ??", "48 8D 14 XX 48 C1 E2 ?? C6 44 24 20 01 48 8B 0D ?? ?? ?? ??") # lea, different in newer versions
        b = self.scan_value("41 B9 ?? ?? ?? ?? 48 8D 14 ?? 48 C1 E2 XX E8 ?? ?? ?? ??", "48 8D 14 ?? 48 C1 E2 XX 41 B9 ?? ?? ?? ??", "48 8D 14 ?? 48 C1 E2 XX C6 44 24 20 01 48 8B 0D ?? ?? ?? ??") # shl, different in newer versions

        # lea + shl logic
        scale = 1 << (a >> 6)
        mul = (scale + 1) << b

        self.offsets["the_functions_size"] = mul

    def dump_execution(self):
        self.offsets["MemoryAlloc"] =           self.scan_rel32("E8 XX XX XX XX 48 89 45 ?? 48 85 C0 74 ?? 45 33 C0", "E8 XX XX XX XX 48 8B D8 48 85 C0 75 ?? 45 33 C0")
        self.offsets["NewCCode"] =              self.scan_rel32("48 8B ?? E8 XX XX XX XX 4C 8B C0 EB ?? 4D 8B ??")
        self.offsets["_vftable__VMBuffer"] =    self.scan_rel32("48 89 44 24 40 48 8B C8 4C 8D 35 XX XX XX XX 48 85 C0", "E8 ?? ?? ?? ?? 4C 8D 35 XX XX XX XX 48 8B F8 48 85 C0")
        self.offsets["ExecuteIt"] =             self.scan_rel32("E8 XX XX XX XX FF C6 48 83 C3 04 48 83 C7 08", "E8 XX XX XX XX 3C 01 74 ?? 48 8B 0D ?? ?? ?? ?? 48 8B 09")
        self.offsets["GlobalTable"] =           self.scan_rel32("48 8B 0D XX XX XX XX 48 8B D1 E8 ?? ?? ?? ?? FF C6", "48 8B 0D XX XX XX XX 44 89 64 24 20 4C 8D 4D 00")
        self.offsets["CurrentExec"] =           self.scan_rel32("48 8B 05 XX XX XX XX 48 85 C0 74 ?? 48 8D 4C 24 30")
        self.offsets["CodeVariableFindSlot"] =  self.scan_rel32("E8 XX XX XX XX 8B D0 48 8B CB E8 ?? ?? ?? ?? BA 01 00 00 00")

    def dump_other(self):
        self.offsets["croom_active"] =          self.scan_value("48 8B 80 XX XX XX XX 48 89 41 08 48 8B C3", "48 8B 80 XX XX XX XX 49 89 42 08 49 8B C2")

        self.offsets["objectbase_structvarsmap"] = self.scan_value("0F 1F 40 00 48 8B ?? XX 48 63 C3 FF C3 48 C1 E0 04")
        self.offsets["objectbase_script"] =        self.scan_value("48 8B 48 08 48 89 ?? ?? ?? ?? ?? EB 07 48 89 ?? XX XX XX XX")

        self.offsets["arraybase_size"] =           self.scan_value("74 ?? 66 0F 6E 41 XX F3 0F E6 C0 F2 0F 11 07", "74 ?? 66 0F 6E 81 XX XX XX XX F3 0F E6 C0 F2 0F 11 07")
        self.offsets["arraybase_storage"] =        self.scan_value("48 03 41 XX 83 78 0C 02 75 ?? 48 8B 08", "48 03 81 XX XX XX XX 83 78 0C 02 75 ?? 48 8B 08")
        self.offsets["arraybase_flags"] =          self.scan_value("48 8B ?? F6 87 XX 00 00 00 01 74 0C", "48 8B ?? F6 47 XX 01 74 0C")

        self.offsets["image_index"] = self.scan_value("F3 0F 11 B3 XX XX XX XX 45 8B C1 48 8B D3 48 8B CB", "F3 0F 59 83 XX XX XX XX F3 0F 11 83 ?? ?? ?? ?? 48 85 C0")
        self.offsets["image_speed"] = self.scan_value("F3 0F 10 8B XX XX XX XX F3 0F 59 8F ?? ?? ?? ?? F3 0F 58 C1", "F3 0F 10 8B XX XX XX XX F3 0F 59 8F ?? ?? ?? ?? F3 0F 58 C1")
        self.offsets["image_xscale"] = self.offsets["image_speed"] + 4
        self.offsets["image_yscale"] = self.offsets["image_speed"] + 8
        self.offsets["image_angle"] = self.offsets["image_speed"] + 12
        self.offsets["image_alpha"] = self.offsets["image_speed"] + 16
        self.offsets["image_blend"] = self.offsets["image_speed"] + 20
        self.offsets["x"] = self.offsets["image_speed"] + 24
        self.offsets["y"] = self.offsets["image_speed"] + 28

        self.offsets["depth"] = self.scan_value("0F 29 74 24 ?? F3 0F 10 B1 XX XX XX XX 75 07", "F3 0F 10 B1 XX XX XX XX A8 01 74 0C")

        self.offsets["room_width"] = self.scan_value("C7 41 XX 80 02 00 00 C7 41 ?? E0 01 00 00", "C7 41 XX 80 02 00 00 45 33 F6", "C7 41 XX 80 02 00 00 33 FF")
        self.offsets["room_height"] = self.offsets["room_width"] + 4
        self.offsets["room_persistent"] = self.offsets["room_width"] + 8

    def scan(self, pattern, signint=False):
        return self.memory.scanner.scan(pattern, module=(self.code_start, self.code_end), signint=signint)
    
    def scan_value(self, *patterns, default=0):
        for pattern in patterns:
            if not pattern: continue

            start, value = self.scan(pattern)
            if start is None or value is None: continue

            return value
        
        return default
    
    def scan_rel32(self, *patterns, default=0):
        for pattern in patterns:
            if not pattern: continue

            start, offset = self.scan(pattern, signint=True)
            if start is None or offset is None: continue

            pattern = pattern.replace(" ", "").lower()
            instpos = pattern.rfind("x")
            while (instpos + 1) < len(pattern) and pattern[instpos + 1] == "?": instpos += 1

            endofinst = ((instpos - 1) // 2) + 1

            return (start + endofinst + offset) - self.memory.base

        return default