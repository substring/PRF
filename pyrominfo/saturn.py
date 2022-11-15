# Copyright (C) 2015 Jan Holthuis
# See Copyright Notice in rominfo.py

from .rominfo import RomInfoParser

class SaturnParser(RomInfoParser):
    """
    Parse a Sega Saturn image. Valid extensions are iso, mdf, img, bin, cue, gdi
    Sega Saturn header references and related source code:
    * https://segaretro.org/images/b/be/ST-040-R4-051795.pdf
    """

    def getValidExtensions(self):
        return ["iso", "mdf", "img", "bin", "cue", "cdi", "gdi"]

    def parse(self, filename):
        props = {}

        tracks = self._getDiscTracks(filename)

        if tracks:
            filename = tracks[0]["filename"]
        else:
            return props

        with open(filename, "rb") as f:
            # read first 17 sectors of disc image and convert it if neccessary
            f.seek(tracks[0]["offset"])
            data = bytearray(f.read(17 * 2352))

            # Try to convert raw CD images
            if tracks != None and tracks[0]["sector_size"] != 2048:
                data = self._convertRawToUser(data, tracks[0]["sector_size"], tracks[0]["mode"])

            if self.isValidData(data):
                props = self.parseBuffer(data)
                if tracks != None:
                    props["tracks"] = tracks
        return props

    def isValidData(self, data):
        if data[0x0 : 0x0 + 15] == b"SEGA SEGASATURN":
            return True
        return False


    def parseBuffer(self, data):
        # See SEGA's Disc Format Standards Specification Sheet Ver. 1.0, p. 13 for details.
        props = {}
        props["platform"] = "Saturn"

        # 0x00 Hardware Identifier
        props["hardware_id"] = self._sanitize(data[0x00 : 0x00 + 16])

        # 0x10 Maker ID
        props["publisher"] = self._sanitize(data[0x10 : 0x10 + 16])
        #TODO 3rd party codes

        # 0x20 Product Number
        props["product_id"] = self._sanitize(data[0x20 : 0x20 + 10])

        # 0x2A Version
        props["product_version"] = self._sanitize(data[0x2a : 0x2a + 6])

        # 0x30 Release Date YYYYMMDD
        release_date_code = self._sanitize(data[0x30 : 0x30 + 8])
        props["release_date"] = "%s-%s-%s" % (release_date_code[0:4], release_date_code[4:6], release_date_code[6:8])

        # 0x38 Device Information
        props["media_info_code"] = self._sanitize(data[0x38 : 0x38 + 8])
        props["media_info"] = "/".join( props["media_info_code"][3:].split("/"))

        # 0x40 Compatible Area Symbol
        props["region_code"] = self._sanitize(data[0x40 : 0x40 + 10])
        props["region"] = ", ".join([saturn_regions.get(d) for d in props["region_code"] \
                                                             if d in saturn_regions])

        # 0x50 Compatible Peripheral
        props["device_code"] = self._sanitize(data[0x50 : 0x50 + 16])
        props["devices"] = ", ".join([saturn_devices.get(d) for d in props["device_code"] \
                                                             if d in saturn_devices])

        # 0x60 Game Title
        props["title"] = self._sanitize(data[0x60 : 0x60 + 112])

        return props

RomInfoParser.registerParser(SaturnParser())


saturn_regions = {
    "J": "Japan",   # Japan
    "T": "Asia",    # Asia NTSC (Taiwan, Philippines, Korea)
    "U": "America", # North America (U. S., Canada, Central South America (Brazil))
    "E": "Europe",  # Europe PAL, East Asia PAL, Central South America PAL
}

saturn_devices = {
    "J": "Control Pad",
    "A": "Analog Controller",
    "M": "Mouse",
    "K": "Keyboard",
    "S": "Steering Controller",
    "T": "Multitap",
}
