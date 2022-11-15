#!/usr/bin/env python3
#
# Copyright (C) 2013 Garrett Brown
# See Copyright Notice in rominfo.py

import testutils

import unittest

gameboy = testutils.loadModule("gameboy")

class TestGameboyParser(unittest.TestCase):
    def setUp(self):
        self.gbParser = gameboy.GameboyParser()

    def test_invalid(self):
        empty = self.gbParser.parse("data/empty")
        self.assertEqual(len(empty), 0)

    def test_gameboy(self):
        props = self.gbParser.parse("data/Tetris.gb")
        self.assertEqual(len(props), 17)
        self.assertEqual(props["title"], "TETRIS")
        self.assertEqual(props["platform"], "Game Boy")
        self.assertEqual(props["sgb_support"], "")
        self.assertEqual(props["publisher"], "Nintendo")
        self.assertEqual(props["publisher_code"], "01")
        self.assertEqual(props["cartridge_type"], "ROM")
        self.assertEqual(props["cartridge_type_code"], "00")
        self.assertEqual(props["rom_size"], "32KB")
        self.assertEqual(props["rom_size_bytes"], 32768)
        self.assertEqual(props["rom_size_code"], "00")
        self.assertEqual(props["ram_size"], "0KB")
        self.assertEqual(props["ram_size_bytes"], 0)
        self.assertEqual(props["ram_size_code"], "00")
        self.assertEqual(props["destination"], "Japan")
        self.assertEqual(props["version"], "01")
        self.assertEqual(props["header_checksum"], "0A")
        self.assertEqual(props["global_checksum"], "16BF")

    def test_gameboycolor(self):
        props = self.gbParser.parse("data/The Legend of Zelda - Links Awakening DX.gbc")
        self.assertEqual(len(props), 17)
        self.assertEqual(props["title"], "ZELDA")
        self.assertEqual(props["platform"], "Game Boy Color")
        self.assertEqual(props["sgb_support"], "yes")
        self.assertEqual(props["publisher"], "Nintendo")
        self.assertEqual(props["publisher_code"], "01")
        self.assertEqual(props["cartridge_type"], "ROM+MBC5+RAM+BATT")
        self.assertEqual(props["cartridge_type_code"], "1B")
        self.assertEqual(props["rom_size"], "1MB")
        self.assertEqual(props["rom_size_bytes"], 1048576)
        self.assertEqual(props["rom_size_code"], "05")
        self.assertEqual(props["ram_size"], "32KB")
        self.assertEqual(props["ram_size_bytes"], 32768)
        self.assertEqual(props["ram_size_code"], "03")
        self.assertEqual(props["destination"], "")
        self.assertEqual(props["version"], "00")
        self.assertEqual(props["header_checksum"], "3C")
        self.assertEqual(props["global_checksum"], "E3FD")

if __name__ == '__main__':
    unittest.main()
