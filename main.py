import os
import pathlib
import sys
import time
import shutil
from threading import Lock, Timer
from typing import Set

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from MrubyDecompiler import compileFile
from NierDocs.tools.pakScriptTools.xmlToYax import xmlToYax
from NierDocs.tools.pakScriptTools.pakRepacker import repackPak
from nier2blender2nier.exportDat import export_dat

from pakWarningsChecker import checkWarningsOfPakFolder

watchDir: str = None
datFile: str = None

def backupFile(file: str):
    # copy the original file to <file>.bak the first time
    backupFile = file + ".bak"
    if not os.path.exists(backupFile):
        shutil.copy(file, backupFile)

def debounce(wait):
    """
    https://gist.github.com/walkermatt/2871026
    Decorator that will postpone a functions
    execution until after wait seconds
    have elapsed since the last time it was invoked.
    """
    def decorator(fn):
        def debounced(*args, **kwargs):
            def call_it():
                fn(*args, **kwargs)
            try:
                debounced.t.cancel()
            except AttributeError:
                pass
            debounced.t = Timer(wait, call_it)
            debounced.t.start()
        return debounced
    return decorator


class FileChangeHandler(FileSystemEventHandler):
    pendingFiles: Set[str]
    mutex = Lock()

    def __init__(self):
        self.pendingFiles = set()

    def on_modified(self, event):
        if event.is_directory:
            return
        self.mutex.acquire()
        self.pendingFiles.add(event.src_path)
        self.mutex.release()
        self.handlePendingFiles()
    
    @debounce(0.15)
    def handlePendingFiles(self):
        self.mutex.acquire()
        hasDatChanged = False
        changedPakDirs = set()
        for file in self.pendingFiles:
            fileName = os.path.basename(file)
            if file.endswith(".xml"):
                yaxFile = file[:-4] + ".yax"
                if not os.path.exists(yaxFile):
                    continue
                print(f"Converting {fileName} to yax")
                xmlToYax(file, yaxFile)
                dirName = os.path.dirname(file)
                if dirName.endswith(".pak"):
                    changedPakDirs.add(dirName)

            elif file.endswith(".rb"):
                mrbBinFile = file[:-3]
                print(f"Compiling {fileName}")
                backupFile(mrbBinFile)
                compileFile(file, mrbBinFile)
                hasDatChanged = True
            
        for dirName in changedPakDirs:
            pakFileName = pathlib.Path(dirName).parts[-1]
            pakFile = str(pathlib.Path(dirName).parent.parent / pakFileName)
            print(f"Repacking {pakFile}")
            checkWarningsOfPakFolder(dirName)
            backupFile(pakFile)
            repackPak(dirName)
            hasDatChanged = True
        if datFile is not None and hasDatChanged:
            export_dat(watchDir, datFile)
        self.pendingFiles.clear()
        self.mutex.release()
        

if __name__ == '__main__':
    # if len(sys.argv) < 2:
    #     print("Usage: python main.py <directory> [<out_dat>]")
    #     sys.exit(1)
    # watchDir = sys.argv[1]
    watchDir = "D:\delete\\mods\\na\\blender\\extracted\\data012.cpk_unpacked\\st5\\nier2blender_extracted\\r501.dat"
    if len(sys.argv) > 2:
        datFile = sys.argv[2]
    handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(handler, watchDir, recursive=True)
    observer.start()
    print(f"Watching {watchDir}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
