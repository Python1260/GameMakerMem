import ctypes

kernel32 = ctypes.windll.kernel32
user32 = ctypes.windll.user32
ntdll = ctypes.windll.ntdll

def get_function(memory, name):
    offset = getattr(memory, name)

    if offset:
        return memory.base + offset
    
    for dll in [kernel32, user32, ntdll]:
        if hasattr(dll, name):
            func = getattr(dll, name)
            address = ctypes.cast(func, ctypes.c_void_p).value

            return address
    
    return 0x0