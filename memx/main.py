# main.py

import ctypes
from psutil import process_iter
from struct import unpack, pack
from re import search
from os import popen

libc = ctypes.CDLL(None)

VM_PROT_ALL = 0x07

def pid_for_pname(process_name):
    procs = []
    for proc in process_iter():
        if process_name == proc.name():
            procs.append(proc)
    if len(procs) == 1:
        return procs[0].pid
    elif len(procs)>1:
        print(f"[MemX] Found multiple processes named {process_name}:")
        i = 1
        for proc in procs:
            print(f"    {i}. PID: {proc.pid}, APP: {proc.exe()}")
            i += 1
        return procs[int(input("[MemX] Enter your choice: ")) - 1].pid
    return None        

class Process:
    def __init__(self, ProcessName: str): 
        self.pid = pid_for_pname(ProcessName)
        self.TEXT = []
        assert (self.pid is not None), "Couldn't find a running instance of %s" % ProcessName
        self.task = ctypes.c_uint32()
        self.mytask=libc.mach_task_self()
        ret=libc.task_for_pid(self.mytask, ctypes.c_int(self.pid), ctypes.pointer(self.task))
        if ret == 5: raise Exception("Please run this app with SUDO.")
        elif ret != 0 : raise Exception("Could not get task for pid %d" % self.pid)

    def read_short(self, address):
        return unpack('h', self.read_bytes(address, 2))[0]
    
    def read_ushort(self, address):
        return unpack('H', self.read_bytes(address, 2))[0]

    def read_int(self, address):
        return unpack('i', self.read_bytes(address, 4))[0]

    def read_uint(self, address):
        return unpack('I', self.read_bytes(address, 4))[0]
    
    def read_long(self, address):
        return unpack('l', self.read_bytes(address, 4))[0]

    def read_ulong(self, address):
        return unpack('L', self.read_bytes(address, 4))[0]
    
    def read_float(self, address):
        return unpack('f', self.read_bytes(address, 4))[0]
    
    def read_double(self, address):
        return unpack('d', self.read_bytes(address, 8))[0]

    def read_longlong(self, address):
        return unpack('q', self.read_bytes(address, 8))[0]
    
    def read_ulonglong(self, address):
        return unpack('Q', self.read_bytes(address, 8))[0]
    
    def read_vec2f(self, address) -> tuple:
        return unpack('ff', self.read_bytes(address, 8))
    
    def read_vec3f(self, address) -> tuple:
        return unpack('fff', self.read_bytes(address, 12))

    def write_short(self, address, value):
        self.write_bytes(address, pack('h', value))
        
    def write_ushort(self, address, value):
        self.write_bytes(address, pack('H', value))

    def write_int(self, address, value):
        self.write_bytes(address, pack('i', value))
        
    def write_uint(self, address, value):
        self.write_bytes(address, pack('I', value))

    def write_long(self, address, value):
        self.write_bytes(address, pack('l', value))

    def write_ulong(self, address, value):
        self.write_bytes(address, pack('L', value))

    def write_float(self, address, value):
        self.write_bytes(address, pack('f', value))

    def write_double(self, address, value):
        self.write_bytes(address, pack('d', value))

    def write_longlong(self, address, value):
        self.write_bytes(address, pack('q', value))

    def write_ulonglong(self, address, value):
        self.write_bytes(address, pack('Q', value))

    def write_vec2f(self, address, value):
        self.write_bytes(address, pack('ff', value))

    def write_vec3f(self, address, value):
        self.write_bytes(address, pack('fff', value))

    def read_bytes(self, address, bytes):
        pdata = ctypes.c_void_p(0)
        data_cnt = ctypes.c_uint32(0)
        res = libc.mach_vm_read(self.task, ctypes.c_ulonglong(address), ctypes.c_longlong(bytes), ctypes.pointer(pdata), ctypes.pointer(data_cnt))
        if res != 0:
            raise Exception("mach_vm_read returned : %s"%res)
        rbuf=ctypes.string_at(pdata.value, data_cnt.value)
        libc.vm_deallocate(self.mytask, pdata, data_cnt)
        return rbuf
    
    def write_bytes(self, address, data):
        data_buffer = ctypes.create_string_buffer(data)
        data_len = ctypes.c_ulonglong(len(data))
        libc.mach_vm_protect(self.task, ctypes.c_ulonglong(address), data_len,ctypes.c_bool(False), ctypes.c_int(VM_PROT_ALL))
        res = libc.mach_vm_write(self.task, ctypes.c_ulonglong(address), data_buffer, data_len)
        if res != 0:
            raise Exception("mach_vm_write returned : %s" % res)

    # This was added to speed up the module getting
    def fetch_modules(self):
        regs = popen(f"vmmap {self.pid} | grep __TEXT").read().split("\n")
        self.TEXT = []
        for reg in regs:
            if "__TEXT" in reg:
                self.TEXT.append(reg)

class Module:
    # TODO: Find a normal & faster way
    def __init__(self, Process: Process, ModuleName: str):
        self.proc = Process
        if not self.proc.TEXT:
            raise Exception("Please use fetch_modules() first.")
        self.BaseAddress = None
        self.Size = None
        for reg in self.proc.TEXT:
            if ModuleName in reg:
                ax = reg.split("__TEXT")[1].split("-")
                self.BaseAddress = int(ax[0], 16)
                self.Size = int(ax[1].split(" ")[0], 16) - self.BaseAddress
                break

    def search_IDA_pattern(self, ida_pattern: str):
        re_format = bytes.fromhex(ida_pattern.replace("?", "2E"))
        return self.search_pattern(re_format)

    def search_pattern(self, pattern: bytes):
        moduleBytes = self.proc.read_bytes(self.BaseAddress, self.Size)
        s = search(pattern, moduleBytes)
        if s != None:
            return self.BaseAddress + s.start()
        return None