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

**To watch a folder:**  

`python main.py <folder> [<out_dat>]`

`<out_dat>` is an optional .dat file export path. If used, `<folder>` has to be a dat directory

### Credits

The dat exporter is from Woeful_Wolf's [Nier2Blender2Nier](https://github.com/WoefulWolf/NieR2Blender2NieR) addon.
