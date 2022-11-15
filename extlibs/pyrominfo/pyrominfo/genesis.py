# Copyright (C) 2013 Garrett Brown
# See Copyright Notice in rominfo.py

from .rominfo import RomInfoParser

class GensisParser(RomInfoParser):
    """
    Parse a Sega Gensis image. Valid extensions are smd, gen, 32x, md, bin, iso, mdx, 68k, sgd, cue.
    Sega Gensis header references and related source code:
    * http://www.zophar.net/fileuploads/2/10614uauyw/Genesis_ROM_Format.txt
    * http://en.wikibooks.org/wiki/Genesis_Programming
    * http://cgfm2.emuviews.com/txt/smdform.txt (SMD file format)
    * http://raphnet.net/electronique/genesis_cart/smd2bin/smd2bin.c (SMD file format)
    * loadrom.c of the Genesis Plus GX project:
    * https://code.google.com/p/genplus-gx/source/browse/trunk/source/loadrom.c
    * rom.c of the Gens project:
    * http://gens.cvs.sourceforge.net/viewvc/gens/Gens-MultiPlatform/linux/src/gens/util/file/rom.c?view=markup
    * md_slot.c of the MAME project:
    * http://git.redump.net/mame/tree/src/mess/machine/md_slot.c
    * https://www.retrodev.com/segacd.html
    * http://devster.monkeeh.com/sega/32xguide1.txt
    * https://plutiedev.com/rom-header
    * https://segaretro.org/images/a/a5/Mega-CD_Disc_Format_Specifications.pdf
    """

    def getValidExtensions(self):
        return ["smd", "gen", "32x", "md", "bin", "iso", "mdx", "68k", "sgd", "cue"]

    def parse(self, filename):
        props = {}

        tracks = self._getDiscTracks(filename)

        if tracks:
            filename = tracks[0]["filename"]

        with open(filename, "rb") as f:
            # only read first 17 sectors for disc images and convert it if neccessary
            if tracks:
                data = bytearray(f.read(17 * 2352))
                if tracks[0]["sector_size"] != 2048:
                    data = self._convertRawToUser(data, tracks[0]["sector_size"], tracks[0]["mode"])
            else:
                data = bytearray(f.read())

            if self.isValidData(data):
                props = self.parseBuffer(data)
                if tracks != None:
                    props["tracks"] = tracks

        return props

    def isValidData(self, data):
        """
        Detect console name (one of two values, depending on the console's country
        of origin) or the presence of an SMD header.
        """
        if data[0x100 : 0x100 + 15] == b"SEGA MEGA DRIVE" or \
           data[0x100 : 0x100 + 15] == b"SEGA_MEGA_DRIVE" or \
           data[0x100 : 0x100 + 12] == b"SEGA GENESIS" or \
           data[0x100 : 0x100 + 8] == b"SEGA 32X" or \
           data[0x100 : 0x100 + 9] == b"SEGA PICO":
            return True
        if self.hasSMDHeader(data) or self.isInterleaved(data):
            return True
        return False

    def parseBuffer(self, data):
        props = {}

        # TODO: If extension is .mdx, decode image
        #data = [b ^ 0x40 for b in data[4 : -1]] # len(data) decreases by 5

        props["platform"] = "Mega Drive"

        # Auto-detect SMD/MD interleaving
        if self.hasSMDHeader(data):
            data = data[0x200 : ]
            self.deinterleaveSMD(data)
            props["format"] = "Super Magic Drive interleaved"
        elif self.isInterleaved(data):
            self.deinterleaveMD(data)
            props["format"] = "Multi Game Doctor interleaved"
        elif data[0x0 : 0x0 + 14] == b"SEGADISCSYSTEM" or \
             data[0x0 : 0x0 + 12] == b"SEGABOOTDISC" or \
             data[0x0 : 0x0 + 12] == b"SEGADATADISC" or \
             data[0x0 : 0x0 + 8] == b"SEGADISC":
            props["format"] = "Sega CD"
        else:
            props["format"] = ""

        # 0100-010f - Console name, can be "SEGA MEGA DRIVE" or "SEGA GENESIS"
        #             depending on the console's country of origin.
        props["console"] = self._sanitize(data[0x100 : 0x100 + 16])

        # 0110-011f - Copyright notice, in most cases of this format: (C)T-XX 1988.JUL
        props["copyright"] = self._sanitize(data[0x110 : 0x110 + 16])

        # Publisher data is extracted from copyright notice
        props["publisher"] = self.getPublisher(props["copyright"][3 : 3 + 4])

        # 0120-014f - Domestic name, the name the game has in its country of origin
        props["foreign_title"] = self._sanitize(data[0x120 : 0x120 + 48])

        # 0150-017f - International name, the name the game has worldwide
        props["title"] = self._sanitize(data[0x150 : 0x150 + 48])

        # 0180-0181 - Type of product. Known values: GM = Game,  AL = Education
        #             en.wikibooks.org uses AL, Genesis_ROM_Format.txt Uses Al, loadrom.c uses AI...
        props["classification"] = "Game" if data[0x180 : 0x180 + 2] == b"GM" else ("Education (%s)" % data[0x180 : 0x180 + 2].decode("ascii", "ignore"))

        # 0183-018A - Product code (type was followed by a space)
        props["code"] = self._sanitize(data[0x183 : 0x183 + 8])

        # 018C-018D - Product version (code was followed by a hyphen "-")
        props["version"] = self._sanitize(data[0x18c : 0x18c + 2])

        # 018E-018F - Checksum
        props["checksum"] = "%04X" % (data[0x18e] << 8 | data[0x18f])

        # 0190-019F - I/O device support
        props["device_code"] = self._sanitize(data[0x190 : 0x190 + 16])
        props["devices"] = ", ".join([genesis_devices.get(d) for d in props["device_code"] \
                                                             if d in genesis_devices])
        # 01BC-01C7 - Modem Support
        if data[0x1bc : 0x1bc + 2] == b"MO":
            props["modem"] = "yes"
            props["modem_code"] = self._sanitize(data[0x1bc : 0x1bc + 12]) 
            props["modem_publisher"] = self.getPublisher(props["modem_code"][2 : 2 + 4])
            props["modem_game_number"] = self._sanitize(data[0x1c2 : 0x1c2 + 2])
            props["modem_version"] = self._sanitize(data[0x1c5 : 0x1c5 + 1])
            props["modem_region"] = genesis_modem_supports.get(self._sanitize(data[0x1c6 : 0x1c6 + 2]), "")

        # 01C8-01EF - Memo
        props["memo"] = self._sanitize(data[0x1c8 : 0x1c8 + 40])

        # 01F0-01FF - Countries in which the product can be released. This field
        #             can contain up to three countries. According to
        #             http://www.squish.net/generator/manual.html, it may also be a
        #             single hex digit which represents a new-style country code.
        props["region_code"] = self._sanitize(data[0x1f0 : 0x1f0 + 16])
        props["region"] = ", ".join([genesis_regions.get(d) for d in props["region_code"] \
                                                             if d in genesis_regions])
        if props["region_code"] != "" and props["region"] == "":
            region = []
            for r_code, r_desc in list(genesis_regions.items()):
                if type(r_code) != str and int(props["region_code"], 16) & r_code == r_code:
                    region.append(r_desc)
            props["region"] = ", ".join(region)

        # Parse special Sega CD header
        # See SEGA's Mega-CD Disc Format Specifications Ver. 2.00, p. 18 for details.
        if props["format"] == "Sega CD":
            # 0000-000f Disc identifier
            props["hardware_id"] = self._sanitize(data[0x00 : 0x00 + 16])
            # 0010-001b Volume name
            props["volume_name"] = self._sanitize(data[0x10 : 0x10 + 12])
            # 001c-001d Volume version - BCD encoded >100 are prereleases
            props["volume_version"] = "%X.%02X" % (data[0x1c], data[0x1d])
            # 0020-001b System name 
            props["system_name"] = self._sanitize(data[0x20 : 0x20 + 12])
            # 002c-001d System version - BCD encoded >100 are prereleases
            props["system_version"] = "%X.%02X" % (data[0x2c], data[0x2d])

        return props

    def deinterleaveSMD(self, data):
        """
        Super Magic Drive interleaved file-format (.SMD) is a non-straight-forward
        file-format. It has a 512-byte header and is interleaved in 16KB blocks,
        with even bytes at the beginning and odd bytes at the end.
        """
        for i in range(len(data) >> 14):
            block = data[i*0x4000 : (i + 1)*0x4000] # 0x4000 == 1 << 14
            data[i*0x4000 : (i + 1)*0x4000 : 2], data[i*0x4000 + 1 : (i + 1)*0x4000 : 2] = \
                block[0x2000 : ], block[ : 0x2000]

    def hasSMDHeader(self, data):
        """
        Returns true if the file was generated by a Super Magic Drive copier.
        Header format (512 bytes):
            Byte 00h : Size of file in 16K blocks.
            Byte 01h : 03h
            Byte 02h : Split file indicator (00h=single or last file, 40h=split file)
            Byte 08h : AAh
            Byte 09h : BBh
            Byte 0Ah : 06h

        Note that smd2bin.c and Gens don't check byte 01h, only bytes 08h-0Ah.
        """
        if len(data) < 512:
            return False
        if data[0x08:0x0a] == b"\xAA\xBB\x06":
            return True

        # If the SMD header's binary data is corrupt or uniform zero, we still
        # want to detect the header, so attempt this heuristic (used in Genesis
        # Plus GX's): console text is not SEGA, size is multiple of 512, and
        # there's an odd number of 512 blocks.
        if data[0x100 : 0x100 + 4] != b"SEGA" and len(data) % 512 == 0 and (len(data) >> 9) % 2:
            return True

        # Finally, directly analyze the payload
        return self.isInterleaved(data[0x200 : ])

    def deinterleaveMD(self, data):
        """
        Multi Game Doctor file-format (.MD) is an interleaved, non-headered format.
        The interleaving it uses is equal to the SMD, but without the division in
        blocks. (Even bytes at the beginning of file, odd bytes at the end. Source
        correction: Genesis_ROM_Format.txt erroneously says "Even at the end, odd
        at the beginning.")
        """
        mid = len(data) >> 1
        data[::2], data[1::2] = data[mid : ], data[ : mid]

    def isInterleaved(self, data):
        """
        Test for interleaved (SMD or MD) data. Tests are from md_slot.c of the
        # MAME project. The data parameter assumes that SMD header has been
        # stripped before being passed as an argument.
        """
        # Gens checks data[0x80 : 0x81] == b"EA" (odd bytes) for evidence of
        # interlacing. I think MAME also checks data[0x2080 : 0x2081] == b"SG"
        # (even bytes).
        if data[0x80 : 0x81] == b"EA" and data[0x2080 : 0x2081] == b"SG":
            return True

        # Phelios USA redump, Target Earth, Klax (Namcot)
        if data[0x80 : 0x81] == b"SG" and data[0x2080 : 0x2081] == b" E":
            return True

        # For MD interleaving, instead of looking for odd bytes, just look for
        # more even bytes. We need two tests here for different console names.
        if data[0x80 : 0x80 + 4] in [b"EAMG", b"EAGN"]:
            return True

        # Test for edge cases. Tests are from md_slot.c of the MAME project.
        # Per their comments, code is taken directly from GoodGEN by Cowering.
        # Tests are for SMD interleaving which uses 16K blocks, so cases with
        # addresses < 0x2000 (8K) should also be valid tests for MD interleaving.
        edge_cases = [
            (0x00f0, "OL R-AEAL"),        # Jap Baseball 94
            (0x00f3, "optrEtranet"),      # Devilish Mahjong Tower
            (0x0100, "\x3C\x00\x00\x3C"), # Golden Axe 2 Beta
            (0x0090, "OEARC   "),         # Omega Race
            (0x6708, " NTEBDKN"),         # Budokan Beta
            (0x02c0, "so fCXP"),          # CDX-Pro 1.8 BIOS
            (0x0090, "sio-Wyo "),         # Ishido (hacked)
            (0x0088, "SS  CAL "),         # Onslaught
            (0x3648, "SG NEPIE"),         # Tram Terror Pirate
            (0x0007, "\x1C\x0A\xB8\x0A"), # Breath of Fire 3 Chinese
            (0x1cbe, "@TTI>"),            # Tetris Pirate
        ]

        return any(data[case[0] : case[0] + len(case[1])] == case[1] for case in edge_cases)

    def getPublisher(self, copyright_str):
        """
        Resolve a copyright string into a publisher name. It SHOULD be 4
        characters after a (C) symbol, but there are variations. When the
        company uses a number as a company code, the copyright usually has
        this format: '(C)T-XX 1988.JUL', where XX is the company code.
        """
        company = copyright_str[0:4]
        if "-" in company:
            company = company[company.rindex("-") + 1 : ]
        company = company.rstrip()
        return gensis_publishers.get(company, "")

