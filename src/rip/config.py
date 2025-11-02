# Copyright (C) 2003 Gregory J. Smethells
# Copyright (C) 2024 Gregory J. Smethells
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

"""
Configuration management for rip.

Handles loading and parsing ~/.riprc configuration file. Maintains backward
compatibility with the original Perl version's config format.
"""

import configparser
from pathlib import Path
import rip.exceptions as exceptions


class Config:
  """
  Configuration manager for rip.

  Loads configuration from ~/.riprc and provides access to settings with
  appropriate type conversion. Creates a default config file if none exists.
  """

  def __init__(self):
    """Initialize config and load from ~/.riprc."""
    self.rcfile = Path.home() / '.riprc'
    self.preferences = {}
    self._loadConfig()

  def _loadConfig(self):
    """
    Load configuration from ~/.riprc.

    Creates a default configuration file if none exists. Uses configparser
    with a dummy [DEFAULT] section to parse the section-less INI format.

    :raises: ConfigError if config file cannot be read
    """
    if not self.rcfile.exists():
      self._createDefaultConfig()
      return

    try:
      config = configparser.ConfigParser()
      with open(self.rcfile, encoding='utf-8') as f:
        configContent = f.read()

      config.read_string('[DEFAULT]\n' + configContent)

      for key, value in config['DEFAULT'].items():
        value = value.strip('"').strip("'")
        self.preferences[key] = value
    except Exception as e:
      raise exceptions.ConfigError(f'Failed to load {self.rcfile}: {e}') from e

  def _createDefaultConfig(self):
    """Create default ~/.riprc configuration file."""
    defaultContent = '''# ALTER THIS FILE AT YOUR OWN RISK!

# RC FILE VERSION 3 (Python)

# The "default" flags will automatically be given to rip when
# you run it each time. They should look like args on a command-line.
default = ""

# This sets the default flags used for lazy rips.
lazy = "-c -t -e"

# This sets the default flags used for superlazy rips.
superlazy = "-c -t -e"

# Sets the default bitrate (in kbps)
kbps = 192

# Sets the default format (mp3, flac, opus, ogg, m4a)
format = "opus"

# Sets the defaults for quality (only used with -q flag for VBR)
qualityOPUS = 6
qualityLAME = 2
qualityOGGENC = 9

# The default device to find the CD in
dev = "/dev/cdrom"

# Debug mode (set to "true" to keep debug files)
debug = ""
'''
    self.rcfile.write_text(defaultContent, encoding='utf-8')
    self._loadConfig()

  def get(self, key, default=None):
    """
    Get a configuration value.

    :param key: Configuration key
    :param default: Default value if key not found
    :type key: str
    :type default: any
    :rtype: str or None
    """
    return self.preferences.get(key, default)

  def getInt(self, key, default=0):
    """
    Get a configuration value as integer.

    :param key: Configuration key
    :param default: Default value if key not found or conversion fails
    :type key: str
    :type default: int
    :rtype: int
    """
    value = self.get(key)
    if value is None:
      return default

    try:
      return int(value)
    except ValueError:
      return default

  def getBool(self, key, default=False):
    """
    Get a configuration value as boolean.

    Matches Perl behavior: empty string is False, any non-empty value is True.

    :param key: Configuration key
    :param default: Default value if key not found
    :type key: str
    :type default: bool
    :rtype: bool
    """
    value = self.get(key)
    if value is None:
      return default

    return value != ''

  def getList(self, key, default=None):
    """
    Get a configuration value as list of arguments.

    Splits value by whitespace to produce argument list suitable for argparse.

    :param key: Configuration key
    :param default: Default value if key not found
    :type key: str
    :type default: list or None
    :rtype: list
    """
    value = self.get(key)
    if value is None:
      return default if default is not None else []

    return value.split()
