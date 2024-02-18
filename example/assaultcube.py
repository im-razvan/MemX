# Simple program that reads the localplayer health value from AsC
from MemX import *

mx = Process("assaultcube")
base = Module(mx, "assaultcube").BaseAddress

s = mx.read_longlong(base + 0x1D9EF0)
healthAddr = mx.read_longlong(s) + 0x418

print(f"Health value: {mx.read_int(healthAddr)}")