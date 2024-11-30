#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#from refinery.units.crypto.hash import HashUnit, Arg

'''
Python impl for the Fowler–Noll–Vo hash function

References:
https://en.wikipedia.org/wiki/Fowler%E2%80%93Noll%E2%80%93Vo_hash_function
http://isthe.com/chongo/tech/comp/fnv/
'''

FNV_PRIME_32 = 16777619
FNV_OFFSET_BASIS_32 = 2166136261
FNVA_OFFSET_BASIS_32 = FNV_OFFSET_BASIS_32

FNV_PRIME_64 = 1099511628211
FNV_OFFSET_BASIS_64 = 14695981039346656037
FNVA_OFFSET_BASIS_64 = FNV_OFFSET_BASIS_64

class fnv():

    def _algorithm(self, data, fnv_prime, fnv_offset_basis, size):
        hash = fnv_offset_basis

        if isinstance(data, str):
            data = data.encode('utf-8')

        assert isinstance(data, bytes)

        for byte in data:
            hash = (hash * fnv_prime) % (2**size)
            hash = hash ^ byte

        return hash
    
    def fnv32(self, data):
        return self._algorithm(data, FNV_PRIME_32, FNV_OFFSET_BASIS_32, 32)
    
    def fnv64(self, data):
        return self._algorithm(data, FNV_PRIME_64, FNV_OFFSET_BASIS_64, 64)

class fnva():

    def _algorithm(self, data, fnv_prime, fnv_offset_basis, size):
        hash = fnv_offset_basis

        if isinstance(data, str):
            data = data.encode('utf-8')

        assert isinstance(data, bytes)

        for byte in data:
            '''
            The "A" variant inverts the  order of operations. This ivnersions leads to *slightly* better avalanche effects.
            '''
            hash = hash ^ byte
            hash = (hash * fnv_prime) % (2**size)

        return hash
    
    def fnva32(self, data):
        return self._algorithm(data, FNV_PRIME_32, FNVA_OFFSET_BASIS_32, 32)
    
    def fnva64(self, data):
        return self._algorithm(data, FNV_PRIME_64, FNVA_OFFSET_BASIS_64, 64)
    