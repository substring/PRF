import argparse
import os
from src.loadmodule import loadModule

"""
List the possible arguments
"""
parser = argparse.ArgumentParser(description='Parse a roms folder and extract data from roms')
parser.add_argument("--system", "-s", help="System name of the roms folder",
     choices=['dreamcast', 'gb', 'gba', 'megadrive', 'mastersystem', 'nes', 'n64', 'nds', 'saturn', 'snes'], required=True)
parser.add_argument("--jobs", "-j", help="Sets the number of parallel jobs to run", type=int, default=1)
args = parser.parse_args()

def getRomParser(system):
    if system == 'nes':
        return loadModule('nes', 'pyrominfo').NESParser()

if __name__ == '__main__':
  #rominfo_module = loadModule('nes', 'pyrominfo')
  #romparser = rominfo_module.NESParser()
  romparser = getRomParser(args.system)
  print(romparser.getValidExtensions())
  