# Copyright (C) 2003 Gregory J. Smethells
# Copyright (C) 2025 Gregory J. Smethells
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

"""
Metadata lookup functionality for rip.

Provides CD metadata lookup via MusicBrainz. Replaces the defunct CDDB
service used in the original Perl version.
"""

import discid
import logging
import musicbrainzngs as mb
import rip.exceptions as exceptions
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Track:
  """Metadata for a single track."""

  number: int
  title: str
  artist: str = ''
  duration: int = 0

  def __post_init__(self):
    if not self.artist:
      self.artist = 'Unknown Artist'


@dataclass
class Album:
  """Metadata for an album."""

  title: str
  artist: str
  tracks: list
  year: str = ''
  genre: str = ''
  discId: str = ''

  def __post_init__(self):
    if not self.title:
      self.title = 'Unknown Album'

    if not self.artist:
      self.artist = 'Unknown Artist'


class MetadataProvider:
  """
  Metadata provider using MusicBrainz.

  Looks up CD metadata from MusicBrainz database using disc ID.
  """

  def __init__(self, userAgent='rip', version='2.0.0', contact=''):
    """
    Initialize metadata provider.

    :param userAgent: Application name for MusicBrainz
    :param version: Application version
    :param contact: Contact URL or email
    :type userAgent: str
    :type version: str
    :type contact: str
    """

    self.userAgent = userAgent
    self.version = version
    self.contact = contact if contact else 'https://github.com/gsmethells/rip'

    mb.set_useragent(self.userAgent, self.version, self.contact)

  def lookupDisc(self, device='/dev/cdrom'):
    """
    Look up CD metadata from MusicBrainz.

    Reads disc ID from CD drive and queries MusicBrainz database.

    :param device: CD device path
    :type device: str
    :rtype: Album
    :raises: MetadataError if lookup fails
    """

    try:
      disc = discid.read(device)

      logger.info(f'Disc ID: {disc.id}')
    except discid.DiscError as e:
      raise exceptions.MetadataError(f'Failed to read disc ID from {device}: {e}') from e

    try:
      result = mb.get_releases_by_discid(disc.id, includes=['artists', 'recordings'])
    except mb.WebServiceError as e:
      raise exceptions.MetadataError(f'MusicBrainz lookup failed: {e}') from e

    if 'disc' not in result:
      raise exceptions.MetadataError('No disc information found in MusicBrainz')

    if 'release-list' not in result['disc'] or not result['disc']['release-list']:
      raise exceptions.MetadataError('No releases found for this disc in MusicBrainz')

    release = result['disc']['release-list'][0]

    return self._parseRelease(release, disc.id)

  def _parseRelease(self, release, discId):
    """
    Parse MusicBrainz release data into Album object.

    :param release: MusicBrainz release data
    :param discId: Disc ID string
    :type release: dict
    :type discId: str
    :rtype: Album
    """

    title = release.get('title', 'Unknown Album')
    artist = 'Unknown Artist'

    if 'artist-credit' in release:
      artistCredit = release['artist-credit']

      if isinstance(artistCredit, list) and len(artistCredit) > 0:
        artist = artistCredit[0].get('artist', {}).get('name', 'Unknown Artist')

    year = ''

    if 'date' in release:
      date = release['date']

      if len(date) >= 4:
        year = date[:4]

    tracks = []

    if 'medium-list' in release:
      mediumList = release['medium-list']

      if mediumList and len(mediumList) > 0:
        medium = mediumList[0]

        if 'track-list' in medium:
          trackList = medium['track-list']

          for idx, track in enumerate(trackList, start=1):
            trackTitle = track.get('recording', {}).get('title', f'Track {idx}')
            trackArtist = artist

            if 'artist-credit' in track.get('recording', {}):
              trackArtistCredit = track['recording']['artist-credit']

              if isinstance(trackArtistCredit, list) and len(trackArtistCredit) > 0:
                trackArtist = trackArtistCredit[0].get('artist', {}).get('name', artist)

            duration = 0

            if 'length' in track.get('recording', {}):
              duration = int(track['recording']['length']) // 1000

            tracks.append(Track(number=idx, title=trackTitle, artist=trackArtist, duration=duration))

    return Album(title=title, artist=artist, tracks=tracks, year=year, discId=discId)

  def lookupDiscInteractive(self, device='/dev/cdrom'):
    """
    Look up CD metadata with interactive selection.

    If multiple releases are found, prompts user to select one.

    :param device: CD device path
    :type device: str
    :rtype: Album
    :raises: MetadataError if lookup fails
    """

    try:
      disc = discid.read(device)

      logger.info(f'Disc ID: {disc.id}')
    except discid.DiscError as e:
      raise exceptions.MetadataError(f'Failed to read disc ID from {device}: {e}') from e

    try:
      result = mb.get_releases_by_discid(disc.id, includes=['artists', 'recordings'])
    except mb.WebServiceError as e:
      raise exceptions.MetadataError(f'MusicBrainz lookup failed: {e}') from e

    if 'disc' not in result:
      raise exceptions.MetadataError('No disc information found in MusicBrainz')

    if 'release-list' not in result['disc'] or not result['disc']['release-list']:
      raise exceptions.MetadataError('No releases found for this disc in MusicBrainz')

    releaseList = result['disc']['release-list']

    if len(releaseList) == 1:
      return self._parseRelease(releaseList[0], disc.id)

    print('\nMultiple releases found:')

    for idx, release in enumerate(releaseList, start=1):
      title = release.get('title', 'Unknown')
      artist = 'Unknown'

      if 'artist-credit' in release:
        artistCredit = release['artist-credit']

        if isinstance(artistCredit, list) and len(artistCredit) > 0:
          artist = artistCredit[0].get('artist', {}).get('name', 'Unknown')

      date = release.get('date', '')
      country = release.get('country', '')
      label = ''

      if 'label-info-list' in release:
        labelInfoList = release['label-info-list']

        if labelInfoList and len(labelInfoList) > 0:
          label = labelInfoList[0].get('label', {}).get('name', '')

      print(f'  {idx}. {artist} - {title}', end='')

      if date:
        print(f' ({date[:4]})', end='')

      if country:
        print(f' [{country}]', end='')

      if label:
        print(f' - {label}', end='')

      print()

    while True:
      try:
        choice = input(f'\nSelect release (1-{len(releaseList)}): ')
        choiceNum = int(choice)

        if 1 <= choiceNum <= len(releaseList):
          return self._parseRelease(releaseList[choiceNum - 1], disc.id)
        else:
          print(f'Please enter a number between 1 and {len(releaseList)}')
      except ValueError:
        print('Please enter a valid number')
      except (KeyboardInterrupt, EOFError):
        raise exceptions.MetadataError('User cancelled selection') from None
