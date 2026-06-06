from .compiler import Compiler
from .shellcode import ShellcodeHandler
from . import functions
from ..structures import RValue
from ..classes import CCode

class Executor():
    def __init__(self, memory):
        self.memory = memory

        self.compiler = Compiler()
        self.shellcodehandler = ShellcodeHandler(self.memory)

        self.strings = []
        self.variables = {}
        self.functions = {}
        self.instance_variables = {}
        self.assets = []
        self.declaredfunctions = 0
    
    def __getattr__(self, name):
        func = self.get_function(name)

        return lambda *args, return_type=int, freeparsed=True : self.call(func, *args, return_type=return_type, freeparsed=freeparsed)
    
    def init(self, strings=None, variables=None, functions=None, instance_variables=None, assets=None, declaredfunctions=None):
        if strings is None: strings = self.strings
        if variables is None: variables = self.variables
        if functions is None: functions = self.functions
        if instance_variables is None: instance_variables = self.instance_variables
        if assets is None: assets = self.assets
        if declaredfunctions is None: declaredfunctions = self.declaredfunctions

        self.strings = strings
        self.variables = variables
        self.functions = functions
        self.instance_variables = instance_variables
        self.assets = assets
        self.declaredfunctions = declaredfunctions

        def gcfilter(game_context):
            game_context.UsingGMLv2 = self.memory.context.is_version_atleast(2, 3)
            game_context.Bytecode14OrLower = not self.memory.context.is_version_atleast(2)
            game_context.UsingGMS2OrLater = self.memory.context.is_version_atleast(2)
            game_context.UsingStringRealOptimizations = self.memory.context.is_version_atleast(2)
            game_context.UsingFinallyBeforeThrow = not self.memory.context.is_version_atleast(2024, 6)
            game_context.UsingTypedBooleans = self.memory.context.is_version_atleast(2, 3, 7)
            game_context.UsingNullishOperator = self.memory.context.is_version_atleast(2, 3, 7) 
            game_context.UsingAssetReferences = self.memory.context.is_version_atleast(2023, 8)
            game_context.UsingRoomInstanceReferences = self.memory.context.is_version_atleast(2024, 2) 
            game_context.UsingFunctionScriptReferences = self.memory.context.is_version_atleast(2024, 2) 
            game_context.UsingNewFunctionResolution = self.memory.context.is_version_atleast(2024, 13) 
            game_context.UsingLongCompoundBitwise = self.memory.context.is_version_atleast(2, 3, 2) 
            game_context.UsingExtraRepeatInstruction = not self.memory.context.is_version_atleast(2022, 11)
            game_context.UsingConstructorSetStatic = self.memory.context.is_version_atleast(2024, 11) 
            game_context.UsingReentrantStatic = not self.memory.context.is_version_atleast(2024, 11)
            game_context.UsingNewFunctionVariables = self.memory.context.is_version_atleast(2024, 2) 
            game_context.UsingSelfToBuiltin = self.memory.context.is_version_atleast(2024, 2) 
            game_context.UsingGlobalConstantFunction = self.memory.context.is_version_atleast(2023, 11) 
            game_context.UsingObjectFunctionForesight = self.memory.context.is_version_atleast(2024, 11) 
            game_context.UsingBetterTryBreakContinue = self.memory.context.is_version_atleast(2024, 11) 
            game_context.UsingBuiltinDefaultArguments = self.memory.context.is_version_atleast(2024, 11) 
            game_context.UsingNewArrayOwners = self.memory.context.is_version_atleast(2, 3, 2) 
            game_context.UsingOptimizedFunctionDeclarations = self.memory.context.is_version_atleast(2024, 14)
            game_context.UsingNewChainedFunctionArgumentOrder = self.memory.context.is_version_atleast(2024, 14, 4)

        self.compiler.init(strings=strings, variables=variables, functions=functions, instance_variables=instance_variables, assets=assets, declaredfunctions=declaredfunctions, gcfilter=gcfilter)
    
    def get_function(self, name):
        return functions.get_function(self.memory, name)

    def call(self, func, *args, return_type=int, freeparsed=True):
        if not func:
            return None
        
        self.shellcodehandler.begin()
        self.shellcodehandler.instr_call(func, *args)
        self.shellcodehandler.instr_release()
        self.shellcodehandler.instr_return()
        
        address = self.shellcodehandler.submit()
        self.memory.thread(address)

        result = self.shellcodehandler.wait(return_type=return_type, freeparsed=freeparsed)

        return result

    def allocate(self, size):
        return self.MemoryAlloc(size, True, 0, 1)
    
    def allocate_structure(self, size, name):
        address = self.allocate(size)

        self.memory.write_ptr(address, self.memory.base + getattr(self.memory, f"_vftable__{name}"))

        return address
    
    def reallocate(self, address, size):
        if not address:
            return self.allocate(size)
        
        data = self.memory.read_bytes(address, size)
        newaddress = self.allocate(size)
        self.memory.write_bytes(newaddress, data)

        return newaddress
    
    def execute(self, gml):
        success, data = self.compiler.compile(gml)

        if not success:
            return 1, data
        
        bytecode, subnodes, stringids, variableids = data

        address = self.allocate(0xB8)
        ccode = CCode(self.memory, self.NewCCode(address, 0, 0))

        globaltable = self.memory.context.get_globaltable()

        result = RValue.new(self.memory, None)
        result.set_value(None)

        ccode.set_bytecode(bytecode)
        ccode.set_func(0x0) # to make this actually work with YYC
        ccode.locals = 1
        ccode.args = 0
        ccode.offset = 0

        newdeclaredfunctions = []

        for node in subnodes:
            subaddress = self.allocate(0xB8)
            subccode = CCode(self.memory, self.NewCCode(subaddress, 0, 0))

            name, sl, sa, so = node

            subccode.set_bytecode(bytecode)
            subccode.locals = sl
            subccode.args = sa
            subccode.offset = so

            newdeclaredfunctions.append((name, subccode))

        self.memory.context.add_declaredfunctions(newdeclaredfunctions)

        newstrings = []
        
        for string in stringids:
            self.strings.append(string)

            newstrings.append(string)

        self.memory.context.add_strings(newstrings)

        newvariables = []
        
        for variable in variableids:
            self.instance_variables[variable] = 100000 + len(self.instance_variables)

            newvariables.append(variable)

        self.memory.context.add_variables(newvariables)

        status = self.ExecuteIt(globaltable, globaltable, ccode, result, 0)
        resultvalue = result.get_value()

        result.destroy()

        if status < 1:
            return 2, resultvalue

        return 0, resultvalue