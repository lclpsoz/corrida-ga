import sys, platform
import ctypes, ctypes.util

collisions = True
try:
    col = ctypes.CDLL("./collisions.so")
    print("Collisions.so loaded!")
except OSError:
    collisions = False
    print("Unable to load collisions.so.")

if collisions:
    col_circuit_ellipse = col.col_circuit_ellipse
    col_circuit_ellipse.argtypes = [ctypes.POINTER(ctypes.c_float),
                                    ctypes.POINTER(ctypes.c_float),
                                    ctypes.POINTER(ctypes.c_float),
                                    ctypes.POINTER(ctypes.c_float),
                                    ctypes.POINTER(ctypes.c_float),
                                    ctypes.c_float,
                                    ctypes.c_float,
                                    ctypes.c_int]
    col_circuit_ellipse.restype = ctypes.POINTER(ctypes.c_int)