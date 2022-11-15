import argparse
import os

from extlibs.pyrominfo.pyrominfo import RomInfo
from extlibs.pyrominfo.pyrominfo import dreamcast, gameboy, gba, genericdisc, genesis, mastersystem, nes, nintendo64, nintendods, saturn, snes
from src.loadmodule import loadModule

"""
List the possible arguments
"""
parser = argparse.ArgumentParser(description='Parse a roms folder and extract data from roms')
parser.add_argument("--system", "-s", help="System name of the roms folder",
     choices=['dreamcast', 'gb', 'gba', 'megadrive', 'mastersystem', 'nes', 'n64', 'nds', 'saturn', 'snes'], required=True)
parser.add_argument("--jobs", "-j", help="Sets the number of parallel jobs to run", type=int, default=1)
args = parser.parse_args()


if __name__ == '__main__':
  print(RomInfo.parse('extlibs/pyrominfo/tests/data/Akumajou Dracula.fds'))
  print(RomInfo.parse('extlibs/pyrominfo/tests/data/Sonic the Hedgehog.bin'))
