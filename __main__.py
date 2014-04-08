#!/usr/bin/python2

from __future__ import print_function

import re
import sys
import os

from mutagen.id3 import ID3NoHeaderError
from mutagen.easyid3 import EasyID3

import mtag
import msort
from args import parser

def main(options):
  options.func(options)

if __name__ == "__main__":
  main(parser.parse_args())

