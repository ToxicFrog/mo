#!/usr/bin/python2

from __future__ import print_function

import re
import sys
import os

from mutagen.id3 import ID3NoHeaderError
from mutagen.easyid3 import EasyID3

from music import getID3ForFile, findMusic
from args import parser, subparsers

options = None
subparser = parser.add_subcommand('sort', help='organize files based on tags')

subparser.add_argument('--library', type=str, help='path to music library', default=os.path.join(os.getenv('HOME'), "Music"))
subparser.add_flag('artist', False, 'prefix file name with artist')
subparser.add_flag('track', True, 'prefix file name with disc (if set) and track number')
subparser.add_flag('dry-run', True, 'report only, do not actually move any files')
subparser.add_flag('dirs-only', False, 'create destination directories but do not move any files')
subparser.add_argument('paths', type=str, nargs='*', default=["."], help='paths to search for music files in, default "."')

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
  if options.track:
    if 'disc' in id3:
      prefix += ('%d' % id3.disc)
    prefix += ('%02d - ' % id3.track)
  if options.artist:
    prefix += ('%s - ' % id3.artist)
  return prefix


def newPath(file):
  id3 = ID3Wrapper(getID3ForFile(file))
  (_, ext) = os.path.splitext(file)

  return '{library}/{genre}/{group}/{album}/{prefix}{title}{ext}'.format(
    library=options.library,
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
  if not options.dry_run:
    os.makedirs(dir)
  else:
    dirs.add(dir)


def moveFile(src, dst):
  print('\t%s' % dst)
  if not options.dry_run:
    os.rename(src, dst)


def main(_options):
  global options
  options = _options

  for i,src in enumerate(findMusic(options.paths)):
    try:
      dst = newPath(src)
      mkDirFor(dst)
      if not options.dirs_only:
        moveFile(src, dst)
    except KeyError as e:
      print("Error sorting file '%s': missing tag %s" % (src, e))
    except OSError as e:
      print("Error sorting file '%s': %s" % (src, e))

subparser.set_defaults(func=main)
if __name__ == '__main__':
  main(parser.parse_args())

