# Copyright (C) 2003 Gregory J. Smethells
# Copyright (C) 2025 Gregory J. Smethells
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

"""Unit tests for ripper module."""

import pytest
import rip.exceptions as exceptions
import rip.ripper as ripper
import subprocess
from unittest.mock import MagicMock


def test_ripperFindsCdparanoia(tmp_path, mocker):
  """Test Ripper finds cdparanoia on PATH."""

  device = tmp_path / 'cdrom'

  device.touch()
  mocker.patch('rip.utils.findTool', return_value='/usr/bin/cdparanoia')

  rip = ripper.Ripper(device=str(device))

  assert rip.tool == ripper.Ripper.CDPARANOIA
  assert rip.toolPath == '/usr/bin/cdparanoia'


def test_ripperFindsCdda2wavAsFallback(tmp_path, mocker):
  """Test Ripper falls back to cdda2wav if cdparanoia not found."""

  device = tmp_path / 'cdrom'

  device.touch()
  mocker.patch('rip.utils.findTool', side_effect=[None, '/usr/bin/cdda2wav'])

  rip = ripper.Ripper(device=str(device))

  assert rip.tool == ripper.Ripper.CDDA2WAV
  assert rip.toolPath == '/usr/bin/cdda2wav'


def test_ripperRaisesErrorWhenNoRipperFound(tmp_path, mocker):
  """Test Ripper raises RipperNotFoundError when no ripper available."""

  device = tmp_path / 'cdrom'

  device.touch()
  mocker.patch('rip.utils.findTool', return_value=None)

  with pytest.raises(exceptions.RipperNotFoundError):
    ripper.Ripper(device=str(device))


def test_ripperRaisesErrorWhenDeviceNotFound(mocker):
  """Test Ripper raises DeviceError when device doesn't exist."""

  mocker.patch('rip.utils.findTool', return_value='/usr/bin/cdparanoia')

  with pytest.raises(exceptions.DeviceError):
    ripper.Ripper(device='/dev/nonexistent')


def test_ripTrackWithCdparanoia(tmp_path, mocker):
  """Test ripTrack() with cdparanoia."""

  device = tmp_path / 'cdrom'

  device.touch()

  output = tmp_path / 'track.wav'

  mocker.patch('rip.utils.findTool', return_value='/usr/bin/cdparanoia')

  mockRun = mocker.patch('subprocess.run')
  rip = ripper.Ripper(device=str(device))

  rip.ripTrack(1, output)
  mockRun.assert_called_once()

  args = mockRun.call_args[0][0]

  assert '/usr/bin/cdparanoia' in args
  assert '1' in args
  assert str(output) in args


def test_ripTrackWithCdparanoiaUsesParanoiaFlag(tmp_path, mocker):
  """Test ripTrack() uses paranoia flag with cdparanoia."""

  device = tmp_path / 'cdrom'

  device.touch()

  output = tmp_path / 'track.wav'

  mocker.patch('rip.utils.findTool', return_value='/usr/bin/cdparanoia')

  mockRun = mocker.patch('subprocess.run')
  rip = ripper.Ripper(device=str(device), paranoia=True)

  rip.ripTrack(1, output)

  args = mockRun.call_args[0][0]

  assert '-z' in args


def test_ripTrackWithCdparanoiaDisablesParanoia(tmp_path, mocker):
  """Test ripTrack() can disable paranoia mode."""

  device = tmp_path / 'cdrom'

  device.touch()

  output = tmp_path / 'track.wav'

  mocker.patch('rip.utils.findTool', return_value='/usr/bin/cdparanoia')

  mockRun = mocker.patch('subprocess.run')
  rip = ripper.Ripper(device=str(device), paranoia=False)

  rip.ripTrack(1, output)

  args = mockRun.call_args[0][0]

  assert '-Z' in args


def test_ripTrackWithCdparanoiaUsesQuietFlag(tmp_path, mocker):
  """Test ripTrack() uses quiet flag when requested."""

  device = tmp_path / 'cdrom'

  device.touch()

  output = tmp_path / 'track.wav'

  mocker.patch('rip.utils.findTool', return_value='/usr/bin/cdparanoia')

  mockRun = mocker.patch('subprocess.run')
  rip = ripper.Ripper(device=str(device), quiet=True)

  rip.ripTrack(1, output)

  args = mockRun.call_args[0][0]

  assert '-q' in args


def test_ripTrackRaisesErrorOnFailure(tmp_path, mocker):
  """Test ripTrack() raises TrackError when subprocess fails."""

  device = tmp_path / 'cdrom'

  device.touch()

  output = tmp_path / 'track.wav'

  mocker.patch('rip.utils.findTool', return_value='/usr/bin/cdparanoia')
  mocker.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'cmd', stderr='error'))

  rip = ripper.Ripper(device=str(device))

  with pytest.raises(exceptions.TrackError):
    rip.ripTrack(1, output)


def test_queryTracksWithCdparanoia(tmp_path, mocker):
  """Test queryTracks() with cdparanoia."""

  device = tmp_path / 'cdrom'

  device.touch()
  mocker.patch('rip.utils.findTool', return_value='/usr/bin/cdparanoia')

  mockResult = MagicMock()
  mockResult.stderr = '  1. 00:00.00 [00:03.12]\n  2. 00:03.12 [00:04.33]\n  3. 00:07.45 [00:02.15]'

  mocker.patch('subprocess.run', return_value=mockResult)

  rip = ripper.Ripper(device=str(device))
  count = rip.queryTracks()

  assert count == 3


def test_queryTracksRaisesErrorOnFailure(tmp_path, mocker):
  """Test queryTracks() raises TrackError when query fails."""

  device = tmp_path / 'cdrom'

  device.touch()
  mocker.patch('rip.utils.findTool', return_value='/usr/bin/cdparanoia')
  mocker.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'cmd'))

  rip = ripper.Ripper(device=str(device))

  with pytest.raises(exceptions.TrackError):
    rip.queryTracks()
