#!/usr/bin/python2

from __future__ import print_function

import re
import sys
import os
from ConfigParser import RawConfigParser

from mutagen.id3 import ID3NoHeaderError
from mutagen.easyid3 import EasyID3

import mtag
import msort
from args import parser

def utf8(str):
  if isinstance(str, unicode):
    return str
  return unicode(str, 'utf-8')

def optionxform(name):
  return name.replace('-', '_')

def parse_rc(file):
  defaults = {}
  rc = RawConfigParser()
  rc.optionxform = optionxform
  rc.read(file)
  if rc.has_section('core'):
    parser.set_defaults(**{ k: v for (k,v) in rc.items('core') })
  if rc.has_section('tag'):
    mtag.subparser.set_defaults(**{ k: v for (k,v) in rc.items('tag') })
  if rc.has_section('sort'):
    msort.subparser.set_defaults(**{ k: v for (k,v) in rc.items('sort') })
  return defaults

def main(options):
  options.func(options)

if __name__ == "__main__":
  import codecs
  sys.stdout = codecs.getwriter('utf8')(sys.stdout)
  parse_rc(os.path.expanduser('~/.morc'))
  # re-parse with the configuration file merged in
  main(parser.parse_args())
