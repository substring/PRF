#!/usr/bin/env python3
#
# Copyright (C) 2013 Garrett Brown
# See Copyright Notice in rominfo.py

import testutils

import unittest

nes = testutils.loadModule("nes")

class TestNESParser(unittest.TestCase):
    def setUp(self):
        self.nesParser = nes.NESParser()

    def test_invalid(self):
        empty = self.nesParser.parse("data/empty")
        self.assertEqual(len(empty), 0)

    def test_nes(self):
        props = self.nesParser.parse("data/Metroid.nes")
        self.assertEqual(len(props), 16)
        self.assertEqual(props["platform"], "Nintendo Entertainment System")
        self.assertEqual(props["prg_size"], "128KB")
        self.assertEqual(props["prg_size_bytes"], 131072)
        self.assertEqual(props["chr_size"], "0KB")
        self.assertEqual(props["chr_size_bytes"], 0)
        self.assertEqual(props["mirroring"], "horizontal")
        self.assertEqual(props["battery"], "")
        self.assertEqual(props["trainer"], "")
        self.assertEqual(props["four_screen_vram"], "")
        self.assertEqual(props["console_type"], "")
        self.assertEqual(props["header"], "iNES")
        self.assertEqual(props["mapper_code"], "001")
        self.assertEqual(props["mapper"], "MMC1")
        self.assertEqual(props["submapper_code"], "")
        self.assertEqual(props["video_output"], "")
        self.assertEqual(props["rom_size_bytes"], 131072)

    def test_unif(self):
        props = self.nesParser.parse("data/Dancing Blocks (1990)(Sachen)(AS)[p][!][SA-013][NES cart].unf")
        self.assertEqual(len(props), 13)
        self.assertEqual(props["platform"], "Nintendo Entertainment System")
        self.assertEqual(props["header"], "UNIF")
        self.assertEqual(props["prg_size"], "32KB")
        self.assertEqual(props["prg_size_bytes"], 32768)
        self.assertEqual(props["chr_size"], "8KB")
        self.assertEqual(props["chr_size_bytes"], 8192)
        self.assertEqual(props["mirroring"], "vertical")
        self.assertEqual(props["battery"], "")
        self.assertEqual(props["four_screen_vram"], "")
        self.assertEqual(props["mapper"], "UNL-SA-NROM")
        self.assertEqual(props["video_output"], "")
        self.assertEqual(props["title"], "Dancing Blocks (72 pin cart)")
        self.assertEqual(props["rom_size_bytes"], 40960)

    def test_fds(self):
        props = self.nesParser.parse("data/Akumajou Dracula.fds")
        self.assertEqual(len(props), 12)
        self.assertEqual(props["platform"], "Familiy Computer Disk System")
        self.assertEqual(props["header"], "FDS")
        self.assertEqual(props["disk_sides"], 2)
        self.assertEqual(props["manufactor_code"], 164)
        self.assertEqual(props["manufactor"], "Konami")
        self.assertEqual(props["title"], "AKM")
        self.assertEqual(props["game_type"], "")
        self.assertEqual(props["revision"], 2)
        self.assertEqual(props["disk_type"], "FMC")
        self.assertEqual(props["manufactor_date"], "1986-10-20")
        self.assertEqual(props["rewrite_date"], "")
        self.assertEqual(props["country"], "Japan")
if __name__ == '__main__':
    unittest.main()
