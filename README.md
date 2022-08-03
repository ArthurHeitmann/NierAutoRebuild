# Nier Auto Rebuild


File watcher for XML and Ruby files.

When a file changes:  
For ruby scripts they will be recompiled.  
For XML files they will be converted to YAX and the PAK files repacked.   
Dat file will be created by combining everything.   

Goal is saving the modder from filetype and tool hell.

### Usage

You need to have the "watchdog" library installed.

Since this repo uses git submodules, you have to clone it with the `--recurse-submodules` option.  
`git clone --recurse-submodules https://github.com/bbssamuray/NierAutoRebuildDat.git`

To watch a folder (`out_dat` is optional .dat export path):

`python main.py <folder> [<out_dat>]`

### Credit

All the credit goes to:

RaiderB

https://github.com/ArthurHeitmann/NierAutoRebuild/


WoefulWolf

https://github.com/WoefulWolf/NieR2Blender2NieR/


## Known issues

If your IDE saves multiple files at the same time, this currently won't work. You have to save one file at a time.
