# Deputil
A pure-python cli, and library, for listing a package(or file)'s dependencies

Currently supports:  
    - Python


### Usage
```bash 
> deputil path/to/package
send2trash
sl4ng
audio_metadata
filetype
dill
pyperclip

> deputil path/to/package -v
send2trash
sl4ng
audio_metadata >= 0.11.1
filetype >= 1.0.8
dill >= 0.3.3
pyperclip >= 1.8.2

> deputil path/to/package -w
...
> cat requirements.txt
send2trash
sl4ng
audio_metadata
filetype
dill
pyperclip
```
