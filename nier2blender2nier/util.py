import json
import os
from typing import List
from nier2blender2nier.ioUtils import read_uint32

def importContentsFileFromFolder(folderPath: str) -> List[str]:
    # search for metadata or json file
    datInfoJson = ""
    fileOrderMetadata = ""
    for file in os.listdir(folderPath):
        if file == "dat_info.json":
            datInfoJson = os.path.join(folderPath, file)
            break
        elif file == "file_order.metadata":
            fileOrderMetadata = os.path.join(folderPath, file)
    if datInfoJson:
        return readJsonDatInfo(datInfoJson)
    elif fileOrderMetadata:
        return readFileOrderMetadata(fileOrderMetadata)
    raise Exception(f"No metadata file found in {folderPath}")


def getFileSortingKey(file: str):
    base, ext = os.path.splitext(file)
    return (base.lower(), ext.lower())

def readJsonDatInfo(filepath: str) -> List[str]:
    with open(filepath, "r") as f:
        filesData = json.load(f)
    files = []
    dir = os.path.dirname(filepath)
    for file in filesData["files"]:
        files.append(os.path.join(dir, file))
    # remove duplicates and sort
    files = list(set(files))
    files.sort(key=getFileSortingKey)
    
    return files
    
def readFileOrderMetadata(filepath: str) -> List[str]:
    if filepath.endswith("hash_order.metadata"):
        raise Exception("hash_order.metadata is not supported! Please use 'file_order.metadata' instead.")
        
    with open(filepath, "rb") as f:
        num_files = read_uint32(f)
        name_length = read_uint32(f)
        files = []
        for i in range(num_files):
            files.append(f.read(name_length).decode("utf-8").strip("\x00"))
        # remove duplicates and sort
        files = list(set(files))
        files.sort(key=getFileSortingKey)

    return files
    