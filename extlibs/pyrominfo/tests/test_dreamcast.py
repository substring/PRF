#!/usr/bin/env python3
#
# Copyright (C) 2013 Garrett Brown
# See Copyright Notice in rominfo.py

import testutils

import unittest

dreamcast = testutils.loadModule("dreamcast")

class TestDreamcastParser(unittest.TestCase):
    def setUp(self):
        self.dreamcastParser = dreamcast.DreamcastParser()

    def test_invalid(self):
        empty = self.dreamcastParser.parse("data/empty")
        self.assertEqual(len(empty), 0)

    def test_dreamcast_gdi(self):
        props = self.dreamcastParser.parse("data/Dreamkey.gdi")
        self.assertEqual(len(props), 17)
        self.assertEqual(props["platform"], "Dreamcast")
        self.assertEqual(props["hardware_id"], "SEGA SEGAKATANA")
        self.assertEqual(props["hardware_vendor_id"], "SEGA ENTERPRISES")
        self.assertEqual(props["media_id"], "D010")
        self.assertEqual(props["media_info_code"], "GD-ROM1/1")
        self.assertEqual(props["media_info"], "1/1")
        self.assertEqual(props["region_code"], "E")
        self.assertEqual(props["region"], "Europe")
        self.assertEqual(props["device_code"], "A799A10")
        self.assertEqual(props["devices"], "VGA box support, Puru Puru pack, Memory card, Start/A/B/Directions, X button, Y button, Analog R trigger, Analog L trigger, Analog horizontal controller, Analog vertical controller, Gun, Mouse")
        self.assertEqual(props["product_id"], "8320068 50")
        self.assertEqual(props["product_version"], "V1.001")
        self.assertEqual(props["release_date"], "2001-12-24")
        self.assertEqual(props["bootfile"], "1ST_READ.BIN")
        self.assertEqual(props["publisher"], "SEGA ENTERPRISES")
        self.assertEqual(props["title"], "DREAMKEY3")
        self.assertEqual(props["tracks"], [{'index': 1, 'mode': 1, 'filename': 'data/Dreamkey-1.bin', 'sector_size': 2352, 'offset': 0}, {'index': 2, 'mode': 0, 'filename': 'data/Dreamkey-2.bin', 'sector_size': 2352, 'offset': 0}, {'index': 3, 'mode': 1, 'filename': 'data/Dreamkey-3.bin', 'sector_size': 2352, 'offset': 0}])

    def test_dreamcast_cdi(self):
        props = self.dreamcastParser.parse("data/Daytona Usa.cdi")
        self.assertEqual(len(props), 17)
        self.assertEqual(props["platform"], "Dreamcast")
        self.assertEqual(props["hardware_id"], "SEGA SEGAKATANA")
        self.assertEqual(props["hardware_vendor_id"], "SEGA ENTERPRISES")
        self.assertEqual(props["media_id"], "2BD2")
        self.assertEqual(props["media_info_code"], "GD-ROM1/1")
        self.assertEqual(props["media_info"], "1/1")
        self.assertEqual(props["region_code"], "JUE")
        self.assertEqual(props["region"], "Asia, America, Europe")
        self.assertEqual(props["device_code"], "2799A10")
        self.assertEqual(props["devices"], "VGA box support, Puru Puru pack, Memory card, Start/A/B/Directions, X button, Y button, Analog R trigger, Analog L trigger, Analog horizontal controller, Analog vertical controller, Gun")
        self.assertEqual(props["product_id"], "MK-51037")
        self.assertEqual(props["product_version"], "V1.004")
        self.assertEqual(props["release_date"], "2001-02-14")
        self.assertEqual(props["bootfile"], "1ST_READ.BIN")
        self.assertEqual(props["publisher"], "SEGA ENTERPRISES")
        self.assertEqual(props["title"], "DAYTONAUSA")
        self.assertEqual(props["tracks"], [{'filename': 'data/Daytona Usa.cdi', 'index': 0, 'mode': 0, 'sector_size': 2352, 'offset': 352800}, {'filename': 'data/Daytona Usa.cdi', 'index': 1, 'mode': 2, 'sector_size': 2336, 'offset': 1408800}])

if __name__ == '__main__':
    unittest.main()
