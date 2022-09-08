import os
from typing import Dict, List, Tuple
import xml.etree.ElementTree as ET
import zlib
import json

# UTILS

def printWarning(text: str) -> None:
	# orange text
	print(f"\033[33m{currentFile}:\tWARNING: {text}\033[0m")

def getId(elem: ET.Element, idTag = "id") -> int:
	try:
		return int(elem.find(idTag).text, 16)
	except:
		return -1

def crc32(text: str) -> int:
	return zlib.crc32(text.encode('ascii')) & 0xFFFFFFFF

# MAIN

currentFile: str = ""
def checkWarningsInFolder(folder: str) -> None:
	global currentFile
	allIds: Dict[str, List[int]] = {
		"groups": [],
		"actions": [],
		"entities": [],
		"script variable": [],
	}

	xmlDocs: Tuple[str, List[ET.Element]] = []
	for file in findAllPakXmlFiles(folder):
		xmlName = os.path.basename(file)
		if not os.path.isfile(file):
			printWarning(f"{xmlName} is missing")
			continue

		currentFile = xmlName
		xmlDoc = ET.parse(file).getroot()
		xmlDocs.append((xmlName, xmlDoc))

		collectIds(xmlDoc, allIds)
	
	for file, xmlDoc in xmlDocs:
		currentFile = file
		verifyIdUsages(xmlDoc, allIds)
		verifySizes(xmlDoc)
		verifyHashes(xmlDoc)

def findAllPakXmlFiles(folder: str) -> List[str]:
	# find all pakInfo.json and find their xml files
	pakInfos: List[str] = []
	xmlFiles: List[str] = []
	for root, dirs, filenames in os.walk(folder):
		for filename in filenames:
			if filename != "pakInfo.json":
				continue
			pakInfos.append(os.path.join(root, filename))

	for pakInfoPath in pakInfos:
		with open(pakInfoPath, "r") as f:
			pakInfo = json.load(f)
		for file in pakInfo["files"]:
			xmlName = file["name"].replace(".yax", ".xml")
			pakInfoFolder = os.path.dirname(pakInfoPath)
			xmlFiles.append(os.path.join(pakInfoFolder, xmlName))
			
	return xmlFiles

# CHECKS

def collectIds(xmlDoc: ET.Element, allIds: Dict[str, List[int]]) -> None:
	def handleId(category: str, elem: ET.Element):
		id = getId(elem)
		if id < 0 or id > 0xFFFFFFFF:
			printWarning(f"{category} (<{elem.tag}>) id 0x{id:x} is out of range")
		if category in allIds and id in allIds[category]:
			printWarning(f"Duplicate {category} (<{elem.tag}>) id 0x{id:x}")
		else:
			if category not in allIds:
				allIds[category] = []
			allIds[category].append(id)

	# file ID
	fileId = getId(xmlDoc)
	if fileId != -1:
		handleId("files", xmlDoc)

	# actions
	for action in xmlDoc.findall("action"):
		handleId("actions", action)

	# groups (0.xml)
	if currentFile == "0.xml":
		for group in xmlDoc.findall("group"):
			handleId("groups", group)
	
	# entities
	for layouts in xmlDoc.findall(".//layouts"):
		normal = layouts.find("normal")
		if normal is None:
			continue
		layouts = normal.find("layouts")
		if layouts is None:
			continue
		for value in layouts.findall("value"):
			handleId("entities", value)
		
	# script ids
	for scriptVars in xmlDoc.findall(".//variables"):
		for value in scriptVars.findall("value"):
			handleId("script variable", value)

def verifyIdUsages(xmlDoc: ET.Element, allIds: Dict[str, List[int]]) -> None:
	actionHash = crc32("hap::Action")
	entityHash = crc32("app::EntityLayout")

	# file group id
	fileGroup = xmlDoc.find("group")
	if fileGroup is not None and fileGroup.text.startswith("0x"):
		fileGroupId = int(fileGroup.text, 16)
		if fileGroupId not in allIds["groups"]:
			printWarning(f"Group id 0x{fileGroupId:x} references unknown group")

	for elem in xmlDoc.iter():
		code = elem.find("code")
		value = elem.find("value")
		id = elem.find("id")
		if code is None or (value is None and id is None):
			continue
		codeId = getId(elem, "code")
		valueId = getId(elem, "value") if value is not None else getId(elem, "id")
		if valueId == 0 or valueId == -1:
			continue
		if codeId == actionHash:
			if valueId not in allIds["actions"]:
				printWarning(f"Action code 0x{codeId:x} references unknown action 0x{valueId:x}")
		elif codeId == entityHash:
			if valueId not in allIds["entities"]:
				printWarning(f"Entity code 0x{codeId:x} references unknown entity 0x{valueId:x}")


def verifySizes(xmlDoc: ET.Element) -> None:
	def verifySizeFor(parent: ET.Element, sizeElemI: int, size: int):
		trueSize = len(parent) - sizeElemI - 1
		if trueSize != size:
			printWarning(f"<{parent.tag}> has {trueSize} elements instead of {size}")

	for elem in xmlDoc.iter():
		sizeElem = elem.find("size")
		countElem = elem.find("count")
		if sizeElem is not None:
			verifySizeFor(
				elem,
				list(elem).index(sizeElem),
				int(sizeElem.text)
			)
		elif countElem is not None and countElem.text.startswith("0x"):
			verifySizeFor(
				elem,
				list(elem).index(countElem),
				int(countElem.text, 16)
			)

def verifyHashes(xmlDoc: ET.Element) -> None:
	for elem in xmlDoc.iter():
		if "str" in elem.attrib:
			if crc32(elem.attrib["str"]) == int(elem.text, 16):
				continue
			printWarning(f"<{elem.tag}> hash mismatch ({elem.text} != crc32(\"{elem.attrib['str']}\")=0x{crc32(elem.attrib['str']):x})")
