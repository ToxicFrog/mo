from __future__ import print_function

import argparse
import os

class FlagAction(argparse.Action):
  def __init__(self, *args, **kwargs):
    super(FlagAction, self).__init__(*args, **kwargs)

  def __call__(self, parser, namespace, values, option_string=None, **kwargs):
    if option_string.startswith('--no-'):
      setattr(namespace, self.dest, False)
    else:
      setattr(namespace, self.dest, True)


class FallbackAction(argparse.Action):
  def __init__(self, fn=None, *args, **kwargs):
    super(FallbackAction, self).__init__(*args, **kwargs)
    self._fn = fn

  def __call__(self, parser, namespace, values, option_string=None, **kwargs):
    self._fn(namespace, values, option_string)

class ArgsFallback(object):
  def __init__(self, wrapped, default):
    self._dict = wrapped
    self._default = default

  def __getitem__(self, key):
    return self._dict.get(key, self._default)

  def __setitem__(self, key, value):
    self._dict[key] = value

  def __contains__(self, key):
    if '=' in key:
      return key in self._dict
    return key.startswith("--")


class MOParser(argparse.ArgumentParser):
  def __init__(self, *args, **kwargs):
    super(MOParser, self).__init__(*args, **kwargs)

  def add_flag(self, name, default, help):
    self.add_argument('--' + name, '--no-' + name, nargs=0, dest=name.replace("-", "_"), help=help, default=default, action=FlagAction)

  def add_subcommand(self, *args, **kwargs):
    return subparsers.add_parser(*args, **kwargs)

  def add_fallback(self, fn):
    self._option_string_actions = ArgsFallback(self._option_string_actions, FallbackAction(option_strings=[], dest="fallback", nargs=1, fn=fn))


parser = MOParser(description="mo -- the music organizer")
subparsers = parser.add_subparsers(help='subcommands')

