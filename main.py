import os
import pathlib
import sys
import time
import shutil
from threading import Timer

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from MrubyDecompiler import compileFile
from NierDocs.tools.pakScriptTools.xmlToYax import xmlToYax
from NierDocs.tools.pakScriptTools.pakRepacker import repackPak


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
    @debounce(0.1)
    def on_modified(self, event):
        if event.src_path.endswith(".xml"):
            yaxFile = event.src_path[:-4] + ".yax"
            if not os.path.exists(yaxFile):
                return
            print(f"Converting {event.src_path} to yax")
            xmlToYax(event.src_path, yaxFile)
            dirName = os.path.dirname(event.src_path)
            if dirName.endswith(".pak"):
                pakFileName = pathlib.Path(dirName).parts[-1]
                pakFile = str(pathlib.Path(dirName).parent.parent / pakFileName)
                print(f"Repacking {pakFile}")
                backupFile(pakFile)
                repackPak(dirName)
        elif event.src_path.endswith(".rb"):
            mrbBinFile = event.src_path[:-3]
            print(f"Compiling {event.src_path}")
            backupFile(mrbBinFile)
            compileFile(event.src_path, mrbBinFile)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python main.py <directory>")
        sys.exit(1)
    watchDir = sys.argv[1]
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
