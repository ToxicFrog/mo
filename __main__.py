#!/usr/bin/python2

from __future__ import print_function

import re
import sys
import os

from mutagen.id3 import ID3NoHeaderError
from mutagen.easyid3 import EasyID3

import mtag
import msort

HELP_TEXT = """
Usage: mo (tag|sort) [options]
  mo tag {--tag value} [-- paths]
    --tag can be an ID3 field name (--TCON), a common name (--genre), or
    the special tag '--auto', in which case the value is a pattern to
    extract tags from based on the filename. Tag names ending with ? will
    be applied only if that tag is not already set.
  mo sort [--library path] [-a] [-t] [-d] [-y] [paths]
    single-letter options can be capitalized to invert their meaning.
    -a: prefix filenames with artist name
    -t: prefix filenames with disc (if set) and track numbers (default)
    -d: create destination directories but do not move any files.
    -y: actually perform the move (default is dry run)
"""

def mo_help(argv):
  print(HELP_TEXT)


commands = {
  'sort': msort.main,
  'tag': mtag.main,
  'help': mo_help,
}


def main(argv):
  if argv[1] in commands:
    commands[argv[1]]([argv[0]] + argv[2:])
  else:
    print("Unknown command '%s'" % argv[1])


if __name__ == "__main__":
  main(sys.argv)

