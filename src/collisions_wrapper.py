import sys, platform
import ctypes, ctypes.util

collisions = True
try:
    col = ctypes.CDLL("src/collisions.so")
    print("Collisions.so loaded!")
except OSError:
    collisions = False
    print("Unable to load collisions.so.")

if collisions:
    # Collision for circuit
    col_circuit = col.col_circuit
    col_circuit.argtypes = [ ctypes.POINTER(ctypes.c_float),
                                    ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_float),
                                    ctypes.c_int]
    col_circuit.restype = ctypes.POINTER(ctypes.c_int)
    
    # Collision distance for  circuit
    col_dist_circuit = col.col_dist_circuit
    col_dist_circuit.argtypes = [   ctypes.POINTER(ctypes.c_float),
                                    ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_float),
                                    ctypes.c_int]
    col_dist_circuit.restype = ctypes.POINTER(ctypes.c_float)

    # Free memory of array
    freeme = col.freeme
    freeme.argtypes = ctypes.c_void_p,
    freeme.ret = None

    # Free memory of N arrays
    freeme_n = col.freeme_n
    freeme_n.argtypes = [ctypes.c_void_p, ctypes.c_int]
    freeme_n.ret = None