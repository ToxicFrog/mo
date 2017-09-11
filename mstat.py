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

subparser = parser.add_subcommand('stat', help='display file information',
  description="""
    Display tags for one or many files.
  """)
subparser.add_argument('paths', type=utf8, nargs='*', default=[u"."], help='paths to search for music files in, default "."')


def main(options):
  music = findMusic(options.paths)

  for i,tags in enumerate(music):
    print("[%d/%d] %s" % (i, len(music), tags.file))
    print("", type(tags))
    for k,v in enumerate(tags._tags):
      print("", k, v, tags[v])
    print("")

subparser.set_defaults(func=main, command='stat')
if __name__ == "__main__":
  main(parser.parse_args())
