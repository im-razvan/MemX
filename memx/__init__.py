"""
MemX Python Library
Made by im-razvan / Version 1.0.7
7 April 2024
"""

import platform

if platform.system() != 'Darwin':
   raise Exception("This library is only compatible with macOS (Darwin) systems.")

from .main import *