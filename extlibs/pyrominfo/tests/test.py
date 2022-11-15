#!/usr/bin/env python3
#
# Copyright (C) 2013 Garrett Brown
# See Copyright Notice in rominfo.py

# TODO: Automate the import process
from test_dreamcast import TestDreamcastParser
from test_gameboy import TestGameboyParser
from test_gba import TestGBAParser
from test_genericdisc import TestGenericdiscParser
from test_genesis import TestGenesisParser
from test_mastersystem import TestMastersystemParser
from test_nes import TestNESParser
from test_nintendo64 import TestNintendo64Parser
from test_nintendods import TestNintendoDsParser
from test_saturn import TestSaturnParser
from test_snes import TestSNESParser

import unittest

if __name__ == "__main__":
    unittest.main()
