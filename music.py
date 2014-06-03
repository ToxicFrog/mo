#!/usr/bin/python2

from __future__ import print_function

import re
import sys
import os
import os.path

import mutagen.id3
from mutagen.id3 import ID3,ID3NoHeaderError,Frames
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis

MUSIC_FILE_EXTENSIONS = ( ".mp3", ".ogg", ".flac", ".m4a", ".aac" )

class TagWrapper(object):
  _tagmap = {}

  @classmethod
  def canWrap(_, file):
    raise NotImplementedError()

  def _wrap(self, file):
    raise NotImplementedError()

  def __init__(self, file):
    self.__dict__['file'] = file
    self.__dict__['_tags'] = self._wrap(file)

  def __getattr__(self, key):
    return self[key]

  def __getitem__(self, key):
    key = self._tagmap.get(key, key)
    return self._tags[key][0] #.replace('/', '-')

  def __setattr__(self, key, value):
    self[key] = value

  def __setitem__(self, key, value):
    key = self._tagmap.get(key, key)
    self._tags[key] = value

  def __contains__(self, key):
    key = self._tagmap.get(key, key)
    return key in self._tags

  def __delitem__(self, key):
    key = self._tagmap.get(key, key)
    del(self._tags[key])

  def save(self, file=None):
    if file is None:
      file = self.file
    self._tags.save(filename=file)

  @property
  def disc(self):
    return re.match('^([0-9]+)', self['disc']).groups()[0]

  @property
  def track(self):
    return re.match('^([0-9]+)', self['track']).groups()[0]


class ID3Wrapper(TagWrapper):
  _tagmap = {
    'album':      'TALB',
    'arranger':   'TPE4',
    'artist':     'TPE1',
    'category':   'TXXX:TIT0',
    'composer':   'TCOM',
    'conductor':  'TPE3',
    'disc':       'TPOS',
    'genre':      'TCON',
    'group':      'TIT1',
    'performer':  'TPE2',
    'title':      'TIT2',
    'track':      'TRCK',
  }

  @classmethod
  def canWrap(_, file):
    return file.endswith(".mp3")

  def _wrap(self, file):
    try:
      return ID3(file)
    except ID3NoHeaderError:
      return ID3()

  def __setitem__(self, key, value):
    key = self._tagmap.get(key, key)
    if key.startswith('TXXX:'): # user-defined text frame
      subkey = key.split(':')[-1]
      self._tags.add(mutagen.id3.TXXX(encoding=3, text=value, desc=subkey))
    else:
      self._tags.add(Frames[key](encoding=3, text=value))


class FLACWrapper(TagWrapper):
  _tagmap = {
    'disc':       'discnumber',
    'group':      'contentgroup',
    'track':      'tracknumber',
  }

  @classmethod
  def canWrap(_, file):
    return file.endswith(".flac")

  def _wrap(self, file):
    return FLAC(file)


class VorbisWrapper(TagWrapper):
  _tagmap = {
    'disc':       'discnumber',
    'group':      'contentgroup',
    'track':      'tracknumber',
  }

  @classmethod
  def canWrap(_, file):
    return file.endswith(".ogg")

  def _wrap(self, file):
    return OggVorbis(file)


class GuessWrapper(TagWrapper):
  @classmethod
  def canWrap(_, file):
    return True

  def _wrap(self, file):
    print("WARNING: guessing tag type of file %s" % file)
    return mutagen.File(file)


def getTagsForFile(file):
  for wrapper in [FLACWrapper, VorbisWrapper, ID3Wrapper, GuessWrapper]:
    if wrapper.canWrap(file):
      return wrapper(file)
  raise ValueError("No tag handler found for file '%s'")


def findMusic(paths):
  def isMusic(file):
    return file.endswith(MUSIC_FILE_EXTENSIONS)
  return [getTagsForFile(os.path.join(path, file))
          for root in paths
          for path,_,files in os.walk(root)
          for file in files
          if isMusic(file)] + [
          getTagsForFile(file)
          for file in paths
          if os.path.isfile(file)]
