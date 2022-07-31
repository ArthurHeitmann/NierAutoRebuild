# Nier Autorebuild

File watcher for XML and Ruby files.

When a file changes:  
For ruby scripts they will be recompiled.  
For XML files they will be converted to YAX and the PAK files repacked.

### Usage

Since this repo uses git submodules, you have to clone it with the `--recurse-submodules` option.  
`git clone --recurse-submodules https://github.com/ArthurHeitmann/NierAutoRebuild.git`

To watch a folder:

`python main.py <folder>`

## Known issues

If your IDE saves multiple files at the same time, this currently won't work. You have to save one file at a time.
