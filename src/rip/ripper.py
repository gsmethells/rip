# Copyright (C) 2003 Gregory J. Smethells
# Copyright (C) 2024 Gregory J. Smethells
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

"""
CD ripping functionality for rip.

Provides CD ripping via cdparanoia or cdda2wav. Automatically discovers
available rippers and wraps them with a unified interface.
"""

import logging
import rip.exceptions as exceptions
import rip.utils as utils
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class Ripper:
  """
  CD ripper that wraps cdparanoia or cdda2wav.

  Automatically detects which ripper is available and provides a unified
  interface for ripping audio CD tracks to WAV files.
  """

  CDPARANOIA = 'cdparanoia'
  CDDA2WAV = 'cdda2wav'

  def __init__(self, device='/dev/cdrom', paranoia=True, speed=None, quiet=False, verbose=False):
    """
    Initialize the ripper.

    :param device: CD device path
    :param paranoia: Enable paranoia mode (extra error correction)
    :param speed: CD read speed (None for default)
    :param quiet: Suppress ripper output
    :param verbose: Enable verbose ripper output
    :type device: str or Path
    :type paranoia: bool
    :type speed: int or None
    :type quiet: bool
    :type verbose: bool
    :raises: RipperNotFoundError if no ripper found
    :raises: DeviceError if device does not exist
    """
    self.device = Path(device)
    self.paranoia = paranoia
    self.speed = speed
    self.quiet = quiet
    self.verbose = verbose
    self.tool = None
    self.toolPath = None

    if not self.device.exists():
      raise exceptions.DeviceError(f'CD device not found: {self.device}')

    self._findRipper()

  def _findRipper(self):
    """
    Find available ripper tool.

    Searches for cdparanoia first, then cdda2wav.

    :raises: RipperNotFoundError if no ripper found
    """
    for tool in [self.CDPARANOIA, self.CDDA2WAV]:
      toolPath = utils.findTool(tool)
      if toolPath:
        self.tool = tool
        self.toolPath = toolPath
        logger.info(f'Found ripper: {tool} at {toolPath}')
        return

    raise exceptions.RipperNotFoundError('No CD ripper found. Please install cdparanoia or cdda2wav.')

  def ripTrack(self, trackNum, outputPath):
    """
    Rip a single track from CD to WAV file.

    :param trackNum: Track number to rip (1-based)
    :param outputPath: Output WAV file path
    :type trackNum: int
    :type outputPath: Path or str
    :raises: TrackError if ripping fails
    """
    outputPath = Path(outputPath)

    if self.tool == self.CDPARANOIA:
      self._ripWithCdparanoia(trackNum, outputPath)
    elif self.tool == self.CDDA2WAV:
      self._ripWithCdda2wav(trackNum, outputPath)
    else:
      raise exceptions.RipperNotFoundError('No ripper tool configured')

  def _ripWithCdparanoia(self, trackNum, outputPath):
    """
    Rip track using cdparanoia.

    :param trackNum: Track number to rip
    :param outputPath: Output WAV file path
    :type trackNum: int
    :type outputPath: Path
    :raises: TrackError if ripping fails
    """
    cmd = [self.toolPath]

    if self.paranoia:
      cmd.append('-z')
    else:
      cmd.append('-Z')

    if self.speed:
      cmd.extend(['-S', str(self.speed)])

    if self.quiet:
      cmd.append('-q')

    if self.verbose:
      cmd.append('-v')

    cmd.extend(['-d', str(self.device)])
    cmd.append(str(trackNum))
    cmd.append(str(outputPath))

    logger.info(f'Ripping track {trackNum} with cdparanoia')
    logger.debug(f'Command: {" ".join(cmd)}')

    try:
      result = subprocess.run(cmd, check=True, capture_output=True, text=True)
      if not self.quiet and result.stderr:
        logger.info(result.stderr)
    except subprocess.CalledProcessError as e:
      raise exceptions.TrackError(f'Failed to rip track {trackNum}: {e.stderr}') from e

  def _ripWithCdda2wav(self, trackNum, outputPath):
    """
    Rip track using cdda2wav.

    :param trackNum: Track number to rip
    :param outputPath: Output WAV file path
    :type trackNum: int
    :type outputPath: Path
    :raises: TrackError if ripping fails
    """
    outputBase = str(outputPath.with_suffix(''))
    cmd = [self.toolPath, '-D', str(self.device), '-t', str(trackNum), '-O', 'wav', outputBase]

    if self.speed:
      cmd.extend(['-S', str(self.speed)])

    if self.paranoia:
      cmd.append('-paranoia')

    if self.quiet:
      cmd.append('-q')

    if self.verbose:
      cmd.append('-v')

    logger.info(f'Ripping track {trackNum} with cdda2wav')
    logger.debug(f'Command: {" ".join(cmd)}')

    try:
      result = subprocess.run(cmd, check=True, capture_output=True, text=True)
      if not self.quiet and result.stderr:
        logger.info(result.stderr)
    except subprocess.CalledProcessError as e:
      raise exceptions.TrackError(f'Failed to rip track {trackNum}: {e.stderr}') from e

  def queryTracks(self):
    """
    Query CD for number of tracks.

    :rtype: int
    :raises: TrackError if query fails
    """
    if self.tool == self.CDPARANOIA:
      return self._queryTracksWithCdparanoia()
    elif self.tool == self.CDDA2WAV:
      return self._queryTracksWithCdda2wav()
    else:
      raise exceptions.RipperNotFoundError('No ripper tool configured')

  def _queryTracksWithCdparanoia(self):
    """
    Query number of tracks using cdparanoia.

    :rtype: int
    :raises: TrackError if query fails
    """
    cmd = [self.toolPath, '-d', str(self.device), '-Q']

    try:
      result = subprocess.run(cmd, check=True, capture_output=True, text=True)
      lines = result.stderr.split('\n')
      trackCount = 0

      for line in lines:
        if line.strip() and line[0].isdigit():
          parts = line.split('.')
          if parts and parts[0].strip().isdigit():
            trackNum = int(parts[0].strip())
            trackCount = max(trackCount, trackNum)

      return trackCount
    except (subprocess.CalledProcessError, ValueError) as e:
      raise exceptions.TrackError(f'Failed to query CD: {e}') from e

  def _queryTracksWithCdda2wav(self):
    """
    Query number of tracks using cdda2wav.

    :rtype: int
    :raises: TrackError if query fails
    """
    cmd = [self.toolPath, '-D', str(self.device), '-J', '-g']

    try:
      result = subprocess.run(cmd, check=True, capture_output=True, text=True)
      lines = result.stdout.split('\n')
      trackCount = 0

      for line in lines:
        if 'Tracks:' in line:
          parts = line.split(':')
          if len(parts) > 1:
            trackCount = int(parts[1].strip())
            break

      return trackCount
    except (subprocess.CalledProcessError, ValueError) as e:
      raise exceptions.TrackError(f'Failed to query CD: {e}') from e
