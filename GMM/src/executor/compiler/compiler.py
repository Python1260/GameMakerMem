from pythonnet import load
import platform

load("coreclr")

import os
import sys
import clr

sys.path.append(os.path.dirname(__file__))
clr.AddReference("Underanalyzer")

from Underanalyzer.Mock import GameContextMock # type: ignore
from Underanalyzer import AssetType # type: ignore

CHUNK2ASSET = {
    "OBJT": AssetType.Object,
    "SPRT": AssetType.Sprite,
    "SOND": AssetType.Sound,
    "ROOM": AssetType.Room,
    "BGND": AssetType.Background,
    "PATH": AssetType.Path,
    "SCPT": AssetType.Script,
    "FONT": AssetType.Font,
    "TMLN": AssetType.Timeline,
    "SHDR": AssetType.Shader,
    "SEQN": AssetType.Sequence,
    "ACRV": AssetType.AnimCurve,
    "PSYS": AssetType.ParticleSystem
}

def getfromfile(filename):
    with open(filename) as file:
        return [pair.split("=") for pair in file.read().split("\n")]

class Compiler():
    def __init__(self):
        self.game_context = None

        self.constants_values = getfromfile("assets/data/constants.txt")
        
        self.init()
    
    def init(self, strings=[], variables={}, functions={}, instance_variables={}, assets=[], declaredfunctions=0, gcfilter=lambda gc : gc):
        self.game_context = GameContextMock()
        
        gcfilter(self.game_context)

        self.init_constants(self.constants_values)

        for idx, string in enumerate(strings):
            self.game_context.DefineString(string, idx)
        
        for name, data in variables.items():
            self.game_context.DefineBuiltinVariable(name, data[0], True, data[1])
        
        for name, data in functions.items():
            self.game_context.DefineBuiltinFunction(name, data[0], data[1])
        
        for name, idx in instance_variables.items():
            self.game_context.DefineInstanceVariable(name, idx)

        for idx, asset in enumerate(assets):
            if asset[0] == "SCPT":
                self.game_context.DefineGlobalFunction(asset[2], 100000 + asset[1])
            else:
                self.game_context.DefineMockAsset(CHUNK2ASSET[asset[0]], asset[1], asset[2])
        
        self.game_context.CodeBuilder.DeclaredFunctions = declaredfunctions
    
    def init_constants(self, constants={}):
        for name, value in constants:
            if name == "os_type":
                os_name = platform.system()
                value = { "Windows": "0.0", "Darwin": "1.0", "Linux": "6.0" }.get(os_name, "0.0")

            self.game_context.DefineConstant(name, float(value))
    
    def compile(self, code, isglobal=False):
        code = 'var _ = function() { try { ' + code + ' } catch (error) { var d = [error.message, error.longMessage, error.script, error.line, error.stacktrace]; show_message("An error occurred while executing GML: " + error.message); } }; call_later(0, 0, _);'

        prevslen = len(dict(self.game_context.GetStrings()))
        prevvlen = len(dict(self.game_context.GetInstanceVariables()))

        try:
            root = self.game_context.CompileCode(code, isglobal)

            bytecode = bytes(root.Serialize(self.game_context))
            subnodes = [(node.Name.Content, node.LocalCount, node.ArgumentCount, node.StartOffset) for node in reversed(root.Children)]
        except Exception as error:
            cerrors = list(self.game_context.CompileContext.Errors)

            return False, [cerror.GenerateMessage() for cerror in cerrors] if len(cerrors) > 0 else [error]
        else:
            newstrings = dict(self.game_context.GetStrings())
            stringids = []

            if len(newstrings) > prevslen:
                stringids = list(newstrings.keys())[prevslen:len(newstrings)]
            
            newvariables = dict(self.game_context.GetInstanceVariables())
            variableids = []

            if len(newvariables) > prevvlen:
                variableids = list(newvariables.keys())[prevvlen:len(newvariables)]

            return True, (bytecode, subnodes, stringids, variableids)