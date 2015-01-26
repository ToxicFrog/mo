#!/usr/bin/python2

from __future__ import print_function

import re
import sys
import os

from mutagen.id3 import ID3NoHeaderError
from mutagen.easyid3 import EasyID3

from music import findMusic
from args import parser, subparsers

def utf8(str):
  if isinstance(str, unicode):
    return str
  return unicode(str, 'utf-8')

subparser = parser.add_subcommand('tag', help='tag files in bulk',
  description="""
    Tag many files, or (with --auto) infer tags from file and directory names.
  """)
subparser.add_argument('--<TAG>=', metavar='', help='clear TAG in all files')
subparser.add_argument('--<TAG>=<VALUE>', metavar='', help='set TAG to VALUE in all files')
subparser.add_argument('--<TAG>?=<VALUE>', metavar='', help='set TAG to VALUE only in files missing TAG')
subparser.add_argument('--auto=<PATTERN>', metavar='', help='automatically set tags based on PATTERN')
subparser.add_argument('paths', type=utf8, nargs='*', default=[u"."], help='paths to search for music files in, default "."')

def parseArg(options, values, arg):
  if not hasattr(options, 'tags'):
    setattr(options, 'tags', [])
  options.tags.append((arg[2:].lower(), utf8(values[0])))

subparser.add_fallback(parseArg)


def setTag(id3, key, value):
  key = key.lower()
  value = utf8(value)
  if key.endswith("?"):
    key = key[:-1]
    if key in id3:
      return
  if key.endswith("@"):
    key = key[:-1]
    if value in id3:
      value = id3[value]
    else:
      sys.stdout.write("\r\x1B[K[ERROR] %s: can't set tag '%s' from '%s'; no value to set from\n" % (file, key, value))
      return
  if value == '':
    if key in id3: # attempting to delete a missing key throws KeyError?!
      del(id3[key])
  else:
    id3[key] = value


def autoTag(id3, pattern, file):
  fields = re.findall(r"\[(.*?)\]", pattern)
  pattern = re.sub(r"([^a-zA-Z0-9_\[\]])", r"\\\1", pattern)
  pattern = re.sub(r"\[.*?\]", "([^/]+?)", pattern)
  values = re.search(pattern, file)
  if not values:
    sys.stdout.write("\r\x1B[K[ERROR] %s: no match for pattern '%s'\n" % (file, pattern))
    return

  for key,value in zip(fields, values.groups()):
    if key:
      setTag(id3, key, value)


def main(options):
  music = findMusic(options.paths)

  for i,tags in enumerate(music):
    try:
      for tag in options.tags:
        if tag[0].startswith("auto"):
          autoTag(tags, tag[1], tags.file)
        else:
          setTag(tags, tag[0], tag[1])
      sys.stdout.write("\r\x1B[K[%d/%d] %s    " % (i, len(music), tags.file))
      sys.stdout.flush()
      tags.save()
    except Exception as e:
      print("ERROR: %s: %s" % (str(e), tags.file))
      print(sys.exc_info()[0])

  sys.stdout.write("\r\x1B[K[%d/%d] DONE    \n" % (len(music), len(music)))

subparser.set_defaults(func=main, command='tag')
if __name__ == "__main__":
  main(parser.parse_args())

