#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from ... import TestUnitBase
from refinery.units.crypto.hash.fnv import *

class TestChecksums(TestUnitBase):

    def test_fnv32(self):
        data = B'binary-refinery'
        self.assertEquals(fnv.fnv32(bytes(data)), bytes.fromhex('357438799'))

    def test_fnv64(self):
        data = B'binary-refinery'
        self.assertEquals(fnv.fnv64(bytes(data)), bytes.fromhex('3965962077988312367'))

    def test_fnva32(self):
        data = B'binary-refinery'
        self.assertEquals(fnva.fnva32(bytes(data)), bytes.fromhex('518774507'))

    def test_fnva64(self):
        data = B'binary-refinery'
        self.assertEquals(fnva.fnva64(bytes(data)), bytes.fromhex('7537022231269251275'))


