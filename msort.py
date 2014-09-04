#!/usr/bin/python2

from __future__ import print_function

import re
import sys
import os
import shutil

from string import Formatter

from mutagen.id3 import ID3NoHeaderError
from mutagen.easyid3 import EasyID3

from music import findMusic
from args import parser, subparsers

def utf8(str):
  if isinstance(str, unicode):
    return str
  return unicode(str, 'utf-8')

options = None
subparser = parser.add_subcommand('sort',
  help='organize files based on tags',
  description="""
    Moves or copies files into the path specified by --library, --dir-name, and
    --file-name, replacing {tag} with the contents of that tag in each file
    being moved. Dry-run by default; use --go to actually make changes.
  """)

subparser.add_argument('paths', type=utf8, nargs='*', default=[u"."],
  help='paths to search for music files in, default %(default)s')
subparser.add_argument('--library', type=utf8,
  help='path to music library',
  default=os.path.join(os.getenv('HOME'), 'Music'))
subparser.add_argument('--dir-name', type=utf8,
  help='pattern for destination directory; default %(default)s',
  default='{library}/{genre}/{category?}/{group/artist/composer/performer}/{album}')
subparser.add_argument('--safe-paths', type=utf8, metavar='PATTERN',
  help='replace characters not normally allowed in filenames; ' +
       'understands "linux", "windows", or a list of characters; default "%(default)s"',
  default='linux')
subparser.add_argument('--safe-char', type=utf8, metavar='CHAR',
  help='replace characters removed by --safe-paths with this, default "%(default)s"',
  default='-')
subparser.add_argument('--mode', type=utf8, metavar='MODE',
  help='whether to move, copy, hardlink, or symlink the files, default "%(default)s"',
  default='move')
subparser.add_flag('go', False,
  help='actually move the files (default is to preview results)')
subparser.add_flag('dirs-only', False,
  help='create destination directories but do not move any files')
subparser.add_flag('skip-existing', False,
  help='skip and report files that already exist')

sp_group = subparser.add_mutually_exclusive_group()
sp_group.add_argument('--file-name', type=utf8,
  help='pattern for destination files; default %(default)s',
  default='{title}')
sp_group.add_argument('--prefix-track',
  help='as --file-name="%(const)s"',
  action='store_const', dest='file_name', const='{disc?}{track!d:02d} - {title}')
sp_group.add_argument('--prefix-artist',
  help='as --file-name="%(const)s"',
  action='store_const', dest='file_name', const='{artist} - {title}')
sp_group.add_argument('--prefix-both',
  help='enables both --prefix-track and --prefix-artist',
  action='store_const', dest='file_name', const='{disc?}{track!d:02d} - {artist} - {title}')
sp_group.add_argument('--no-prefix',
  help='disables all --prefix options even if set in config file',
  action='store_const', dest='file_name', const='{title}')

class MusicPathFormatter(Formatter):
  _conversions = {
    'd': int,
    'f': float,
  }

  def __init__(self, tags):
    self._tags = tags

  def make_safe(self, path):
    path = utf8(path)

    def make_tr(chars):
      return { ord(char): options.safe_char for char in chars }

    if options.safe_paths == 'linux':
      # replace /
      return path.translate(make_tr(u'/'))
    elif options.safe_paths == 'windows':
      # replace <>:"/\|?*
      return path.translate(make_tr(u'<>:"/\\|?*'))
    elif options.safe_paths:
      # replace any character in --safe-paths
      return path.translate(make_tr(options.safe_paths))
    return path

  def get_value(self, key, args, kwargs):
    optional = False
    if '/' in key:
      for subkey in key.split('/'):
        try:
          return self.get_value(subkey, args, kwargs)
        except:
          pass
      raise KeyError(key)
    if key.endswith('?'):
      key = key[:-1]
      optional = True
    if key in kwargs:
      return kwargs[key]
    if hasattr(self._tags, key):
      return self.make_safe(getattr(self._tags, key))
    if optional:
      return ''
    raise KeyError(key)

  def convert_field(self, value, conversion):
    if conversion in self._conversions:
      return self._conversions[conversion](value)
    return super(MusicPathFormatter, self).convert_field(value, conversion)


def newPath(tags):
  (_, ext) = os.path.splitext(tags.file)
  template = os.path.join(options.dir_name, options.file_name) + ext

  return MusicPathFormatter(tags).format(
    template,
    library=options.library)


dirs = set()
def mkDirFor(file):
  dir = os.path.dirname(file)
  if dir in dirs:
    return
  print(dir)
  dirs.add(dir)
  if options.go and not os.path.exists(dir):
    os.makedirs(dir)


movers = {
  'move': shutil.move,
  'copy': shutil.copy2,
  'symlink': os.symlink,
  'hardlink': os.link,
}
def moveFile(src, dst, skipped):
  if os.path.exists(dst) and options.skip_existing:
    skipped.append(dst)
    return
  print('\t%s' % os.path.basename(dst))
  if options.go:
    movers[options.mode](src, dst)


def main(_options):
  global options
  options = _options
  skipped = []

  for i,tags in enumerate(sorted(findMusic(options.paths), key=lambda x: x.file)):
    try:
      dst = newPath(tags)
      mkDirFor(dst)
      if not options.dirs_only:
        moveFile(tags.file, dst, skipped)
    except KeyError as e:
     print("Error sorting file '%s': missing tag %s" % (tags.file, e))
    except OSError as e:
      print("Error sorting file '%s': %s" % (tags.file, e))
  if skipped:
    print("\n\t==== SKIPPED ====\n")
    for file in skipped:
      print(file)

subparser.set_defaults(func=main, command='sort')
if __name__ == '__main__':
  main(parser.parse_args())

