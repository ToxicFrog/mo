#!/usr/bin/python2

from __future__ import print_function

import re
import sys
import os

from mutagen.id3 import ID3NoHeaderError
from mutagen.easyid3 import EasyID3

from music import getID3ForFile, findMusic

MUSIC_FILE_EXTENSIONS = ( ".mp3", ".ogg", ".flac", ".m4a", ".aac" )

# easyID3 already supports album, artist, title, genre
EasyID3.RegisterTextKey("track", "TRCK")
EasyID3.RegisterTextKey("disc", "TPOS")
EasyID3.RegisterTextKey("group", "TIT1")
EasyID3.RegisterTXXXKey("supergroup", "TIT0")


def setTag(id3, key, value):
  key = key.lower()
  if key.endswith("?"):
    key = key[:-1]
    if key in id3:
      return
  id3[key] = value

def autoTag(id3, pattern, file):
  fields = re.findall(r"\[(.*?)\]", pattern)
  pattern = re.sub(r"([^a-zA-Z0-9_\[\]])", r"\\\1", pattern)
  pattern = re.sub(r"\[.*?\]", "([^/]+)", pattern)
  values = re.search(pattern, file)
  if not values:
    print("Warning: no match for " + pattern)
    return

  for key,value in zip(fields, values.groups()):
    if key:
      setTag(id3, key, value)


def parseArgs(argv):
  i = 1

  # parse tags
  tags = []
  while i < len(argv):
    arg = argv[i]
    if arg == "--":
      i += 1
      break
    elif arg.startswith("--"):
      tags.append((arg[2:].lower(), argv[i+1]))
      i += 2
    else:
      break

  # parse paths
  paths = argv[i:]
  if not paths:
    paths = ["."]

  return (tags,paths)


def main(argv):
  (tags,paths) = parseArgs(argv)

  paths = findMusic(paths)

  for i,file in enumerate(paths):
    id3 = getID3ForFile(file)
    for tag in tags:
      if tag[0].startswith("auto"):
        autoTag(id3, tag[1], file)
      else:
        setTag(id3, tag[0], tag[1])

    sys.stdout.write("\r[%d/%d] %s    " % (i, len(paths), file))
    sys.stdout.flush()
    id3.save(filename=file)
    #print(id3)
  sys.stdout.write("\r\033[K[%d/%d] DONE    \n" % (len(paths), len(paths)))

if __name__ == "__main__":
  main(sys.argv)

