#A very slightly modified version of
#https://github.com/WoefulWolf/NieR2Blender2NieR/blob/master/dat_dtt/exporter/export_dat.py

import math
import os

from nier2blender2nier.ioUtils import write_string, write_Int32, write_buffer, read_int32
#from util import *


def to_string(bs, encoding = 'utf8'):
	return bs.split(b'\x00')[0].decode(encoding)

def export_dat(export_filepath, file_list):
    files = file_list
    fileNumber = len(files)
    from .datHashGenerator import generateHashData
    hashData = generateHashData(files)

    fileExtensionsSize = 0
    fileExtensions = []
    for fp in files:
        fileExt = fp.split('.')[-1]
        fileExt += '\x00' * (3 - len(fileExt))
        fileExtensionsSize += len(fileExt) + 1
        fileExtensions.append(fileExt)

    nameLength = 0                              
    for fp in files:
        fileName = os.path.basename(fp)
        if len(fileName)+1 > nameLength:
            nameLength = len(fileName)+1

    fileNames = []                             
    for fp in files:
        fileName = os.path.basename(fp)
        fileNames.append(fileName)

    hashMapSize = hashData.getStructSize()

    # Header
    fileID = 'DAT'
    fileNumber = fileNumber
    fileOffsetsOffset = 32
    fileExtensionsOffset = fileOffsetsOffset + (fileNumber * 4)
    fileNamesOffset = fileExtensionsOffset + fileExtensionsSize
    fileSizesOffset = fileNamesOffset + (fileNumber * nameLength) + 4
    hashMapOffset = fileSizesOffset + (fileNumber * 4)

    #fileOffsets
    fileOffsets = []
    currentOffset = hashMapOffset + hashMapSize
    for fp in files:
        currentOffset = (math.ceil(currentOffset / 16)) * 16
        fileOffsets.append(currentOffset)
        currentOffset += os.path.getsize(fp)

    # fileSizes
    fileSizes = []
    for fp in files:
        fileSizes.append(os.path.getsize(fp))

    # WRITE
        # Header
    dat_file = open(export_filepath, 'wb')
    write_string(dat_file, fileID)
    write_Int32(dat_file, fileNumber)
    write_Int32(dat_file, fileOffsetsOffset)
    write_Int32(dat_file, fileExtensionsOffset)
    write_Int32(dat_file, fileNamesOffset)
    write_Int32(dat_file, fileSizesOffset)
    write_Int32(dat_file, hashMapOffset)
    write_buffer(dat_file, 4)

        # fileOffsets
    for value in fileOffsets:
        write_Int32(dat_file, value)

        # fileExtensions
    for value in fileExtensions:
        write_string(dat_file, value)

        # nameLength
    write_Int32(dat_file, nameLength)

        # fileNames
    for value in fileNames:
        write_string(dat_file, value)
        if len(value) < nameLength:
            write_buffer(dat_file, nameLength - len(value) - 1)

        # fileSizes
    for value in fileSizes:
        write_Int32(dat_file, value)

        # hashMap
    hashData.write(dat_file)

        # Files
    for i, fp in enumerate(files):
        dat_file.seek(fileOffsets[i])
        fileData = open(fp, 'rb')
        fileContent = fileData.read()
        dat_file.write(fileContent)
        fileData.close()

    dat_file.close()
    print('DAT/DTT Export Complete. :)')