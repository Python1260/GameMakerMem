from .classes import CRoom, CScript
from .structures import HashMap
from .settings.types import *

class GlobalContext():
    def __init__(self, memory):
        self.memory = memory
    
    def get_room(self):
        ptr = self.memory.read_ptr(self.memory.base + self.memory.RunRoom)
        return CRoom(self.memory, ptr)
    
    def get_roomref(self):
        ref = self.memory.read_int(self.memory.base + self.memory.CurrentRoom)
        return (REF_ROOM, ref)
    
    def get_fps(self):
        return self.memory.read_int(self.memory.base + self.memory.Fps)

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

        for i in range(the_numb):
            ptr = the_functions + i * self.memory.the_functions_size
            name = self.memory.read_string(self.memory.read_ptr(ptr + 0x0) if self.memory.the_functions_deref else ptr + 0x0)
            args = self.memory.read_int(ptr + self.memory.the_functions_argnumb)

            if args == 0xFFFFFFFF: args = -1

            if name:
                funcs[name] = (i, args)

        return funcs
    
    def get_refname(self, rtype):
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
        
        name = str(rid)

        if rtype == REF_OBJECT:
            ptr = self.memory.read_ptr(self.memory.base + self.memory.ObjectHash)
            elements = self.memory.read_ptr(ptr + 0x0)
            mask = self.memory.read_int(ptr + 0x8)

            link = elements + (rid & mask) * 0x10
            node = self.memory.read_ptr(link + 0x0)

            while node:
                mid = self.memory.read_int(node + 0x10)

                if mid == rid:
                    mobj = self.memory.read_ptr(node + 0x18)
                    name = self.memory.read_string(self.memory.read_ptr(mobj + 0x0))
                    break

                node = self.memory.read_ptr(node + 0x8)
        else:
            ptr = None

            if rtype == REF_SPRITE:
                ptr = self.memory.read_ptr(self.memory.base + self.memory.SpriteNames)
            elif rtype == REF_ROOM:
                ptr = self.memory.read_ptr(self.memory.base + self.memory.RoomNames)

            if ptr is not None:
                mobj = ptr + rid * 0x8
                name = self.memory.read_string(self.memory.read_ptr(mobj + 0x0))

        
        if name == "": name = "..."

        return name
    
    def get_codevariablename(self, k):
        array = self.memory.read_ptr(self.memory.base + self.memory.VarNamesInstanceArray)

        objind = k - 100000
        if objind < 0: return "[undefined]"

        ptr = array + objind * 0x8
        name = self.memory.read_string(self.memory.read_ptr(ptr))

        return name
    
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
        
        variables = self.get_builtinvarlookup().get_elements()
        functions = self.get_thefunctions()
        
        instance_variables = self.get_instancevarlookup().get_elements()
        
        assets = []

        gamefilelength = self.memory.read_int(self.memory.base + self.memory.GameFileLength)
        gamefilebuffer = self.memory.read_ptr(self.memory.base + self.memory.GameFileBuffer)

        i = 0

        while i < gamefilelength:
            chunk = self.memory.read_string(gamefilebuffer + i, length=0x4)
            length = self.memory.read_int(gamefilebuffer + i + 0x4)

            i += 0x8
            if chunk == "FORM":
                continue

            if chunk in ("OBJT", "SPRT", "SOND", "ROOM", "BGND", "PATH", "SCPT", "FONT", "TMLN", "SHDR"):
                count = self.memory.read_int(gamefilebuffer + i)

                for j in range(count):
                    offset = self.memory.read_int(gamefilebuffer + i + 0x4 + j * 0x4)
                    pname = self.memory.read_int(wad + offset)
                    if not pname: continue

                    string = self.memory.read_string(wad + pname)

                    assets.append((chunk, j, string))
            elif chunk in ("ACRV", "SEQN", "PSYS"):
                count = self.memory.read_int(gamefilebuffer + i + 0x4)

                for j in range(count):
                    offset = self.memory.read_int(gamefilebuffer + i + 0x8 + j * 0x4)
                    pname = self.memory.read_int(wad + offset)
                    if not pname: continue

                    string = self.memory.read_string(wad + pname)

                    assets.append((chunk, j, string))

            i += length

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
        self.memory.write_int(self.memory.base + self.memory.ScriptMainItemsCount, declaredfunctions + 1)

        if self.memory.ScriptMainNames:
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

        if self.memory.ScriptMainNames:
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