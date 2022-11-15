#
#     Copyright (C) 2013 Garrett Brown
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
#     The above copyright notice and this permission notice shall be included
#     in all copies or substantial portions of the Software.
#
# The Software may include Python modules derived from other works using
# different licensing terms. In such cases, the Python module is considered to
# be a separate work and is subject to the licensing terms declared at the
# beginning of that module.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import struct
import re
import csv

class RomInfoParser(object):
    """
    Base class for ROM info parsers. When an info parser subclasses this
    object, it can register itself with registerParser(), and
    pyrominfo.parse() will automatically include it when trying to parse a ROM
    file.
    """

    __parsers = []

    @staticmethod
    def registerParser(romInfoParser):
        RomInfoParser.__parsers.append(romInfoParser)

    @staticmethod
    def getParsers():
        return RomInfoParser.__parsers

    def __init__(self):
        pass

    def getValidExtensions(self):
        return []

    def isValidExtension(self, ext):
        return ext in self.getValidExtensions()

    def parse(self, filename):
        return {}

    def isValidData(self, data):
        return False

    def parseBuffer(self, data):
        return {}

    def _getExtension(self, uri):
        return uri[uri.rindex(".") + 1 : ].lower() if "." in uri else ""

    def _sanitize(self, title):
        """
        Turn all non-ASCII characters into spaces (tab, CR and LF line breaks
        are OK to preserve formatting), and then return a stripped string.
        """
        return ''.join(chr(b) if b in [ord('\t'), ord('\n'), ord('\r')] or \
                       0x20 <= b and b <= 0x7E else ' ' for b in title).strip()

    def _allASCII(self, data):
        return all(0x20 <= b and b <= 0x7E for b in data)

    def _parseCdi(self, filename):
        tracks = []
        with open(filename, mode="rb") as f:
            f.seek(0, 2)
            image_length = f.tell()
            if image_length < 8:
                #Image file is too short
                return None

            f.seek(-8, 2)

            image_version = cdi_versions.get(struct.unpack("<I", f.read(4))[0], "")
            if image_version not in [2, 3, 3.5]:
                #Unsupported image version
                return None

            image_header_offset = struct.unpack("<I", f.read(4))[0]
            if image_header_offset == 0:
                #Bad image format
                return None

            if image_version == 3.5:
                f.seek(image_length - image_header_offset)
            else:
                f.seek(image_header_offset)

            track_offset = 0
            index = 0
            # Sessions
            for s in range(struct.unpack("<H", f.read(2))[0]):
                # Tracks
                for t in range(struct.unpack("<H", f.read(2))[0]):
                    track = {}
                    track["filename"] = filename
                    track["index"] = index
                    index += 1

                    # DiscJuggler 3.00.780 and up adds extra data
                    if struct.unpack("<I", f.read(4))[0] != 0:
                        f.seek(8, 1)

                    for i in range(2):
                        current_start_mark = f.read(10)
                        if current_start_mark != b"\x00\x00\x01\x00\x00\x00\xFF\xFF\xFF\xFF":
                            #Could not find the track start mark
                            return None

                    f.seek(4, 1)
                    f.seek(struct.unpack("<B", f.read(1))[0] + 19, 1)

                    # DiscJuggler 4 adds extra data
                    if struct.unpack("<I", f.read(4))[0] == 0x80000000:
                        f.seek(8, 1)
                    f.seek(2, 1)
                    track_pregap_length = struct.unpack("<I", f.read(4))[0]
                    f.seek(10, 1)
                    track["mode"] = struct.unpack("<I", f.read(4))[0]
                    f.seek(16, 1)
                    track_total_length = struct.unpack("<I", f.read(4))[0]
                    f.seek(16, 1)
                    sector_size_id = struct.unpack("<I", f.read(4))[0]

                    if sector_size_id in track_sector_sizes:
                        track["sector_size"] = track_sector_sizes.get(sector_size_id, "")
                    else:
                        #Unsupported sector size
                        return None

                    track["offset"] = (track_offset + track_pregap_length *
                                       track["sector_size"])

                    track_offset += track_total_length * track["sector_size"]

                    f.seek(29, 1)
                    if image_version != 2:
                        f.seek(5, 1)
                        # DiscJuggler 3.00.780 and up adds extra data
                        if struct.unpack("<I", f.read(4))[0] == 0xffffffff:
                            f.seek(78, 1)

                    tracks.append(track)

                # Skip to next session
                f.seek(12, 1)
                if image_version != 2:
                    f.seek(1, 1)

            # Extract IP.BIN data
            if len(tracks) == 0:
                return None
            return tracks

    def _parseCue(self, filename):
        tracks = []
        track = {}

        with open(filename, mode="r") as f:
            for line in f:
                m = re.search('FILE .(.*). (.*)$', line)
                if m:
                    track_filename = os.path.relpath(os.path.join(
                      os.path.dirname(filename),m.group(1)))
                m = re.search('TRACK (\d+) ([^\s]*)', line)
                if m:
                    track["index"] = int(m.group(1))
                    if m.group(2) == "AUDIO":
                        track["mode"] = 0
                        track["sector_size"] = 2352
                    elif m.group(2) == "MODE1/2048":
                        track["mode"] = 1
                        track["sector_size"] = 2048
                    elif m.group(2) == "MODE1/2352":
                        track["mode"] = 1
                        track["sector_size"] = 2352
                    elif m.group(2) in ["MODE2/2336", "CDI/2336"]:
                        track["mode"] = 2
                        track["sector_size"] = 2336
                    elif m.group(2) in ["MODE2/2352", "CDI/2352"]:
                        track["mode"] = 2
                        track["sector_size"] = 2352
                m = re.search('INDEX (\d+) (\d+):(\d+):(\d+)', line)
                if m:
                    if int(m.group(1)) == 1:
                        minutes = int(m.group(2))
                        seconds = int(m.group(3))
                        sectors = int(m.group(4))
                        track["offset"] = ((minutes * 60 * 75) + (seconds * 75) + sectors) * track["sector_size"]
                        if track:
                            track["filename"] = track_filename
                            tracks.append(track)
                            track = {}
        if len(tracks) == 0:
            return None
        return tracks

    def _parseGdi(self, filename):
        tracks = []
        track = {}

        with open(filename, mode="r") as f:
            num_tracks = int(f.readline().strip())
            gdi_reader = csv.reader(f, delimiter=' ', quotechar='"', skipinitialspace=True)
            for row in gdi_reader:
                track = {}
                track["index"] = int(row[0])
                track["mode"] = 0 if int(row[2]) == 0 else 1
                track["filename"] = os.path.relpath(os.path.join(
                    os.path.dirname(filename), row[4]))
                track["sector_size"] = int(row[3])
                track["offset"] = int(row[5])
                tracks.append(track)
        if len(tracks) == 0:
            return None
        return tracks

    def _parseDiscImage(self, filename):
        """
        Locate Primary Volume Descriptor of a disc image.
        """
        tracks = []
        track = {}
        track["filename"] = filename

        with open(filename, "rb") as f:
            # read first 17 CD sectors of CD image
            data = f.read(17 * 2352)

        # MODE1/2048 Mode 1 Data (cooked)
        if data[0x8001 : 0x8001 + 5] in [b"CD001", b"BEA01"]:
            track["mode"] = 1
            track["sector_size"] = 2048
        # MODE1/2336 Mode 1 Data (raw)
        elif data[0x9211 : 0x9211 + 5] in [b"CD001", b"BEA01"]:
            track["mode"] = 1
            track["sector_size"] = 2336
        # MODE1/2352 Mode 1 raw
        elif data[0x9311 : 0x9311 + 5] in [b"CD001", b"BEA01"]:
            track["mode"] = 1
            track["sector_size"] = 2352
        # MODE2/2048 XA Mode 2 Data (form 1)
        elif data[0x8019 : 0x8019 + 5] in [b"CD001", b"BEA01"]:
            track["mode"] = 2
            track["sector_size"] = 2048
        # MODE2/2324 XA Mode 2 Data (form 2)
        elif data[0x8bb9 : 0x8bb9 + 5] in [b"CD001", b"BEA01"]:
            track["mode"] = 2
            track["sector_size"] = 2324
        # MODE2/2336 XA Mode 2 Data (form mix) / CDI Mode 2 Data
        elif data[0x9219 : 0x9219 + 5] in [b"CD001", b"BEA01", b"CD-I "]:
            track["mode"] = 2
            track["sector_size"] = 2336
        # MODE2/2352 XA Mode 2 Data (raw) / CDI Mode 2 Data
        elif data[0x9319 : 0x9319 + 5] in [b"CD001", b"BEA01", b"CD-I "]:
            track["mode"] = 2
            track["sector_size"] = 2352
        # AUDIO / CDG / no disc image
        else:
            return None

        track["index"] = 0
        track["offset"] = 0
        tracks.append(track)
        return tracks

    def _getDiscTracks(self, filename):
        ext = self._getExtension(filename)
        if ext == "cdi":
            return self._parseCdi(filename)
        elif ext == "cue":
            return self._parseCue(filename)
        elif ext == "gdi":
            return self._parseGdi(filename)
        elif ext in ["iso", "mdf", "img", "bin", "raw"]:
            return self._parseDiscImage(filename)
        else:
            return None

    def _convertRawToUser(self, rawdata, size = 2352, mode = 1):
        """
        function name: http://baetzler.de/vidgames/psx_cd_faq.html
        Convert RAW disc data to user data.
        """
        userdata = []
        #header = 16 if mode == 1 else 24
        if mode == 1 and size == 2352:
            header = 16
        elif mode == 2 and size == 2336:
            header = 8
        elif mode == 2 and size == 2352:
            header = 24
        else:
            header = 0

        if size == 2048:
            return rawdata

        for i in range(len(rawdata) // size):
            userdata.extend(rawdata[(i * size) + header : (i * size) + header + 2048])
        return bytes(userdata)

cdi_versions = {
    0x80000004: 2,
    0x80000005: 3,
    0x80000006: 3.5,
}

track_sector_sizes = {
    0: 2048,
    1: 2336,
    2: 2352
}

track_modes = {
    0: "AUDIO",
    1: "MODE1",
    2: "MODE2"
}
