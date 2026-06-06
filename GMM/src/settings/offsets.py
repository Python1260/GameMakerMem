import os
import json

OFFSETS = {}

def get_offset(version, name):
    return OFFSETS.get(version, {}).get(name, 0x0)

def has_offsets(version):
    if not version in OFFSETS: return False

    offsets = OFFSETS[version]

    return all(offset != 0 for offset in offsets.values())

def offsets_to_file(filename, offsets):
    module_name = os.path.splitext(os.path.basename(filename))[0]

    offsets["Version"] = module_name

    with open(filename, "w") as file:
        try:
            json.dump(offsets, file, indent=4)
        except:
            pass

def offsets_from_file(filename):
    module_name = os.path.splitext(os.path.basename(filename))[0]

    with open(filename) as file:
        try:
            OFFSETS[module_name] = json.load(file)
        except:
            pass

##### HOW TO FIND OFFSETS USING STRINGS (OUTDATED) #####
# RunRoom =                 layer_get_id() - wrong number of arguments
# CurrentRoom =             %sFATAL ERROR in Room Creation Code for room %s\n\n\n%s\n
# NewRoom =                 room_goto
# Fps =                     Entering main loop.\n
# builtinVarLookup =        variable_instance_get
# instanceVarLookup =       <unknown variable>
# ObjectHash =              object_get_name
# SpriteNames =             sprite_get_name
# RoomNames =               room_get_name
# VarNamesInstanceArray =   <unknown variable>
# markedCount =             instance_destroy
# DeactiveListDirty =       instance_destroy
# ActiveListDirty =         instance_destroy

# WADBase =                 Process Chunk: %s   %u  (%4.2fMB)\n
# YYHeader =                Process Chunk: %s   %u  (%4.2fMB)\n -> case 0x384E4547, qword assigned to a1
# YYString =                ID_STRG\n -> the qword
# YYStringCount =           ID_STRG\n -> the dword
# GameFileLength =          initialise everything! -> xrefs -> the dword
# GameFileBuffer =          initialise everything! -> xrefs -> the qword
# ScriptMainNumber =        Script_Free called with %d and global %d\n
# ScriptMainItemsArray =    Script_Free called with %d and global %d\n
# ScriptMainItemsCount =    Script_Free called with %d and global %d\n -> or just array - 0x8
# ScriptMainNames =         Script_Free called with %d and global %d\n
# the_functions =           show_message -> caller -> qword, used a lot
# the_numb =                show_message -> caller -> dword, assigned to itself + 1

# MemoryAlloc =             COMPILATION ERROR in Script: %s\n%s -> called with argument 0xB8
# NewCCode =                COMPILATION ERROR in Script: %s\n%s -> ternary operator, called with arg1, arg2, 0
# ExecuteIt =               COMPILATION ERROR in Script: %s\n%s -> called with the same qword two times as arg
# GlobalTable =             COMPILATION ERROR in Script: %s\n%s -> used two times in ExecuteIt
# CodeVariableFindSlot =    longMessage -> go to call -> first call

# croom_active =            instance_place
# croom_deactive =          -> croom_active + 0x18
# cinstance_structvarsmap = variable_instance_get_names

# ALL INSTANCE (OR ROOM) RELATED OFFSETS ARE STORED IN THEIR GETTER FUNCTIONS (x, y, ...)