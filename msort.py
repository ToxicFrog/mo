#!/usr/bin/python2

from __future__ import print_function

import re
import sys
import os

from mutagen.id3 import ID3NoHeaderError
from mutagen.easyid3 import EasyID3

from music import getID3ForFile, findMusic

MUSIC_LIBRARY = '/orias/media/music/_sorted'

options = {
  't': True,  # prefix track
  'a': False, # prefix artist
  'y': False, # run for real
  'd': False, # dirs only
}

class ID3Wrapper(object):
  def __init__(self, id3):
    self._id3 = id3

  def __getattr__(self, key):
    val = self._id3[key][0]
    if key == 'disc' or key == 'track':
      return int(val.split('/')[0])
    return val.replace('/', '-')

  def __contains__(self, key):
    return key in self._id3


def parseArgs(argv):
  paths = []
  i = 1
  while i < len(argv):
    arg = argv[i]
    i += 1
    if arg.startswith('-'):
      flag = arg[1:]
      if flag.lower() == flag:
        options[flag.lower()] = True
      else:
        options[flag.lower()] = False
    else:
      paths.append(arg)

  return paths or ['.']


def tagToGroup(id3):
  # For group we check these three tags, in order, first wins:
  # TIT1, Content Group (group)
  # TPE1, Artist (artist)
  # TPE2, Album Artist (performer)
  if 'group' in id3:
    group = id3.group
  elif 'artist' in id3:
    group = id3.artist
  elif 'performer' in id3:
    group = id3.performer
  else:
    raise KeyError('group')

  if 'supergroup' in id3:
    return os.path.join(id3.supergroup, group)
  else:
    return group


def tagToPrefix(id3):
  prefix = ''
  if options['t']:
    if 'disc' in id3:
      prefix += ('%d' % id3.disc)
    prefix += ('%02d - ' % id3.track)
  if options['a']:
    prefix += ('%s - ' % id3.artist)
  return prefix


def newPath(file):
  id3 = ID3Wrapper(getID3ForFile(file))
  (_, ext) = os.path.splitext(file)

  return '{library}/{genre}/{group}/{album}/{prefix}{title}{ext}'.format(
    library=MUSIC_LIBRARY,
    genre=id3.genre,
    group=tagToGroup(id3),
    album=id3.album,
    prefix=tagToPrefix(id3),
    title=id3.title,
    ext=ext)


dirs = set()
def mkDirFor(file):
  dir = os.path.dirname(file)
  if os.path.exists(dir) or dir in dirs:
    return
  print(dir)
  if options['y']:
    os.makedirs(dir)
  else:
    dirs.add(dir)


def moveFile(src, dst):
  print('\t%s' % dst)
  if options['y']:
    os.rename(src, dst)

def main(argv):
  paths = parseArgs(argv)
  for i,src in enumerate(findMusic(paths)):
    # generate path for file
    # move file into path
    try:
      dst = newPath(src)
      mkDirFor(dst)
      if not options['d']:
        moveFile(src, dst)
    except KeyError as e:
      print("Error sorting file '%s': missing tag %s" % (src, e))
    except Exception as e:
      print("Error sorting file '%s': %s" % (src, e))


if __name__ == '__main__':
  main(sys.argv)

