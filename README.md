# Python Photo Renamer
This is just a litle script I made to rename photos based on their modified
date.

# Installation
```
python3 -m virtualenv venv3
source venv3/bin/activate
```

# Usage
Rename a single file with:
`python rename-photos.py foo.jpg` or
`python rename-photos.py --no-preserve-filenames foo,jpg`

Batch rename files in a folder with:
`find /path/to/folder/ -type f -exec ./rename-photos.py {} \;`

# TODO
- [ ] Fix macOS creation dates being newer than modification dates. Will be a
command line flag.

- [ ] Allow passing in a path to a folder and rename all photos in that folder