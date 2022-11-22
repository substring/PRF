import binascii
import hashlib
import os
import py7zr
import zipfile

class Rom:
	# rom must be a fullpath to an existing rom file
	def __init__(self, rom: str, crc = '', filecrc = ''):
		if not os.path.exists(rom):
			raise Exception(rom + " doesn't exist")
		self.rompathname = rom
		self.rompath = os.path.dirname(rom)
		self.romfile = os.path.basename(rom)
		self.romname = os.path.splitext(self.romfile)[0]
		self.romext = os.path.splitext(rom)[1][1:]
		self.crc = crc
		self.md5 = None
		self.sha1 = None
		self.filecrc = filecrc
		self.archiveContent = []
		self.isoExtensions = ['iso', 'cue', 'chd']
		self.known_archive_extentions = ['zip', '7z']
		self.getCRC()
		self.getMD5()
		self.getSHA1()

	def __repr__(self):
		return "Rom('{}', crc = '{}', filecrc = '{}')".format(self.rompathname, self.crc, self.filecrc)

	def __str__(self):
		return "Rom: {}\nSplit into {} / {} . {}\nHashes:\n  - CRC: {}\n  - MD5: {}\n  - SHA1: {}\nFile content:: {}".format(self.rompathname, self.rompath, self.romfile, self.romext, self.crc, self.md5, self.sha1, self.archiveContent)

	def getCRC(self) -> str |None:
		if self.crc:
			return self.crc
		self.listArchive()
		if self.isArchive() and len(self.archiveContent) == 1:
			self.crc = list(self.archiveContent[0].values())[0].zfill(8)
		elif self.isArchive():
			self.crc = self.fileCRC()
		else:
			self.crc = self.fileCRC()
		return self.crc

	def fileCRC(self) -> str:
		buf = open(self.rompathname, 'rb').read()
		self.filecrc = self.compute_hash(buf, 'crc')
		return self.filecrc

	def isArchive(self) -> bool:
		return self.romext in self.known_archive_extentions

	def listArchiveFromZip(self) -> list:
		filesList = []
		with zipfile.ZipFile(self.rompathname) as romzip:
			zipinfodata = romzip.infolist()
			for f in zipinfodata:
				decimalCRC = romzip.getinfo(f.filename).CRC
				filesList.append({f.filename: f'{decimalCRC:x}'})
		return filesList

	def listArchiveFrom7z(self) -> list:
		filesList = []
		with py7zr.SevenZipFile(self.rompathname, 'r') as romzip:
			zipinfodata = romzip.list()
			for f in zipinfodata:
				decimalCRC = zipinfodata[0].crc32
				filesList.append({f.filename: f'{decimalCRC:x}'})
		return filesList

	def listArchive(self) -> list | None:
		if self.romext not in ['7z', 'zip']:
			return None
		if self.romext == 'zip':
			self.archiveContent = self.listArchiveFromZip()
		if self.romext == '7z':
			self.archiveContent = self.listArchiveFrom7z()

	def extractFileFromZip(self, archiveFile: str, destinationPath = '/tmp'):
		if not destinationPath:
			return zipfile.ZipFile(self.rompathname).read(archiveFile)
		with zipfile.ZipFile(self.rompathname) as romzip:
			outputFile = romzip.extract(archiveFile, destinationPath)
			return outputFile

	def extractFileFrom7z(self, archiveFile: str, destinationPath = '/tmp'):
		if not destinationPath:
			return py7zr.SevenZipFile(self.rompathname).read([archiveFile])[archiveFile].getvalue()
		with py7zr.SevenZipFile(self.rompathname, 'r') as romzip:
			romzip.extract(destinationPath, archiveFile)
			return "{}/{}".format(destinationPath, archiveFile)

	def extractRom(self, fileName=None, path=''):
		extractedFileLocation = None
		if not fileName:
			fileName = list(self.archiveContent[0].keys())[0]
		if self.romext == 'zip':
			extractedFileLocation = self.extractFileFromZip(fileName, path)
		if self.romext == '7z':
			extractedFileLocation = self.extractFileFrom7z(fileName, path)
		return extractedFileLocation

	def getMD5orSHA1(self, hashType) -> str | None:
		if hashType not in ['md5', 'sha1']:
			return None

		if self.isArchive() and len(self.archiveContent) != 1:
			file_data = open(self.rompathname,'rb').read()
		elif self.isArchive() and len(self.archiveContent) == 1:
			file_data = self.extractRom()
		elif not self.isArchive():
			file_data = open(self.rompathname,'rb').read()
		else:
			# This case should never happen, but the most obvious reason is an unvalid archive
			raise Exception('Not a valid file')
		return self.compute_hash(file_data, hashType)

	def getMD5(self):
		if not self.md5:
			self.md5 = self.getMD5orSHA1('md5')
		return self.md5

	def getSHA1(self):
		if not self.sha1:
			self.sha1 = self.getMD5orSHA1('sha1')
		return self.sha1

	def compute_hash(self, buffer, hash_type:str) -> str:
		if hash_type == 'crc' or hash_type == 'crc32)':
			return "%08X".lower() % (binascii.crc32(buffer) & 0xFFFFFFFF)
		if hash_type == 'md5':
			return hashlib.md5(buffer).hexdigest()
		if hash_type == 'sha1':
			return hashlib.sha1(buffer).hexdigest()
		return ''