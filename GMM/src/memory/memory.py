import pymem
import psutil
import ctypes
from ctypes import wintypes
import threading

from .scanner import Scanner
from ..globalcontext import GlobalContext
from ..executor import Executor
from ..settings.offsets import get_offset, has_offsets

kernel32 = ctypes.windll.kernel32

class Memory():
    def __init__(self, app, name=""):
        self.app = app
        
        self.scanner = Scanner(self)
        self.context = GlobalContext(self)
        self.executor = Executor(self)

        self.detached_callback = None

        self.name = name
        self.version = "0"
        self.process = None
        
        self.module = None
        
        self.pid = 0
        self.handle = None
        self.base = 0x0

    def __getattr__(self, name):
        return get_offset(self.version, name)
    
    def __bool__(self):
        return has_offsets(self.version)

    def attach(self, name=None):
        if name is not None: self.name = name

        try:
            process = pymem.Pymem(self.name)
        except:
            if self.process == None:
                return False

            self.process = None

            return True
        else:
            if self.process and process.process_id == self.process.process_id:
                process.close_process()
                return False
            
            self.process = process

            self.module = self.process.process_base

            self.pid = self.process.process_id
            self.handle = self.process.process_handle
            self.base = self.process.base_address

            self.version = self.scanner.get_version()

            if self.detached_callback:
                def worker(handle=self.handle, callback=self.detached_callback):
                    kernel32.WaitForSingleObject(handle, 0xFFFFFFFF)
                    callback()
                
                threading.Thread(target=worker, daemon=True).start()

            return True
    
    def attached(self):
        return self.process is not None and psutil.pid_exists(self.pid)
    
    def detach(self):
        self.process.close_process()
        self.process = None
    
    def on_detached(self, callback):
        self.detached_callback = callback
    
    def is_version_atleast(self, major, minor=0, release=0, build=0):
        elements = self.version.split(".")

        majorver = int(elements[0])
        minorver = int(elements[1]) if len(elements) > 1 else 0
        releasever = int(elements[2]) if len(elements) > 2 else 0
        buildver = int(elements[3]) if len(elements) > 3 else 0

        if majorver != major:
            return majorver > major
        
        if minorver != minor:
            return minorver > minor
        
        if releasever != release:
            return releasever > release
        
        if buildver != build:
            return buildver > build
        
        return True
    
    def allocate(self, size):
        try:
            return self.process.allocate(size)
        except:
            return 0x0
    
    def free(self, address):
        try:
            return self.process.free(address)
        except:
            return False
        
    def thread(self, address):
        try:
            return self.process.start_thread(address)
        except:
            return None
    
    def read_bytes(self, address, length):
        try:
            return self.process.read_bytes(address, length)
        except Exception as e:
            return b""
    
    def write_bytes(self, address, value):
        try:
            self.process.write_bytes(address, value, len(value))
            return True
        except:
            return False
    
    def read_string(self, address, length=0x100):
        try:
            value = self.process.read_bytes(address, length)
        except Exception as e:
            return ""
        
        end = value.find(b"\x00")
        if end != -1: value = value[:end]

        return value.decode("utf-8", errors="ignore")
    
    def write_string(self, address, value):
        value = value.encode("utf-8", errors="ignore")
        value += b"\x00"

        try:
            self.process.write_bytes(address, value, len(value))
            return True
        except:
            return False
    
    def read_ptr(self, address):
        try:
            return self.process.read_ulonglong(address)
        except:
            return 0x0
    
    def write_ptr(self, address, value):
        try:
            self.process.write_ulonglong(address, int(value))
            return True
        except:
            return False
    
    def read_number(self, address):
        return self.read_ptr(address)
    
    def write_number(self, address, value):
        return self.write_ptr(address, value)
        
    def read_int(self, address):
        try:
            return self.process.read_uint(address)
        except:
            return 0x0
    
    def write_int(self, address, value):
        try:
            self.process.write_uint(address, int(value))
            return True
        except:
            return False
    
    def read_short(self, address):
        try:
            return self.process.read_ushort(address)
        except:
            return 0x0
    
    def write_short(self, address, value):
        try:
            self.process.write_ushort(address, int(value))
            return True
        except:
            return False
    
    def read_char(self, address):
        try:
            return self.process.read_uchar(address)
        except:
            return 0x0
    
    def write_char(self, address, value):
        try:
            self.process.write_uchar(address, int(value))
            return True
        except:
            return False
    
    def read_bool(self, address):
        try:
            return self.process.read_bool(address)
        except:
            return False
    
    def write_bool(self, address, value):
        try:
            self.process.write_bool(address, bool(value))
            return True
        except:
            return False
        
    def read_float(self, address):
        try:
            return self.process.read_float(address)
        except:
            return 0.0
    
    def write_float(self, address, value):
        try:
            self.process.write_float(address, float(value))
            return True
        except:
            return False
    
    def read_double(self, address):
        try:
            return self.process.read_double(address)
        except:
            return 0.0
    
    def write_double(self, address, value):
        try:
            self.process.write_double(address, float(value))
            return True
        except:
            return False