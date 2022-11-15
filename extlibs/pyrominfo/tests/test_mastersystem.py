#!/usr/bin/env python3
#
# Copyright (C) 2013 Garrett Brown
# See Copyright Notice in rominfo.py

import testutils

import unittest

mastersystem = testutils.loadModule("mastersystem")

class TestMastersystemParser(unittest.TestCase):
    def setUp(self):
        self.mastersystemParser = mastersystem.MasterSystemParser()

    def test_invalid(self):
        empty = self.mastersystemParser.parse("data/empty")
        self.assertEqual(len(empty), 0)

    def test_mastersystem(self):
        props = self.mastersystemParser.parse("data/Air Rescue.sms")
        self.assertEqual(len(props), 14)
        self.assertEqual(props["header_id"], "TMR SEGA")
        self.assertEqual(props["reserved_word"], "")
        self.assertEqual(props["checksum"], "F90A")
        self.assertEqual(props["checksum_ascii"], [])
        self.assertEqual(props["code"], "007102")
        self.assertEqual(props["version"], "00")
        self.assertEqual(props["platform"], "Master System")
        self.assertEqual(props["region"], "Export")
        self.assertEqual(props["rom_size"], "256KB")
        self.assertEqual(props["rom_size_bytes"], 262144)
        self.assertEqual(props["date"], "")
        self.assertEqual(props["author"], "")
        self.assertEqual(props["title"], "")
        self.assertEqual(props["description"], "")

    def test_gamegear(self):
        props = self.mastersystemParser.parse("data/Tails Adventures.gg")
        self.assertEqual(len(props), 14)
        self.assertEqual(props["header_id"], "TMR SEGA")
        self.assertEqual(props["reserved_word"], "")
        self.assertEqual(props["checksum"], "0000")
        self.assertEqual(props["checksum_ascii"], [])
        self.assertEqual(props["code"], "002583")
        self.assertEqual(props["version"], "00")
        self.assertEqual(props["platform"], "Game Gear")
        self.assertEqual(props["region"], "Export")
        self.assertEqual(props["rom_size"], "256KB")
        self.assertEqual(props["rom_size_bytes"], 262144)
        self.assertEqual(props["date"], "")
        self.assertEqual(props["author"], "")
        self.assertEqual(props["title"], "")
        self.assertEqual(props["description"], "")

if __name__ == '__main__':
    unittest.main()
