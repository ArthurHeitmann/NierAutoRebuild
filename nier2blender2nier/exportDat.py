#A very slightly modified version of
#https://github.com/WoefulWolf/NieR2Blender2NieR/blob/master/dat_dtt/exporter/export_dat.py

import math
import os

from nier2blender2nier.ioUtils import write_string, write_Int32, write_buffer, read_int32
#from util import *


def to_string(bs, encoding = 'utf8'):
	return bs.split(b'\x00')[0].decode(encoding)

#def main(dat_dir, export_filepath):
def export_dat(dat_dir, export_filepath):
    files = []
    hash_file_path = None

    # Get hash_file_path
    for filepath in os.listdir(dat_dir):
        if 'hash_data.metadata' in filepath:
            hash_file_path = dat_dir + '/' + filepath

    if hash_file_path == None:
        print('[!] DAT/DTT Error: hash_data.metadata not found.')
        return

    # Get files and their order
    if os.path.isfile(dat_dir + '/' + 'file_order.metadata'):
        file_orderFile = open(dat_dir + '/' + 'file_order.metadata', 'rb')
        fileCount = read_int32(file_orderFile)
        fileNameSize = read_int32(file_orderFile)

        for i in range(fileCount):
            fileName = to_string(file_orderFile.read(fileNameSize))
            files.append(dat_dir + '/' + fileName)
            # print('[' + fileName + ']')
    else:
        print('[!] DAT/DTT Error: file_order.metadata not found.')
        return
    

    fileNumber = len(files)

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

    hashMapSize = os.path.getsize(hash_file_path)

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
    hashMapFile = open(hash_file_path, 'rb')
    hashMap = hashMapFile.read()
    dat_file.write(hashMap)
    hashMapFile.close()

        # Files
    for i, fp in enumerate(files):
        dat_file.seek(fileOffsets[i])
        fileData = open(fp, 'rb')
        fileContent = fileData.read()
        dat_file.write(fileContent)
        fileData.close()

    dat_file.close()
    
    print('DAT Export Complete. :)')
    print()
