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
subparser = parser.add_subcommand('sort', 
  help='organize files based on tags',
  description="""
    The --file-name and --dir-name arguments can contain {tags}. In addition to the usual (disc,
    track, genre, etc), it supports the special tags "category" (the extension tag TIT0) and
    "group" (whichever of content-group, artist, composer, or performer it finds first).

    If a {tag} ends with ?, it will be treated as "" if missing. Otherwise, if it encounters a
    file missing that tag, it will report an error and exit.

    It is recommended that you run first with --dry-run (the default). Use --no-dry-run to
    actually move the files.
  """)

subparser.add_argument('paths', type=str, nargs='*', default=["."],
  help='paths to search for music files in, default %(default)s')
subparser.add_argument('--library', type=str,
  help='path to music library',
  default=os.path.join(os.getenv('HOME'), 'Music'))
subparser.add_argument('--dir-name', type=str, 
  help='pattern for destination directory; default %(default)s',
  default='{library}/{genre}/{category?}/{group}/{album}')
subparser.add_flag('dry-run', True,
  help='report only, do not actually move any files')
subparser.add_flag('dirs-only', False,
  help='create destination directories but do not move any files')

sp_group = subparser.add_mutually_exclusive_group()
sp_group.add_argument('--file-name', type=str,
  help='pattern for destination files; default %(default)s',
  default='{title}')
sp_group.add_argument('--prefix-track',
  help='as --file-name="%(const)s"',
  action='store_const', dest='file_name', const='{disc?}{track} - {title}')
sp_group.add_argument('--prefix-artist',
  help='as --file-name="%(const)s"',
  action='store_const', dest='file_name', const='{artist} - {title}')
sp_group.add_argument('--prefix-both',
  help='enables both --prefix-track and --prefix-artist',
  action='store_const', dest='file_name', const='{disc?}{track} - {artist} - {title}')

class ID3Wrapper(dict):
  def __init__(self, id3):
    self._id3 = id3

  def __getattr__(self, key):
    return self[key]

  def __getitem__(self, key):
    return self._id3[key][0].replace('/', '-')

  def __contains__(self, key):
    return key in self._id3

  @property
  def disc(self):
    return self._id3['disc'][0].split('/')[0]

  @property
  def track(self):
    return self._id3['track'][0].split('/')[0]

  @property
  def group(self):
    if 'group' in self._id3:
      return self._id3['group']
    if 'artist' in self._id3:
      return self._id3['artist']
    if 'composer' in self._id3:
      return self._id3['composer']
    if 'performer' in self._id3:
      return self._id3['performer']
    raise KeyError('group')

  def asDict(self):
    return { key: value for (key, value) in self._id3.iteritems() }


def parseTemplate(tmpl, id3, fields):
  def fillField(key):
    key = key.group(1)
    optional = False
    if key.endswith('?'):
      key = key[:-1]
      optional = True
    if key not in fields:
      if key in id3:
        fields[key] = id3[key]
      elif not optional:
        raise KeyError(key)
      else:
        return ''
    return '{' + key + '}'
  return re.sub('{(.+?)}', fillField, tmpl)


def newPath(file):
  id3 = ID3Wrapper(getID3ForFile(file))
  (_, ext) = os.path.splitext(file)

  template = os.path.join(options.dir_name, options.file_name) + ext
  kwargs = { 'library': options.library }
  template = parseTemplate(template, id3, kwargs)

  return template.format(**kwargs)


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

