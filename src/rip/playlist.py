# Copyright (C) 2003 Gregory J. Smethells
# Copyright (C) 2025 Gregory J. Smethells
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

"""
Playlist generation for rip.

Generates M3U and PLS format playlists for ripped audio files.
"""

import logging
import rip.exceptions as exceptions
from pathlib import Path

logger = logging.getLogger(__name__)


class PlaylistGenerator:
  """
  Playlist file generator.

  Creates M3U and PLS format playlists for collections of audio files.
  """

  FORMAT_M3U = 'm3u'
  FORMAT_PLS = 'pls'

  def __init__(self, format='m3u'):
    """
    Initialize playlist generator.

    :param format: Playlist format (m3u or pls)
    :type format: str
    :raises: ValueError if format is unsupported
    """

    format = format.lower()

    if format not in [self.FORMAT_M3U, self.FORMAT_PLS]:
      raise ValueError(f'Unsupported playlist format: {format}. Use "m3u" or "pls".')

    self.format = format

  def generate(self, files, outputPath, title=None, relativePaths=True):
    """
    Generate playlist file.

    :param files: List of audio file paths to include
    :param outputPath: Output playlist file path
    :param title: Optional playlist title (for extended formats)
    :param relativePaths: Use relative paths in playlist if True
    :type files: list
    :type outputPath: Path or str
    :type title: str or None
    :type relativePaths: bool
    :raises: exceptions.RipError if generation fails
    """

    outputPath = Path(outputPath)
    files = [Path(f) for f in files]

    for filePath in files:
      if not filePath.exists():
        logger.warning(f'File not found, skipping: {filePath}')

    files = [f for f in files if f.exists()]

    if not files:
      raise exceptions.RipError('No valid files to add to playlist')

    if self.format == self.FORMAT_M3U:
      self._generateM3u(files, outputPath, title, relativePaths)
    elif self.format == self.FORMAT_PLS:
      self._generatePls(files, outputPath, relativePaths)
    else:
      raise exceptions.RipError(f'Unsupported playlist format: {self.format}')

    logger.info(f'Created playlist: {outputPath}')

  def _generateM3u(self, files, outputPath, title, relativePaths):
    """
    Generate M3U playlist file.

    :param files: List of audio file paths
    :param outputPath: Output playlist path
    :param title: Optional playlist title
    :param relativePaths: Use relative paths
    :type files: list
    :type outputPath: Path
    :type title: str or None
    :type relativePaths: bool
    """

    try:
      with open(outputPath, 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\n')

        if title:
          f.write(f'#PLAYLIST:{title}\n')

        for filePath in files:
          if relativePaths:
            try:
              filePath = filePath.relative_to(outputPath.parent)
            except ValueError:
              pass

          f.write(f'{filePath}\n')
    except OSError as e:
      raise exceptions.RipError(f'Failed to write M3U playlist: {e}') from e

  def _generatePls(self, files, outputPath, relativePaths):
    """
    Generate PLS playlist file.

    :param files: List of audio file paths
    :param outputPath: Output playlist path
    :param relativePaths: Use relative paths
    :type files: list
    :type outputPath: Path
    :type relativePaths: bool
    """

    try:
      with open(outputPath, 'w', encoding='utf-8') as f:
        f.write('[playlist]\n')
        f.write(f'NumberOfEntries={len(files)}\n')
        f.write('\n')

        for idx, filePath in enumerate(files, start=1):
          if relativePaths:
            try:
              filePath = filePath.relative_to(outputPath.parent)
            except ValueError:
              pass

          f.write(f'File{idx}={filePath}\n')

        f.write('\n')
        f.write('Version=2\n')
    except OSError as e:
      raise exceptions.RipError(f'Failed to write PLS playlist: {e}') from e


def generatePlaylist(files, outputPath, format='m3u', title=None, relativePaths=True):
  """
  Convenience function to generate a playlist.

  :param files: List of audio file paths
  :param outputPath: Output playlist file path
  :param format: Playlist format (m3u or pls)
  :param title: Optional playlist title
  :param relativePaths: Use relative paths in playlist
  :type files: list
  :type outputPath: Path or str
  :type format: str
  :type title: str or None
  :type relativePaths: bool
  """

  generator = PlaylistGenerator(format=format)

  generator.generate(files, outputPath, title=title, relativePaths=relativePaths)
