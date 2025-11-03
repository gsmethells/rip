# Copyright (C) 2003 Gregory J. Smethells
# Copyright (C) 2025 Gregory J. Smethells
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

"""Unit tests for config module."""

import pytest
import rip.config as config
import rip.exceptions as exceptions
from pathlib import Path


def test_configCreatesDefaultRiprc(tmp_path, monkeypatch):
  """Test that Config creates default ~/.riprc if it doesn't exist."""

  riprc = tmp_path / '.riprc'

  monkeypatch.setattr(Path, 'home', lambda: tmp_path)

  cfg = config.Config()

  assert riprc.exists()
  assert 'RC FILE VERSION 3' in riprc.read_text()

  assert 'format = "mp3"' in riprc.read_text()


def test_configLoadsExistingRiprc(tmp_path, monkeypatch):
  """Test that Config loads existing ~/.riprc file."""

  riprc = tmp_path / '.riprc'

  riprc.write_text('kbps = 320\nformat = "mp3"\ndev = "/dev/sr0"')
  monkeypatch.setattr(Path, 'home', lambda: tmp_path)

  cfg = config.Config()

  assert cfg.get('kbps') == '320'
  assert cfg.get('format') == 'mp3'
  assert cfg.get('dev') == '/dev/sr0'


def test_configGetReturnsDefault(tmp_path, monkeypatch):
  """Test that Config.get() returns default for missing keys."""

  riprc = tmp_path / '.riprc'

  riprc.write_text('kbps = 192')
  monkeypatch.setattr(Path, 'home', lambda: tmp_path)

  cfg = config.Config()

  assert cfg.get('missing', 'default_value') == 'default_value'
  assert cfg.get('missing') is None


def test_configGetIntConvertsToInt(tmp_path, monkeypatch):
  """Test that Config.getInt() converts values to integers."""

  riprc = tmp_path / '.riprc'

  riprc.write_text('kbps = 256\nquality = 5')
  monkeypatch.setattr(Path, 'home', lambda: tmp_path)

  cfg = config.Config()

  assert cfg.getInt('kbps') == 256
  assert cfg.getInt('quality') == 5
  assert cfg.getInt('missing', 999) == 999


def test_configGetIntReturnsDefaultOnInvalidValue(tmp_path, monkeypatch):
  """Test that Config.getInt() returns default for non-numeric values."""

  riprc = tmp_path / '.riprc'

  riprc.write_text('kbps = not_a_number')
  monkeypatch.setattr(Path, 'home', lambda: tmp_path)

  cfg = config.Config()

  assert cfg.getInt('kbps', 192) == 192


def test_configGetBoolHandlesEmptyString(tmp_path, monkeypatch):
  """Test that Config.getBool() treats empty string as False."""

  riprc = tmp_path / '.riprc'

  riprc.write_text('debug = ""\neject = "true"')
  monkeypatch.setattr(Path, 'home', lambda: tmp_path)

  cfg = config.Config()

  assert cfg.getBool('debug') is False
  assert cfg.getBool('eject') is True
  assert cfg.getBool('missing', True) is True


def test_configGetListSplitsOnWhitespace(tmp_path, monkeypatch):
  """Test that Config.getList() splits values by whitespace."""

  riprc = tmp_path / '.riprc'

  riprc.write_text('lazy = "-c -t -e"\nsuperlazy = "-c -t -e -g"')
  monkeypatch.setattr(Path, 'home', lambda: tmp_path)

  cfg = config.Config()

  assert cfg.getList('lazy') == ['-c', '-t', '-e']
  assert cfg.getList('superlazy') == ['-c', '-t', '-e', '-g']
  assert cfg.getList('missing', ['default']) == ['default']


def test_configStripsQuotes(tmp_path, monkeypatch):
  """Test that Config strips quotes from values."""

  riprc = tmp_path / '.riprc'

  riprc.write_text('format = "opus"\ndev = "/dev/cdrom"')
  monkeypatch.setattr(Path, 'home', lambda: tmp_path)

  cfg = config.Config()

  assert cfg.get('format') == 'opus'
  assert cfg.get('dev') == '/dev/cdrom'


def test_configIgnoresComments(tmp_path, monkeypatch):
  """Test that Config ignores comment lines."""

  riprc = tmp_path / '.riprc'

  riprc.write_text('# This is a comment\nkbps = 192\n# Another comment\nformat = "flac"')
  monkeypatch.setattr(Path, 'home', lambda: tmp_path)

  cfg = config.Config()

  assert cfg.get('kbps') == '192'
  assert cfg.get('format') == 'flac'


def test_configIgnoresEmptyLines(tmp_path, monkeypatch):
  """Test that Config ignores empty lines."""

  riprc = tmp_path / '.riprc'

  riprc.write_text('\n\nkbps = 192\n\n\nformat = "mp3"\n\n')
  monkeypatch.setattr(Path, 'home', lambda: tmp_path)

  cfg = config.Config()

  assert cfg.get('kbps') == '192'
  assert cfg.get('format') == 'mp3'


def test_configRaisesErrorOnInvalidFile(tmp_path, monkeypatch, mocker):
  """Test that Config raises ConfigError if file cannot be read."""

  riprc = tmp_path / '.riprc'

  riprc.write_text('valid = "value"')
  monkeypatch.setattr(Path, 'home', lambda: tmp_path)
  mocker.patch('configparser.ConfigParser.read_string', side_effect=Exception('Parse error'))

  with pytest.raises(exceptions.ConfigError):
    config.Config()
