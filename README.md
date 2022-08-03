# Nier Auto Rebuild


File watcher for XML and Ruby files.

When a file changes:  
For ruby scripts they will be recompiled.  
For XML files they will be converted to YAX and the PAK files repacked.
Dat file will be created by combining everything.

### Usage

You need to have the "watchdog" library installed.

Since this repo uses git submodules, you have to clone it with the `--recurse-submodules` option.  
`git clone --recurse-submodules https://github.com/ArthurHeitmann/NierAutoRebuild.git`

To watch a folder:

`python main.py <folder> <out_file>`

### Credit

All the credit goes to:

RaiderB

https://github.com/ArthurHeitmann/NierAutoRebuild


WoefulWolf

https://github.com/WoefulWolf/NieR2Blender2NieR/


## Known issues

If your IDE saves multiple files at the same time, this currently won't work. You have to save one file at a time.