RomInfoParser.registerParser(GensisParser())


genesis_regions = {
    "J": "Asia",     # Japan, Korea, Asian NTSC
    "U": "America",  # North American NTSC, Brazilian PAL-M, Argentine PAL-N
    "E": "Europe",   # European PAL
    0b0001: "Domestic, NTSC (Japan)",
    0b0010: "Domestic, PAL",
    0b0100: "Overseas, NTSC (America)",
    0b1000: "Overseas, PAL (Europe)",
}

genesis_devices = {
    "J": "3B Joypad",
    "6": "6B Joypad",
    "K": "Keyboard",
    "P": "Printer",
    "B": "Control Ball",
    "F": "Floppy Drive",
    "L": "Activator",
    "4": "Multitap",
    "0": "MS Joypad",
    "R": "RS232C Serial",
    "T": "Tablet",
    "V": "Paddle",
    "C": "CD-ROM",
    "M": "Mega Mouse",
    "G": "Menacer",
    "A": "Analog joystick",
    "D": "Download",
}

gensis_publishers = {
    "ACLD": "Ballistic",
    "RSI":  "Razorsoft",
    "SEGA": "SEGA",
    "TREC": "Treco",
    "VRGN": "Virgin Games",
    "WSTN": "Westone",
    "10":   "Takara",
    "11":   "Taito or Accolade",
    "12":   "Capcom",
    "13":   "Data East",
    "14":   "Namco or Tengen",
    "15":   "Sunsoft",
    "16":   "Bandai",
    "17":   "Dempa",
    "18":   "Technosoft",
    "19":   "Technosoft",
    "20":   "Asmik",
    "22":   "Micronet",
    "23":   "Vic Tokai",
    "24":   "American Sammy",
    "29":   "Kyugo",
    "32":   "Wolfteam",
    "33":   "Kaneko",
    "35":   "Toaplan",
    "36":   "Tecmo",
    "40":   "Toaplan",
    "42":   "UFL Company Limited",
    "43":   "Human",
    "45":   "Game Arts",
    "47":   "Sage's Creation",
    "48":   "Tengen",
    "49":   "Renovation or Telenet",
    "50":   "Electronic Arts",
    "56":   "Razorsoft",
    "58":   "Mentrix",
    "60":   "Victor Musical Ind.",
    "69":   "Arena",
    "70":   "Virgin",
    "73":   "Soft Vision",
    "74":   "Palsoft",
    "76":   "Koei",
    "79":   "U.S. Gold",
    "81":   "Acclaim/Flying Edge",
    "83":   "Gametek",
    "86":   "Absolute",
    "87":   "Mindscape",
    "93":   "Sony",
    "95":   "Konami",
    "97":   "Tradewest",
    "100":  "T*HQ Software",
    "101":  "Tecmagik",
    "112":  "Designer Software",
    "113":  "Psygnosis",
    "119":  "Accolade",
    "120":  "Code Masters",
    "125":  "Interplay",
    "130":  "Activision",
    "132":  "Shiny & Playmates",
    "144":  "Atlus",
    "151":  "Infogrames",
    "161":  "Fox Interactive",
    "177":  "Ubisoft",
    "239":  "Disney Interactive",
}

genesis_modem_supports = {
    "00": "Japan no mic",
    "10": "Japan with mic",
    "20": "Overseas no mic",
    "30": "Overseas with mic",
    "40": "Japan no mic, Overseas no mic",
    "50": "Japan with mic, Overseas with mic",
    "60": "Japan no mic, Overseas with mic",
    "70": "Japan with mic, Overseas no mic",
    "80": "Reserved",
    "90": "Reserved",
}
