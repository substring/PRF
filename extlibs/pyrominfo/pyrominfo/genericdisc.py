# Copyright (C) 2013 Garrett Brown
# See Copyright Notice in rominfo.py

from .rominfo import RomInfoParser

class GenericDiscParser(RomInfoParser):
    """
    Parse generic disc image or cuesheets. Valid extensions are iso, mdf, img, bin, cue, cdi, gdi.
    * https://wiki.osdev.org/ISO_9660
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
        if data[0x8001 : 0x8001 + 5] in [ b"CD001", b"BEA01", b"CD-I "]:
            return True
        return False

    def parseBuffer(self, data):
        props = {}
        props["platform"] = "Generic Disc"
        props["standard_id"] = self._sanitize(data[0x8001 : 0x8001 + 5])
        props["system_id"] = self._sanitize(data[0x8008 : 0x8008 + 32])
        props["volume_id"] = self._sanitize(data[0x8028 : 0x8028 + 32])
        props["set_info"] = "%d/%d" % (data[0x807f], data[0x807b])
        props["volume_set_id"] = self._sanitize(data[0x80be : 0x80be + 128])
        props["publisher_id"] = self._sanitize(data[0x813e : 0x813e + 128])
        props["data_preparer_id"] = self._sanitize(data[0x81be : 0x81be + 128])
        props["application_id"] = self._sanitize(data[0x823e : 0x823e + 128])
        props["copyright_file_id"] = self._sanitize(data[0x82be : 0x82be + 37])
        props["abstract_file_id"] = self._sanitize(data[0x82e3 : 0x82e3 + 37])
        props["bibliographic_file_id"] = self._sanitize(data[0x8308 : 0x8308 + 37])
        #props["creation_date_code"] = self._sanitize(data[0x832d : 0x832d + 17])
        props["creation_date"] = self._convertPvgDate(data[0x832d : 0x832d + 17])
        #props["modification_date_code"] = self._sanitize(data[0x833e : 0x833e + 17])
        props["modification_date"] = self._convertPvgDate(data[0x833e : 0x833e + 17])
        #props["expiration_date_code"] = self._sanitize(data[0x834f : 0x834f + 17])
        props["expiration_date"] = self._convertPvgDate(data[0x834f : 0x834f + 17])
        #props["effective_date_code"] = self._sanitize(data[0x8360 : 0x8360 + 17])
        props["effective_date"] = self._convertPvgDate(data[0x8360 : 0x8360 + 17])

        return props

    def _convertPvgDate(self, date):
        '''
        PVG date format is Year from 0001 to 9999
                           Month from 01 to 12
                           Day from 01 to 31.
                           Hour from 00 to 23.
                           Minute from 00 to 59.
                           Second from 00 to 59.
                           Hundredths of a second from 00 to 99
                           Time zone offset from GMT as integer
        '''
        if date == b"0000000000000000\x00":
            return ""
        else:
            return "%s-%s-%s %s:%s:%s.%s +%02d:%02d" % (date[0:4].decode("ascii"), date[4:6].decode("ascii"), date[6:8].decode("ascii"), \
                                                  date[8:10].decode("ascii"), date[10:12].decode("ascii"), \
                                                  date[12:14].decode("ascii"), date[14:16].decode("ascii"), \
                                                  (date[16] / 4), (date[16] % 4 * 15))

RomInfoParser.registerParser(GenericDiscParser())
