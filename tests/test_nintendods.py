#!/usr/bin/env python3
#
# Copyright (C) 2013 Garrett Brown
# See Copyright Notice in rominfo.py

import testutils

import unittest

nintendods = testutils.loadModule("nintendods")

class TestNintendoDsParser(unittest.TestCase):
    def setUp(self):
        self.nintendoDsParser = nintendods.NintendoDsParser()

    def test_invalid(self):
        empty = self.nintendoDsParser.parse("data/empty")
        self.assertEqual(len(empty), 0)

    def test_nds(self):
        props = self.nintendoDsParser.parse("data/Time Hollow.nds")
        self.assertEqual(len(props), 11)
        self.assertEqual(props["title"], "TIMEHOLLOW")
        self.assertEqual(props["code"], "YHLP")
        self.assertEqual(props["publisher"], "Konami")
        self.assertEqual(props["publisher_code"], "A4")
        self.assertEqual(props["unit_code"], "00")
        self.assertEqual(props["platform"], "Nintendo DS")
        self.assertEqual(props["ndsi_enhanced"], "")
        self.assertEqual(props["rom_size"], "1024Mbit")
        self.assertEqual(props["rom_size_bytes"], 134217728)
        self.assertEqual(props["version"], "00")
        self.assertEqual(props["header_checksum"], "2233")

if __name__ == '__main__':
    unittest.main()
