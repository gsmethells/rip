# Copyright (C) 2003 Gregory J. Smethells
# Copyright (C) 2024 Gregory J. Smethells
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

"""
Utility functions for rip.

Provides helper functions for track parsing, filename sanitization,
device discovery, and path handling.
"""

import os
import re
import rip.exceptions as exceptions
import shutil
from pathlib import Path


def parseTracks(trackArgs):
  """
  Parse track numbers from command-line arguments.

  Supports individual tracks (1 2 3) and ranges (1-5 7-9).
  Returns a sorted list of unique track numbers.

  Examples:
    parseTracks(['1', '3-5', '7']) -> [1, 3, 4, 5, 7]
    parseTracks(['1', '2', '1']) -> [1, 2]

  :param trackArgs: List of track number arguments
  :type trackArgs: list
  :rtype: list
  :raises: TrackError if track format is invalid
  """
  tracks = set()

  for arg in trackArgs:
    if '-' in arg:
      try:
        start, end = arg.split('-', 1)
        startNum = int(start)
        endNum = int(end)

        if startNum < 1 or endNum < 1 or startNum > 99 or endNum > 99:
          raise exceptions.TrackError(f'Track numbers must be between 1 and 99: {arg}')

        if startNum > endNum:
          raise exceptions.TrackError(f'Invalid track range (start > end): {arg}')

        tracks.update(range(startNum, endNum + 1))
      except ValueError as e:
        raise exceptions.TrackError(f'Invalid track range format: {arg}') from e
    else:
      try:
        trackNum = int(arg)
        if trackNum < 1 or trackNum > 99:
          raise exceptions.TrackError(f'Track number must be between 1 and 99: {trackNum}')

        tracks.add(trackNum)
      except ValueError as e:
        raise exceptions.TrackError(f'Invalid track number: {arg}') from e

  return sorted(tracks)


def sanitizeFilename(filename, useUnderscore=True):
  """
  Sanitize filename by removing/replacing unsafe characters.

  Removes characters that could cause issues with filesystems or shells.
  Optionally replaces spaces with underscores.

  :param filename: Filename to sanitize
  :param useUnderscore: Replace spaces with underscores if True
  :type filename: str
  :type useUnderscore: bool
  :rtype: str
  """
  safe = filename

  safe = re.sub(r'[<>:"|?*\x00-\x1f]', '', safe)
  safe = re.sub(r'[/\\]', '-', safe)
  safe = re.sub(r'[;\[\]\{\}`$!&]', '', safe)

  safe = safe.strip()
  safe = re.sub(r'\.+$', '', safe)

  if useUnderscore:
    safe = safe.replace(' ', '_')

  if not safe:
    safe = 'unknown'

  return safe


def findCdDevices():
  """
  Find available CD/DVD devices on the system.

  Checks common device paths and /dev/disk/by-id for USB drives.

  :rtype: list
  """
  devices = []
  commonPaths = ['/dev/cdrom', '/dev/dvd', '/dev/sr0', '/dev/sr1', '/dev/sr2']

  for path in commonPaths:
    devicePath = Path(path)
    if devicePath.exists():
      devices.append(devicePath)

  diskByIdDir = Path('/dev/disk/by-id')
  if diskByIdDir.exists():
    for device in diskByIdDir.glob('usb-*'):
      deviceName = device.name.lower()
      if 'cd' in deviceName or 'dvd' in deviceName:
        realDevice = device.resolve()
        if realDevice not in devices:
          devices.append(realDevice)

  return devices


def findTool(toolName):
  """
  Find a tool on the system PATH.

  :param toolName: Name of the tool to find
  :type toolName: str
  :rtype: str or None
  :return: Full path to tool if found, None otherwise
  """
  toolPath = shutil.which(toolName)
  return toolPath


def formatDuration(seconds):
  """
  Format duration in seconds as MM:SS.

  :param seconds: Duration in seconds
  :type seconds: int or float
  :rtype: str
  """
  minutes = int(seconds // 60)
  secs = int(seconds % 60)
  return f'{minutes:02d}:{secs:02d}'


def ensureDirectory(dirPath):
  """
  Ensure directory exists, creating it if necessary.

  :param dirPath: Path to directory
  :type dirPath: Path or str
  :raises: OSError if directory cannot be created
  """
  path = Path(dirPath)
  path.mkdir(parents=True, exist_ok=True)


def getTempWavPath(trackNum):
  """
  Generate temporary WAV file path for a track.

  Uses process ID to ensure uniqueness across concurrent runs.

  :param trackNum: Track number
  :type trackNum: int
  :rtype: Path
  """
  pid = os.getpid()
  return Path(f'rip_temp_{pid}_{trackNum}.wav')
