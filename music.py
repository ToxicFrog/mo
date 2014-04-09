#!/usr/bin/python2

from __future__ import print_function

import re
import sys
import os

from mutagen.id3 import ID3NoHeaderError
from mutagen.easyid3 import EasyID3

MUSIC_FILE_EXTENSIONS = ( ".mp3", ".ogg", ".flac", ".m4a", ".aac" )

# easyID3 already supports album, artist, title, genre
EasyID3.RegisterTextKey("track", "TRCK")
EasyID3.RegisterTextKey("disc", "TPOS")
EasyID3.RegisterTextKey("group", "TIT1")
EasyID3.RegisterTXXXKey("category", "TIT0")


def getID3ForFile(file):
  try:
    id3 = EasyID3(file)
  except ID3NoHeaderError:
    id3 = EasyID3()
  return id3


def findMusic(paths):
  def isMusic(file):
    return file.endswith(MUSIC_FILE_EXTENSIONS)
  return [os.path.join(path, file)
          for root in paths
          for path,_,files in os.walk(root)
          for file in files
          if isMusic(file)]
