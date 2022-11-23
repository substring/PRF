import argparse
import concurrent.futures
import os
import re

import goodset
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
parser.add_argument("--naming", "-n", help="Specify a rom naming convention (Not yet implemented)", type=int, default=1, choices=['nointro', 'goodset'])
parser.add_argument("--fail", help="No exceptions mangagement, break on any error", action='store_true')
parser.add_argument("--print", "-p", help="Print a light report at the end", action='store_true')
args = parser.parse_args()

def parse_rom(rom_file: str):
    # Determine if the file is a supported archive or not
    # Archive: make sure there is only one rom inside and buffer it
    # Compute its hashes
    my_rom = Rom(rom_file)
    cleaned_rom_name = clean_name_goodset(my_rom)
    #print(my_rom)
    real_rom = ''
    #if my_rom.archiveContent and len(my_rom.archiveContent) == 1:
    if my_rom.isArchive() and len(my_rom.archiveContent) > 1:
        raise ValueError("Can't determine which rom to extract from archive")
    elif my_rom.isArchive():
        real_rom = list(my_rom.archiveContent[0].keys())[0]
        rom_data = my_rom.extractRom()
        ret = RomInfo.parseBuffer(rom_data)
    else:
        #print(rom_file)
        ret = RomInfo.parse(rom_file)

    if not ret:
        raise ValueError('Unknown header')

    ret['source'] = rom_file
    ret['rom'] = real_rom if real_rom else os.path.basename(rom_file)
    ret['cleaned_title'] = cleaned_rom_name
    return ret

def clean_name_goodset(rom_obj: Rom) -> str|None:
    rom_name = rom_obj.romname
    # We reverse the results, so the country is the last pattern we would match and replace
    # Anything before is part of the rom name
    #for matching_group in reversed(re.findall("\(.*?\)", rom_name)):
    for matching_group in reversed(re.findall("(\(.*?\)|\[.*?\])", rom_name)):
        rom_name = rom_name.replace(matching_group, '')
        if matching_group[1:-1] in goodset.COUNTRY_CODES:
            #print('Found country: %s' % matching_group[1:-1])
            break
    #print('Final rom name: %s' % rom_name)
    return rom_name.rstrip()

def clean_name_nointro(name: Rom) -> str|None:
    pass

def final_output(ok_roms_list: {}):
    for rom in ok_roms_list:
        #print(rom)
        #continue
        print(rom['cleaned_title'], end='')
        if 'title' in rom:
            print(" - %s" % rom['title'], end='')
        if 'foreign_title' in rom:
            print(" / %s" % rom['foreign_title'], end='')
        print()

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
    files_list = sorted(files_list)
    # print(files_list)
    total_nb_files = len(files_list)
    nb_parsed_files = 0
    roms_error = dict()
    roms_ok = list()

    with concurrent.futures.ThreadPoolExecutor(max_workers = args.jobs) as executor:
        parsed_files = {executor.submit(parse_rom, file): file for file in files_list}
        for rom in concurrent.futures.as_completed(parsed_files):
            result = parsed_files[rom]
            nb_parsed_files += 1
            if args.fail:
                data = rom.result()
                continue
            try:
                data = rom.result()
            except Exception as exc:
                print("\r%r generated an exception: %s" % (result, exc))
                roms_error[result] = exc
            else:
                #print('Parsing result: \n%s' % data)
                # should sort roms in a dict indexed with the 'title' or 'foreign_title' if it exists in the result
                roms_ok.append(data)
            finally:
                print("\rFiles parsed: %d / %d" % (nb_parsed_files, total_nb_files), end='')
    print() # bring back a \n
    print("Roms not parsed: %d/%d" % (len(roms_error), total_nb_files))

    if args.print:
        final_output(roms_ok)
