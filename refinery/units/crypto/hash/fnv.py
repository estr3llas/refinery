#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from refinery.units.crypto.hash import HashUnit, Arg

'''
Python impl for the Fowler–Noll–Vo hash function

References:
https://en.wikipedia.org/wiki/Fowler%E2%80%93Noll%E2%80%93Vo_hash_function
http://isthe.com/chongo/tech/comp/fnv/
'''

FNV_PRIME_32 = 0x01000193
FNV_PRIME_64 = 0x100000001b3

FNV_OFFSET_BASIS_32 = 0x811c9dc5
FNVA_OFFSET_BASIS_32 = FNV_OFFSET_BASIS_32
FNV_OFFSET_BASIS_64 = 0xcbf29ce484222325
FNVA_OFFSET_BASIS_64 = FNV_OFFSET_BASIS_64

class fnv(HashUnit):

    def _algorithm(data, fnv_prime, fnv_offset_basis, size):
        hash = fnv_offset_basis

        for byte in data:
            hash = (hash * fnv_prime) % size
            hash = hash ^ ord(byte)

        return hash
    
    def fnv32(self, data):
        return self._algorithm(data, FNV_PRIME_32, FNV_OFFSET_BASIS_32, 32)
    
    def fnv64(self, data):
        return self._algorithm(data, FNV_PRIME_64, FNV_OFFSET_BASIS_64, 64)

class fnva(HashUnit):

    def _algorithm(data, fnv_prime, fnv_offset_basis, size):
        hash = fnv_offset_basis

        for byte in data:
            '''
            The "A" variant inverts the  order of operations. This ivnersions leads to *slightly* better avalanche effects.
            '''
            hash = hash ^ ord(byte)
            hash = (hash * fnv_prime) % size

        return hash
    
    def fnva32(self, data):
        return self._algorithm(data, FNV_PRIME_32, FNVA_OFFSET_BASIS_32, 32)
    
    def fnva64(self, data):
        return self._algorithm(data, FNV_PRIME_64, FNVA_OFFSET_BASIS_64, 64)


fnv = fnv()