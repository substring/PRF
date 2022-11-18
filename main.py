import argparse
import concurrent.futures
import os

from rom import Rom
from extlibs.pyrominfo.pyrominfo import RomInfo
from extlibs.pyrominfo.pyrominfo import dreamcast, gameboy, gba, genericdisc, genesis, mastersystem, nes, nintendo64, nintendods, saturn, snes


"""
List the possible arguments
"""

parser = argparse.ArgumentParser(description='Parse a roms folder and extract data from roms')
parser.add_argument("path", type=str, help="A path to roms")
parser.add_argument("--system", "-s", help="System name of the roms folder",
    choices=['dreamcast', 'gb', 'gba', 'megadrive', 'mastersystem', 'nes', 'n64', 'nds', 'saturn', 'snes'], required=True)
parser.add_argument("--jobs", "-j", help="Sets the number of parallel jobs to run", type=int, default=1)
args = parser.parse_args()

def parse_rom(rom_file: str):
    # Determine if the file is a supported archive or not
    # Archive: make sure there is only one rom inside and buffer it
    # Compute its hashes
    my_rom = Rom(rom_file)
    #print(my_rom)
    real_rom = ''
    #if my_rom.archiveContent and len(my_rom.archiveContent) == 1:
    if my_rom.isArchive() and len(my_rom.archiveContent) > 1:
        ret = {}
    elif my_rom.isArchive():
        real_rom = list(my_rom.archiveContent[0].keys())[0]
        rom_data = my_rom.extractRom('ram', real_rom)
        ret = RomInfo.parseBuffer(rom_data)
    else:
        ret = RomInfo.parse(rom_file)
    ret['source'] = rom_file
    ret['rom'] = real_rom if real_rom else os.path.basename(rom_file)
    return ret


if __name__ == '__main__':
    #print(RomInfo.parse('extlibs/pyrominfo/tests/data/Akumajou Dracula.fds'))
    #print(RomInfo.parse('extlibs/pyrominfo/tests/data/Sonic the Hedgehog.bin'))

    if not os.path.exists(args.path):
        raise ValueError("Path %s doesn't exist", args.path)

    # find files
    files_list = []
    print("Looking for files...")
    for path, subdirs, files in os.walk(args.path):
        for name in files:
            files_list.append(os.path.join(path, name))
    print("Sorting file list...")
    files = sorted(files)
    # print(files_list)
    total_nb_files = len(files)
    nb_parsed_files = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers = args.jobs) as executor:
        parsed_files = {executor.submit(parse_rom, file): file for file in files_list}
        for rom in concurrent.futures.as_completed(parsed_files):
            result = parsed_files[rom]
            nb_parsed_files += 1
            try:
                data = rom.result()
            except Exception as exc:
                print("\r%r generated an exception: %s" % (result, exc))
            else:
                #print('Parsing result: \n%s' % data)
                pass
            finally:
                print("\rFiles parsed: %d / %d" % (nb_parsed_files, total_nb_files), end='')

