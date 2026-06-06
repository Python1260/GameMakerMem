from .classes import CRoom, CScript
from .structures import HashMap, ObjectBase
from .settings.types import *

class GlobalContext():
    def __init__(self, memory):
        self.memory = memory

        self.chunks = {}

        self.majorver = 0
        self.minorver = 0
        self.releasever = 0
        self.buildver = 0

    def init(self):
        self.chunks = self.get_chunks()

        detectedver = self.get_version()

        if "UILR" in self.chunks:
            detectedver = (2024, 13, 0, 0)
        elif "PSEM" in self.chunks:
            detectedver = (2023, 2, 0, 0)
        elif "FEAT" in self.chunks:
            detectedver = (2022, 8, 0, 0)
        elif "FEDS" in self.chunks:
            detectedver = (2, 3, 6, 0)
        elif "SEQN" in self.chunks:
            detectedver = (2, 3, 0, 0)
        elif "TGIN" in self.chunks:
            detectedver = (2, 2, 1, 0)

        self.majorver, self.minorver, self.releasever, self.buildver = detectedver
    
    def get_chunks(self):
        wad = self.memory.read_ptr(self.memory.base + self.memory.WADBase)
        wadend = self.memory.read_ptr(self.memory.base + self.memory.WADEnd)

        chunks = {}

        i = wad

        while i < wadend:
            chunk = self.memory.read_string(i, length=0x4)
            length = self.memory.read_int(i + 0x4)

            i += 0x8
            if chunk == "FORM":
                continue
        
            chunks[chunk] = i

            i += length
        
        return chunks
    
    def get_chunk_values(self, chunkname):
        wad = self.memory.read_ptr(self.memory.base + self.memory.WADBase)

        chunkaddr = self.chunks[chunkname]

        chunkvalues = []

        if chunkname in ("OBJT", "SPRT", "SOND", "ROOM", "BGND", "PATH", "SCPT", "FONT", "TMLN", "SHDR"):
            count = self.memory.read_int(chunkaddr)

            for j in range(count):
                offset = self.memory.read_int(chunkaddr + 0x4 + j * 0x4)
                pname = self.memory.read_int(wad + offset)

                string = self.memory.read_string(wad + pname)

                chunkvalues.append(string)
        elif chunkname in ("ACRV", "SEQN", "PSYS"):
            count = self.memory.read_int(chunkaddr + 0x4)

            for j in range(count):
                offset = self.memory.read_int(chunkaddr + 0x8 + j * 0x4)
                pname = self.memory.read_int(wad + offset)

                string = self.memory.read_string(wad + pname)

                chunkvalues.append(string)
        
        return chunkvalues

    def get_version(self):
        yyheader = self.memory.read_ptr(self.memory.base + self.memory.YYHeader)

        majorver = self.memory.read_int(yyheader + 0x2C)
        minorver = self.memory.read_int(yyheader + 0x30)
        releasever = self.memory.read_int(yyheader + 0x34)
        buildver = self.memory.read_int(yyheader + 0x38)

        return majorver, minorver, releasever, buildver
    
    def is_version_atleast(self, major, minor=0, release=0, build=0):
        if self.majorver != major:
            return self.majorver > major
        
        if self.minorver != minor:
            return self.minorver > minor
        
        if self.releasever != release:
            return self.releasever > release
        
        if self.buildver != build:
            return self.buildver > build
        
        return True
    
    def get_room(self):
        ptr = self.memory.read_ptr(self.memory.base + self.memory.RunRoom)
        return CRoom(self.memory, ptr)
    
    def get_roomref(self):
        ref = self.memory.read_int(self.memory.base + self.memory.CurrentRoom)
        return (REF_ROOM, ref)
    
    def get_fps(self):
        return self.memory.read_int(self.memory.base + self.memory.Fps)
    
    def get_globaltable(self):
        ptr = self.memory.read_ptr(self.memory.base + self.memory.GlobalTable)
        globaltable = ObjectBase(self.memory, ptr)

        globaltable.id = -5

        return globaltable

    def get_builtinvarlookup(self):
        ptr = self.memory.read_ptr(self.memory.base + self.memory.builtinVarLookup)
        return HashMap(self.memory, ptr)
    
    def get_instancevarlookup(self):
        ptr = self.memory.read_ptr(self.memory.base + self.memory.instanceVarLookup)
        return HashMap(self.memory, ptr)
    
    def get_thefunctions(self):
        funcs = {}

        the_functions = self.memory.read_ptr(self.memory.base + self.memory.the_functions)
        the_numb = self.memory.read_int(self.memory.base + self.memory.the_numb)

        doderef = self.memory.base < self.memory.read_ptr(the_functions + 0x0) < (self.memory.base + self.memory.size)

        for i in range(the_numb):
            ptr = the_functions + i * self.memory.the_functions_size
            name = self.memory.read_string(self.memory.read_ptr(ptr + 0x0) if doderef else ptr + 0x0)
            args = self.memory.read_int(ptr + self.memory.the_functions_size - 0x8)

            if args == 0xFFFFFFFF: args = -1

            if name:
                funcs[name] = (i, args)

        return funcs
    
    def get_refname(self, rtype):
        if self.memory.context.is_version_atleast(2023, 8):
            refs = self.memory.base + self.memory.name2ref

            for i in range(0x20):
                ptr = refs + i * 0x10

                r = self.memory.read_int(ptr + 0x8)

                if rtype == r:
                    name = self.memory.read_string(self.memory.read_ptr(ptr))
                    return name
        
        if rtype in NAME2REF:
            return NAME2REF[rtype]
        
        return "[undefined]"
    
    def get_assetname(self, rtype, rid):
        if rid == 0xFFFFFFFF: return "noone"
        if rid > 100000: return "instance"

        if rtype in CHUNK2REF:
            chunkname = CHUNK2REF[rtype]
            chunkvalues = self.get_chunk_values(chunkname)

            if rid < len(chunkvalues):
                return chunkvalues[rid]
            else:
                return "..."

        return str(rid)
    
    def get_codevariablename(self, k):
        variables = self.memory.executor.instance_variables

        for varname, varid in variables.items():
            if varid == k:
                return varname

        return "[unknown variable]"
    
    def get_gamecontext(self):
        wad = self.memory.read_ptr(self.memory.base + self.memory.WADBase)

        strings = []

        yystring = self.memory.read_ptr(self.memory.base + self.memory.YYString)
        yystringcount = self.memory.read_int(self.memory.base + self.memory.YYStringCount)

        for i in range(yystringcount):
            offset = self.memory.read_int(yystring + i * 0x4)
            length = self.memory.read_int(wad + offset + 0x0)
            string = self.memory.read_string(wad + offset + 0x4, length=length)

            strings.append(string)
        
        builtin_variables = self.get_builtinvarlookup().get_elements()
        gvcount = self.memory.read_int(self.memory.base + self.memory.StartGlobalVariables)
        variables = { vname: (vid, vid >= gvcount) for vname, vid in builtin_variables.items() }

        functions = self.get_thefunctions()
        
        instance_variables = self.get_instancevarlookup().get_elements()
        
        assets = []

        for chunkname in self.chunks.keys():
            chunkvalues = self.get_chunk_values(chunkname)

            for idx, chunkvalue in enumerate(chunkvalues):
                if chunkname == "SCPT":
                    chunkvalue = chunkvalue.removeprefix("gml_Script_")

                    if chunkvalue.startswith(("anon_", "___struct___", "____struct___")) or "gml_Object_" in chunkvalue:
                        continue

                asset = (chunkname, idx, chunkvalue)

                assets.append(asset)

        declaredfunctions = self.memory.read_int(self.memory.base + self.memory.ScriptMainNumber)

        return strings, variables, functions, instance_variables, assets, declaredfunctions
    
    def add_declaredfunction(self, name, ccode):
        declaredfunctions = self.memory.read_int(self.memory.base + self.memory.ScriptMainNumber)
        declaredfunctionarray = self.memory.read_ptr(self.memory.base + self.memory.ScriptMainItemsArray)
        declaredfunctionnames = self.memory.read_ptr(self.memory.base + self.memory.ScriptMainNames)

        cscriptaddress = self.memory.read_ptr(declaredfunctionarray + 0 * 0x8)
        cscript = CScript(self.memory, cscriptaddress)
        newcscript = cscript.copy()

        newcscript.set_name(name)
        newcscript.set_code(ccode)

        self.memory.write_ptr(declaredfunctionarray + declaredfunctions * 0x8, newcscript.address)
        self.memory.write_int(self.memory.base + self.memory.ScriptMainNumber, declaredfunctions + 1)
        self.memory.write_int(self.memory.base + self.memory.ScriptMainItemsArray - 0x8, declaredfunctions + 1)

        if not self.memory.context.is_version_atleast(2023, 8):
            newlength = len(name.encode("utf-8", errors="ignore"))
            newptr = self.memory.executor.allocate(newlength + 1)
            self.memory.write_string(newptr, name)

            self.memory.write_ptr(declaredfunctionnames + declaredfunctions * 0x8, newptr)

        return newcscript
    
    def add_string(self, name):
        wad = self.memory.read_ptr(self.memory.base + self.memory.WADBase)

        yystring = self.memory.read_ptr(self.memory.base + self.memory.YYString)
        yystringcount = self.memory.read_int(self.memory.base + self.memory.YYStringCount)

        newlength = len(name.encode("utf-8", errors="ignore"))
        newptr = self.memory.allocate(newlength + 5)

        offset = newptr - wad

        if offset < 0:
            tofree = []

            # IM SORRY!!!
            # it's better than reallocating the WAD though...
            while offset < 0:
                tofree.append(newptr)
                newptr = self.memory.allocate(newlength + 5)

                offset = newptr - wad
            
            for addr in tofree:
                self.memory.free(addr)
        
        self.memory.write_int(newptr + 0x0, newlength)
        self.memory.write_string(newptr + 0x4, name)

        self.memory.write_int(yystring + yystringcount * 0x4, offset)
        self.memory.write_int(self.memory.base + self.memory.YYStringCount, yystringcount + 1)
    
    def add_variable(self, name):
        num = self.memory.executor.CodeVariableFindSlot(0, name)

        return num

    def add_declaredfunctions(self, items):
        if len(items) == 0: return

        declaredfunctions = self.memory.read_int(self.memory.base + self.memory.ScriptMainNumber)
        declaredfunctionarray = self.memory.read_ptr(self.memory.base + self.memory.ScriptMainItemsArray)
        declaredfunctionnames = self.memory.read_ptr(self.memory.base + self.memory.ScriptMainNames)

        declaredfunctionarray = self.memory.executor.reallocate(declaredfunctionarray, (declaredfunctions + len(items)) * 0x8)
        self.memory.write_ptr(self.memory.base + self.memory.ScriptMainItemsArray, declaredfunctionarray)

        if not self.memory.context.is_version_atleast(2024):
            declaredfunctionnames = self.memory.executor.reallocate(declaredfunctionnames, (declaredfunctions + len(items)) * 0x8)
            self.memory.write_ptr(self.memory.base + self.memory.ScriptMainNames, declaredfunctionnames)

        for item in items:
            self.add_declaredfunction(*item)
        
        return declaredfunctions

    def add_strings(self, items):
        if len(items) == 0: return

        yystring = self.memory.read_ptr(self.memory.base + self.memory.YYString)
        yystringcount = self.memory.read_int(self.memory.base + self.memory.YYStringCount)

        yystring = self.memory.executor.reallocate(yystring, (yystringcount + len(items)) * 0x4)
        self.memory.write_ptr(self.memory.base + self.memory.YYString, yystring)
        
        for item in items:
            self.add_string(item)
        
        return yystringcount
    
    def add_variables(self, items):
        if len(items) == 0: return

        for item in items:
            self.add_variable(item)
    
    def room_goto(self, ref):
        self.memory.write_int(self.memory.base + self.memory.NewRoom, ref)

    def instance_destroy(self, instance):
        if not instance.get_flags(IFLAGS_DESTROYED):
            instance.set_flags(IFLAGS_DESTROYED, True)
            instance.set_flags(IFLAGS_DESTROY, True)

            self.memory.write_int(self.memory.base + self.memory.markedCount, self.memory.read_int(self.memory.base + self.memory.markedCount) + 1)

            if instance.get_deactive():
                self.memory.write_bool(self.memory.base + self.memory.DeactiveListDirty, True)
            else:
                self.memory.write_bool(self.memory.base + self.memory.ActiveListDirty, True)