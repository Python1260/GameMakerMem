RunRoom = 0x8B2790
CurrentRoom = 0x8B27C8
NewRoom = 0x5F44D8
Fps = 0x8B27FC
builtinVarLookup = 0x67AFF8
instanceVarLookup = 0x8C1EE8
name2ref = 0x6E2710
ObjectHash = 0x69FA98
SpriteNames = 0x8B2178
RoomNames = 0x6A1C98
VarNamesInstanceArray = 0x5F4CF8
markedCount = 0x688820
DeactiveListDirty = 0x5F4AE4
ActiveListDirty = 0x5F4AE5

WADBase = 0x6A1DE8
YYString = 0x6A1E20
YYStringCount = 0x6A1D84
GameFileLength = 0x6A1D3C
GameFileBuffer = 0x6A1D78
ScriptMainNumber = 0x6A2E58
ScriptMainItemsArray = 0x6A2E68
ScriptMainItemsCount = 0x6A2E60
ScriptMainNames = 0x6A2E50
the_functions = 0x8C1E40
the_numb = 0x8C1E48
the_functions_size = 0x18
the_functions_deref = 0x1
the_functions_argnumb = 0x10

MemoryAlloc = 0x391150
NewCCode = 0x1BAA40
ExecuteIt = 0x1BB570
GlobalTable = 0x6A1D98
CodeVariableFindSlot = 0x1BF7D0

from .offsets_2022_1 import (
    croom_active,
    croom_deactive,

    cinstance_structvarsmap,

    image_index,
    image_speed,
    image_xscale,
    image_yscale,
    image_angle,
    image_alpha,
    image_blend,
    x,
    y,
    xstart,
    ystart,
    xprevious,
    yprevious,
    direction,
    speed,
    friction,
    gravity,
    hspeed,
    vspeed,
    depth,
    
    room_width,
    room_height,
    room_persistent
)