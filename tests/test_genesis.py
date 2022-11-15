#!/usr/bin/env python3
#
# Copyright (C) 2013 Garrett Brown
# See Copyright Notice in rominfo.py

import testutils

import unittest

genesis = testutils.loadModule("genesis")

class TestGenesisParser(unittest.TestCase):
    def setUp(self):
        self.genesisParser = genesis.GensisParser()

    def test_invalid(self):
        empty = self.genesisParser.parse("data/empty")
        self.assertEqual(len(empty), 0)

    def test_genesis(self):
        props = self.genesisParser.parse("data/Sonic the Hedgehog.bin")
        self.assertEqual(len(props), 16)
        self.assertEqual(props["platform"], "Mega Drive")
        self.assertEqual(props["format"], "")
        self.assertEqual(props["console"], "SEGA MEGA DRIVE")
        self.assertEqual(props["copyright"], "(C)SEGA 1991.APR")
        self.assertEqual(props["publisher"], "SEGA")
        self.assertEqual(props["foreign_title"], "SONIC THE               HEDGEHOG")
        self.assertEqual(props["title"], "SONIC THE               HEDGEHOG")
        self.assertEqual(props["classification"], "Game")
        self.assertEqual(props["code"], "00001009")
        self.assertEqual(props["version"], "00")
        self.assertEqual(props["checksum"], "264A")
        self.assertEqual(props["device_code"], "J")
        self.assertEqual(props["devices"], "3B Joypad")
        self.assertEqual(props["memo"], "")
        self.assertEqual(props["region_code"], "JUE")
        self.assertEqual(props["region"], "Asia, America, Europe")

    def test_segacd(self):
        props = self.genesisParser.parse("data/Road Avenger.iso")
        self.assertEqual(len(props), 22)
        self.assertEqual(props["platform"], "Mega Drive")
        self.assertEqual(props["format"], "Sega CD")
        self.assertEqual(props["console"], "SEGA MEGA DRIVE")
        self.assertEqual(props["copyright"], "(C)T-32 1993.FEB")
        self.assertEqual(props["publisher"], "Wolfteam")
        self.assertEqual(props["foreign_title"], "ROAD BLASTER FX")
        self.assertEqual(props["title"], "ROAD AVENGER")
        self.assertEqual(props["classification"], "Education (MK)")
        self.assertEqual(props["code"], "4603-50")
        self.assertEqual(props["version"], "")
        self.assertEqual(props["checksum"], "2020")
        self.assertEqual(props["device_code"], "J")
        self.assertEqual(props["devices"], "3B Joypad")
        self.assertEqual(props["memo"], "")
        self.assertEqual(props["region_code"], "JUE")
        self.assertEqual(props["region"], "Asia, America, Europe")
        self.assertEqual(props["hardware_id"], "SEGADISCSYSTEM")
        self.assertEqual(props["volume_name"], "WOLFTEAM")
        self.assertEqual(props["volume_version"], "1.00")
        self.assertEqual(props["system_name"], "XOS/TOC")
        self.assertEqual(props["volume_version"], "1.00")

        self.assertEqual(props["tracks"], [{'filename': 'data/Road Avenger.iso', 'mode': 1, 'sector_size': 2048, 'index': 0, 'offset': 0}])

    def test_32x(self):
        props = self.genesisParser.parse("data/Star Wars Arcade.32x")
        self.assertEqual(len(props), 16)
        self.assertEqual(props["platform"], "Mega Drive")
        self.assertEqual(props["format"], "")
        self.assertEqual(props["console"], "SEGA 32X       U")
        self.assertEqual(props["copyright"], "(C)SEGA 1994 SEP")
        self.assertEqual(props["publisher"], "SEGA")
        self.assertEqual(props["foreign_title"], "STAR WARS ARCADE")
        self.assertEqual(props["title"], "STAR WARS ARCADE")
        self.assertEqual(props["classification"], "Game")
        self.assertEqual(props["code"], "MK-84508")
        self.assertEqual(props["version"], "00")
        self.assertEqual(props["checksum"], "CF83")
        self.assertEqual(props["device_code"], "J6")
        self.assertEqual(props["devices"], "3B Joypad, 6B Joypad")
        self.assertEqual(props["memo"], "")
        self.assertEqual(props["region_code"], "UJ")
        self.assertEqual(props["region"], "America, Asia")

if __name__ == '__main__':
    unittest.main()
