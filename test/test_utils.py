# Copyright (C) 2003 Gregory J. Smethells
# Copyright (C) 2025 Gregory J. Smethells
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

"""Unit tests for utils module."""

import pytest
import rip.exceptions as exceptions
import rip.utils as utils
from pathlib import Path
from unittest.mock import patch


def test_parseTracksHandlesSingleTrack():
  """Test parseTracks() with single track numbers."""

  result = utils.parseTracks(['1', '3', '5'])

  assert result == [1, 3, 5]


def test_parseTracksHandlesRanges():
  """Test parseTracks() with track ranges."""

  result = utils.parseTracks(['1-3', '7-9'])

  assert result == [1, 2, 3, 7, 8, 9]


def test_parseTracksHandlesMixedFormat():
  """Test parseTracks() with mix of singles and ranges."""

  result = utils.parseTracks(['1', '3-5', '7', '9-11'])

  assert result == [1, 3, 4, 5, 7, 9, 10, 11]


def test_parseTracksRemovesDuplicates():
  """Test parseTracks() removes duplicate track numbers."""

  result = utils.parseTracks(['1', '2', '1', '3-5', '4'])

  assert result == [1, 2, 3, 4, 5]


def test_parseTracksRaisesErrorOnInvalidNumber():
  """Test parseTracks() raises TrackError for invalid track numbers."""

  with pytest.raises(exceptions.TrackError, match='Invalid track number'):
    utils.parseTracks(['not_a_number'])


def test_parseTracksRaisesErrorOnOutOfRange():
  """Test parseTracks() raises TrackError for out-of-range tracks."""

  with pytest.raises(exceptions.TrackError, match='must be between 1 and 99'):
    utils.parseTracks(['0'])

  with pytest.raises(exceptions.TrackError, match='must be between 1 and 99'):
    utils.parseTracks(['100'])


def test_parseTracksRaisesErrorOnInvalidRange():
  """Test parseTracks() raises TrackError for invalid range format."""

  with pytest.raises(exceptions.TrackError, match='Invalid track range'):
    utils.parseTracks(['5-3'])


def test_sanitizeFilenameRemovesUnsafeCharacters():
  """Test sanitizeFilename() removes unsafe characters."""

  result = utils.sanitizeFilename('test<>:"|?*file')

  assert '<' not in result
  assert '>' not in result
  assert ':' not in result
  assert '"' not in result
  assert '|' not in result
  assert '?' not in result
  assert '*' not in result


def test_sanitizeFilenameReplacesSlashes():
  """Test sanitizeFilename() replaces slashes with hyphens."""

  result = utils.sanitizeFilename('test/file\\name')

  assert '/' not in result
  assert '\\' not in result
  assert '-' in result


def test_sanitizeFilenameReplacesSpacesWithUnderscores():
  """Test sanitizeFilename() replaces spaces with underscores."""

  result = utils.sanitizeFilename('test file name', useUnderscore=True)

  assert result == 'test_file_name'


def test_sanitizeFilenameKeepsSpaces():
  """Test sanitizeFilename() keeps spaces when useUnderscore=False."""

  result = utils.sanitizeFilename('test file name', useUnderscore=False)

  assert result == 'test file name'


def test_sanitizeFilenameReturnsUnknownForEmptyString():
  """Test sanitizeFilename() returns 'unknown' for empty strings."""

  result = utils.sanitizeFilename('')

  assert result == 'unknown'

  result = utils.sanitizeFilename('   ')

  assert result == 'unknown'


def test_findCdDevicesFindsCommonPaths(tmp_path):
  """Test findCdDevices() finds devices at common paths."""

  cdrom = tmp_path / 'cdrom'

  cdrom.touch()

  dvd = tmp_path / 'dvd'

  dvd.touch()

  with patch('rip.utils.Path') as mockPath:
    mockPath.return_value.exists.side_effect = lambda: True
    devices = []

    for path in ['/dev/cdrom', '/dev/dvd']:
      pathObj = Path(path)

      if path == '/dev/cdrom':
        devices.append(pathObj)

    assert len(devices) > 0


def test_findToolFindsToolOnPath(mocker):
  """Test findTool() finds tool on system PATH."""

  mocker.patch('shutil.which', return_value='/usr/bin/lame')

  result = utils.findTool('lame')

  assert result == '/usr/bin/lame'


def test_findToolReturnsNoneWhenNotFound(mocker):
  """Test findTool() returns None when tool not found."""

  mocker.patch('shutil.which', return_value=None)

  result = utils.findTool('nonexistent_tool')

  assert result is None


def test_formatDurationFormatsCorrectly():
  """Test formatDuration() formats seconds as MM:SS."""

  assert utils.formatDuration(0) == '00:00'
  assert utils.formatDuration(59) == '00:59'
  assert utils.formatDuration(60) == '01:00'
  assert utils.formatDuration(125) == '02:05'
  assert utils.formatDuration(3661) == '61:01'


def test_ensureDirectoryCreatesDirectory(tmp_path):
  """Test ensureDirectory() creates directory if it doesn't exist."""

  newDir = tmp_path / 'test' / 'nested' / 'dir'

  utils.ensureDirectory(newDir)
  assert newDir.exists()
  assert newDir.is_dir()


def test_ensureDirectoryHandlesExistingDirectory(tmp_path):
  """Test ensureDirectory() doesn't fail on existing directory."""

  existingDir = tmp_path / 'existing'

  existingDir.mkdir()
  utils.ensureDirectory(existingDir)
  assert existingDir.exists()


def test_getTempWavPathIncludesTrackNumber():
  """Test getTempWavPath() includes track number in path."""

  result = utils.getTempWavPath(5)

  assert '5' in str(result)
  assert result.suffix == '.wav'


def test_getTempWavPathIncludesPid():
  """Test getTempWavPath() includes process ID in path."""

  import os

  result = utils.getTempWavPath(1)

  assert str(os.getpid()) in str(result)
