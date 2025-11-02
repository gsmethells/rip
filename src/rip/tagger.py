# Copyright (C) 2003 Gregory J. Smethells
# Copyright (C) 2024 Gregory J. Smethells
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

"""
Audio file tagging functionality for rip.

Provides tagging for multiple audio formats using mutagen library.
Supports MP3 (ID3), FLAC, Opus, Ogg Vorbis, and AAC/M4A.
"""

import logging
import mutagen
import rip.exceptions as exceptions
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.id3 import ID3NoHeaderError
from mutagen.mp4 import MP4
from mutagen.oggopus import OggOpus
from mutagen.oggvorbis import OggVorbis
from pathlib import Path

logger = logging.getLogger(__name__)


class Tagger:
  """
  Audio file tagger supporting multiple formats.

  Uses mutagen to write metadata tags to audio files. Handles format-specific
  tagging requirements for MP3, FLAC, Opus, Ogg Vorbis, and AAC/M4A.
  """

  def __init__(self):
    """Initialize tagger."""

    pass

  def tagFile(self, filePath, track, album):
    """
    Tag an audio file with metadata.

    Automatically detects file format and applies appropriate tagging.

    :param filePath: Path to audio file
    :param track: Track metadata
    :param album: Album metadata
    :type filePath: Path or str
    :type track: metadata.Track
    :type album: metadata.Album
    :raises: TaggingError if tagging fails
    """

    filePath = Path(filePath)

    if not filePath.exists():
      raise exceptions.TaggingError(f'File not found: {filePath}')

    suffix = filePath.suffix.lower()

    if suffix == '.mp3':
      self._tagMp3(filePath, track, album)
    elif suffix == '.flac':
      self._tagFlac(filePath, track, album)
    elif suffix == '.opus':
      self._tagOpus(filePath, track, album)
    elif suffix == '.ogg':
      self._tagOgg(filePath, track, album)
    elif suffix in ['.m4a', '.mp4']:
      self._tagM4a(filePath, track, album)
    else:
      raise exceptions.TaggingError(f'Unsupported file format: {suffix}')

    logger.info(f'Tagged: {filePath.name}')

  def _tagMp3(self, filePath, track, album):
    """
    Tag MP3 file using ID3 tags.

    :param filePath: Path to MP3 file
    :param track: Track metadata
    :param album: Album metadata
    :type filePath: Path
    :type track: metadata.Track
    :type album: metadata.Album
    :raises: TaggingError if tagging fails
    """

    try:
      try:
        audio = EasyID3(str(filePath))
      except ID3NoHeaderError:
        audio = mutagen.File(str(filePath), easy=True)

        audio.add_tags()

      audio['title'] = track.title
      audio['artist'] = track.artist if track.artist != 'Unknown Artist' else album.artist
      audio['album'] = album.title
      audio['tracknumber'] = str(track.number)

      if album.year:
        audio['date'] = album.year

      if album.genre:
        audio['genre'] = album.genre

      audio.save()
    except Exception as e:
      raise exceptions.TaggingError(f'Failed to tag MP3 file: {e}') from e

  def _tagFlac(self, filePath, track, album):
    """
    Tag FLAC file using Vorbis comments.

    :param filePath: Path to FLAC file
    :param track: Track metadata
    :param album: Album metadata
    :type filePath: Path
    :type track: metadata.Track
    :type album: metadata.Album
    :raises: TaggingError if tagging fails
    """

    try:
      audio = FLAC(str(filePath))
      audio['title'] = track.title
      audio['artist'] = track.artist if track.artist != 'Unknown Artist' else album.artist
      audio['album'] = album.title
      audio['tracknumber'] = str(track.number)

      if album.year:
        audio['date'] = album.year

      if album.genre:
        audio['genre'] = album.genre

      audio.save()
    except Exception as e:
      raise exceptions.TaggingError(f'Failed to tag FLAC file: {e}') from e

  def _tagOpus(self, filePath, track, album):
    """
    Tag Opus file using Vorbis comments.

    :param filePath: Path to Opus file
    :param track: Track metadata
    :param album: Album metadata
    :type filePath: Path
    :type track: metadata.Track
    :type album: metadata.Album
    :raises: TaggingError if tagging fails
    """

    try:
      audio = OggOpus(str(filePath))
      audio['title'] = track.title
      audio['artist'] = track.artist if track.artist != 'Unknown Artist' else album.artist
      audio['album'] = album.title
      audio['tracknumber'] = str(track.number)

      if album.year:
        audio['date'] = album.year

      if album.genre:
        audio['genre'] = album.genre

      audio.save()
    except Exception as e:
      raise exceptions.TaggingError(f'Failed to tag Opus file: {e}') from e

  def _tagOgg(self, filePath, track, album):
    """
    Tag Ogg Vorbis file using Vorbis comments.

    :param filePath: Path to Ogg file
    :param track: Track metadata
    :param album: Album metadata
    :type filePath: Path
    :type track: metadata.Track
    :type album: metadata.Album
    :raises: TaggingError if tagging fails
    """

    try:
      audio = OggVorbis(str(filePath))
      audio['title'] = track.title
      audio['artist'] = track.artist if track.artist != 'Unknown Artist' else album.artist
      audio['album'] = album.title
      audio['tracknumber'] = str(track.number)

      if album.year:
        audio['date'] = album.year

      if album.genre:
        audio['genre'] = album.genre

      audio.save()
    except Exception as e:
      raise exceptions.TaggingError(f'Failed to tag Ogg file: {e}') from e

  def _tagM4a(self, filePath, track, album):
    """
    Tag AAC/M4A file using MP4 tags.

    :param filePath: Path to M4A file
    :param track: Track metadata
    :param album: Album metadata
    :type filePath: Path
    :type track: metadata.Track
    :type album: metadata.Album
    :raises: TaggingError if tagging fails
    """

    try:
      audio = MP4(str(filePath))

      audio['\xa9nam'] = track.title
      audio['\xa9ART'] = track.artist if track.artist != 'Unknown Artist' else album.artist
      audio['\xa9alb'] = album.title

      audio['trkn'] = [(track.number, 0)]

      if album.year:
        audio['\xa9day'] = album.year

      if album.genre:
        audio['\xa9gen'] = album.genre

      audio.save()
    except Exception as e:
      raise exceptions.TaggingError(f'Failed to tag M4A file: {e}') from e
