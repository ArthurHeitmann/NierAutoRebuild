import os
from typing import Dict, List
import xml.etree.ElementTree as ET
import zlib

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
def checkWarningsOfPakFolder(folder: str) -> None:
	global currentFile
	allIds: Dict[str, List[int]] = {}

	xmlDocs: List[ET.Element] = []
	for file in os.listdir(folder):
		# is YAX XML
		filePath = os.path.join(folder, file)
		if not (file.endswith(".xml") and os.path.exists(filePath.replace(".xml", ".yax"))):
			continue

		currentFile = file
		xmlDoc = ET.parse(filePath).getroot()
		xmlDocs.append(xmlDoc)

		collectIds(xmlDoc, allIds)
	
	for xmlDoc in xmlDocs:
		verifyIdUsages(xmlDoc, allIds)
		verifySizes(xmlDoc)
		verifyHashes(xmlDoc)

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

	# actions
	for action in xmlDoc.findall("action"):
		handleId("actions", action)
	
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

	for elem in xmlDoc.iter():
		code = elem.find("code")
		value = elem.find("value")
		if code is None or value is None:
			continue
		codeId = getId(elem, "code")
		valueId = getId(elem, "value")
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
			printWarning(f"<{elem.tag}> hash mismatch ({elem.text} != crc32(\"{elem.attrib['str']}\")=0x{crc32(elem.text):x})")
