"""
MemX Python Library
Made by im-razvan / Version 1.0
10 February 2024
"""

import ctypes
from psutil import process_iter
from struct import unpack, pack
from os import popen

libc = ctypes.CDLL(None)

def pid_for_pname(process_name):
    for proc in process_iter():
        if process_name == proc.name():
            return proc.pid
    return None

class MemX:
    def __init__(self, ProcessName: str): 
        self.pid = pid_for_pname(ProcessName)
        assert (self.pid is not None), "Couldn't find a running instance of %s" % ProcessName
        self.task = ctypes.c_uint32()
        self.mytask=libc.mach_task_self()
        ret=libc.task_for_pid(self.mytask, ctypes.c_int(self.pid), ctypes.pointer(self.task))
        if ret == 5: raise Exception("Please run this app with SUDO.")
        elif ret != 0 : raise Exception("Could not get task for pid %d" % self.pid)

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
        ret = libc.mach_vm_write(self.task, ctypes.c_ulonglong(address), data_buffer, data_len)
        if ret != 0:
            raise Exception("mach_vm_write returned : %s" % ret)

    # TODO: Find a normal way
    # It's working but eh
    def get_module_base(self, module):
        regs = popen(f"vmmap {self.pid} | grep __TEXT").read().split("\n")
        for reg in regs:
            if module in reg:
                r = int(reg.split("__TEXT")[1].split("-")[0], 16)
                return r