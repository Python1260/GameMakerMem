SCRIPT_SAFE = "assets/gml/safescript.gml"
SCRIPT_BASE = "assets/gml/basescript.gml"
SCRIPT_INIT = "assets/gml/initscript.gml"

def read_script(path):
    with open(path) as file:
        content = file.read()
    
    return content

def get_script(content, **constants):
    for name, value in constants.items():
        content = content.replace(f"${name}$", str(value))
    
    return content

def get_safescript(code):
    content = read_script(SCRIPT_SAFE)
    content = get_script(content, CODE=code)

    return content

def get_basescript(code):
    content = read_script(SCRIPT_BASE)
    content = get_script(content, CODE=code)

    return content

def get_initscript(name, thresold):
    content = read_script(SCRIPT_INIT)
    content = get_script(content, NAME=name, THRESOLD=thresold)

    return content