#!/usr/bin/python2

from __future__ import print_function

import re
import sys
import os

from mutagen.id3 import ID3NoHeaderError
from mutagen.easyid3 import EasyID3

from music import findMusic
from args import parser, subparsers

subparser = parser.add_subcommand('tag', help='tag files in bulk')
subparser.add_argument('--<TAG>=', metavar='', help='clear TAG in all files')
subparser.add_argument('--<TAG>=<VALUE>', metavar='', help='set TAG to VALUE in all files')
subparser.add_argument('--<TAG>?=<VALUE>', metavar='', help='set TAG to VALUE only in files missing TAG')
subparser.add_argument('--auto=<PATTERN>', metavar='', help='automatically set tags based on PATTERN')
subparser.add_argument('paths', type=str, nargs='*', default=["."], help='paths to search for music files in, default "."')

def parseArg(options, values, arg):
  if not hasattr(options, 'tags'):
    setattr(options, 'tags', [])
  options.tags.append((arg[2:].lower(), values[0]))

subparser.add_fallback(parseArg)


def setTag(id3, key, value):
  key = key.lower()
  if key.endswith("?"):
    key = key[:-1]
    if key in id3:
      return
  if value == '':
    if key in id3: # attempting to delete a missing key throws KeyError?!
      del(id3[key])
  else:
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


def main(options):
  music = findMusic(options.paths)

  for i,tags in enumerate(music):
    for tag in options.tags:
      if tag[0].startswith("auto"):
        autoTag(tags, tag[1], file)
      else:
        setTag(tags, tag[0], tag[1])

    sys.stdout.write("\r[%d/%d] %s    " % (i, len(music), tags.file))
    sys.stdout.flush()
    tags.save()
  sys.stdout.write("\r\033[K[%d/%d] DONE    \n" % (len(music), len(music)))

subparser.set_defaults(func=main)
if __name__ == "__main__":
  main(parser.parse_args())

