#  MemX
## A Python Library to Manipulate macOS Processes.
---
### Example usage:
```
from memx import *

mx = Process("assaultcube")
mx.fetch_modules()
base = Module(mx, "assaultcube").BaseAddress

s = mx.read_longlong(base + 0x1D9EF0)
healthAddr = mx.read_longlong(s) + 0x418

print(f"Health value: {mx.read_int(healthAddr)}")
```
This program reads the health value from a process named `assaultcube`.