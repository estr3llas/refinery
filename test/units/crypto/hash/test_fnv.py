#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from ... import TestUnitBase
from refinery.units.crypto.hash.fnv import *

class TestChecksums(TestUnitBase):

    def test_fnv32(self):
        hasher = fnv()

        self.assertEquals(hasher.fnv32('binary-refinery'), '357438799')

    def test_fnv64(self):
        hasher = fnv()

        self.assertEquals(hasher.fnv64('binary-refinery'), '3965962077988312367')

    def test_fnva32(self):
        hasher = fnva()

        self.assertEquals(hasher.fnva32('binary-refinery'), '518774507')

    def test_fnva64(self):
        hasher = fnva()

        self.assertEquals(hasher.fnva64('binary-refinery'), '7537022231269251275')