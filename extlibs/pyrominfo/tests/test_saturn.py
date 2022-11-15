#!/usr/bin/env python3
#
# Copyright (C) 2013 Garrett Brown
# See Copyright Notice in rominfo.py

import testutils

import unittest

saturn = testutils.loadModule("saturn")

class TestSaturnParser(unittest.TestCase):
    def setUp(self):
        self.saturnParser = saturn.SaturnParser()

    def test_invalid(self):
        empty = self.saturnParser.parse("data/empty")
        self.assertEqual(len(empty), 0)

    def test_saturn(self):
        props = self.saturnParser.parse("data/Virtua Fighter CG Portrait Collection-1.bin")
        self.assertEqual(len(props), 14)
        self.assertEqual(props["platform"], "Saturn")
        self.assertEqual(props["hardware_id"], "SEGA SEGASATURN")
        self.assertEqual(props["publisher"], "SEGA ENTERPRISES")
        self.assertEqual(props["product_id"], "610-6083")
        self.assertEqual(props["product_version"], "V1.000")
        self.assertEqual(props["release_date"], "1995-08-03")
        self.assertEqual(props["media_info_code"], "CD-1/1")
        self.assertEqual(props["media_info"], "1/1")
        self.assertEqual(props["region_code"], "E")
        self.assertEqual(props["region"], "Europe")
        self.assertEqual(props["device_code"], "J")
        self.assertEqual(props["devices"], "Control Pad")
        self.assertEqual(props["title"], "VF CG COLLECTION")
        self.assertEqual(props["tracks"], [{'filename': 'data/Virtua Fighter CG Portrait Collection-1.bin', 'mode': 1, 'sector_size': 2352, 'index': 0, 'offset': 0}])

if __name__ == '__main__':
    unittest.main()
