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

def merge_rc_section(rc, section, defaults):
  if rc.has_section(section):
    for key,value in rc.items(section):
      defaults[key] = utf8(value)

def optionxform(name):
  return name.replace('-', '_')

def parse_rc(file, section):
  defaults = {}
  parser = RawConfigParser()
  parser.optionxform = optionxform
  parser.read(file)
  merge_rc_section(parser, 'core', defaults)
  merge_rc_section(parser, section, defaults)
  return defaults

def main(options):
  options.func(options)

if __name__ == "__main__":
  import codecs
  sys.stdout = codecs.getwriter('utf8')(sys.stdout)
  options = parser.parse_args()
  parser.set_defaults(**parse_rc(os.path.expanduser('~/.morc'), options.command))
  # re-parse with the configuration file merged in
  main(parser.parse_args())
