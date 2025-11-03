# Copyright (C) 2003 Gregory J. Smethells
# Copyright (C) 2025 Gregory J. Smethells
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

"""Unit tests for metadata module."""

import pytest
import rip.exceptions as exceptions
import rip.metadata as metadata
from unittest.mock import MagicMock


def test_trackDataclass():
  """Test Track dataclass initialization."""

  track = metadata.Track(number=1, title='Test Track', artist='Test Artist', duration=180)

  assert track.number == 1
  assert track.title == 'Test Track'
  assert track.artist == 'Test Artist'
  assert track.duration == 180


def test_trackDefaultsToUnknownArtist():
  """Test Track defaults to 'Unknown Artist' when artist is empty."""

  track = metadata.Track(number=1, title='Test', artist='')

  assert track.artist == 'Unknown Artist'


def test_albumDataclass():
  """Test Album dataclass initialization."""

  tracks = [metadata.Track(1, 'Track 1'), metadata.Track(2, 'Track 2')]
  album = metadata.Album(title='Test Album', artist='Test Artist', tracks=tracks, year='2025')

  assert album.title == 'Test Album'
  assert album.artist == 'Test Artist'
  assert len(album.tracks) == 2
  assert album.year == '2025'


def test_albumDefaultsToUnknownAlbum():
  """Test Album defaults to 'Unknown Album' when title is empty."""

  album = metadata.Album(title='', artist='Test', tracks=[])

  assert album.title == 'Unknown Album'


def test_albumDefaultsToUnknownArtist():
  """Test Album defaults to 'Unknown Artist' when artist is empty."""

  album = metadata.Album(title='Test', artist='', tracks=[])

  assert album.artist == 'Unknown Artist'


def test_metadataProviderInitialization():
  """Test MetadataProvider initialization."""

  provider = metadata.MetadataProvider(userAgent='test', version='1.0', contact='test@example.com')

  assert provider.userAgent == 'test'
  assert provider.version == '1.0'
  assert provider.contact == 'test@example.com'


def test_lookupDiscReadsDiscId(mocker):
  """Test lookupDisc() reads disc ID from device."""

  mockDisc = MagicMock()
  mockDisc.id = 'test-disc-id'

  mocker.patch('discid.read', return_value=mockDisc)

  mockResult = {
    'disc': {
      'release-list': [
        {
          'title': 'Test Album',
          'artist-credit': [{'artist': {'name': 'Test Artist'}}],
          'date': '2025-01-01',
          'medium-list': [
            {
              'track-list': [
                {'recording': {'title': 'Track 1', 'length': 180000}},
              ]
            }
          ]
        }
      ]
    }
  }

  mocker.patch('musicbrainzngs.get_releases_by_discid', return_value=mockResult)

  provider = metadata.MetadataProvider()
  album = provider.lookupDisc('/dev/cdrom')

  assert album.discId == 'test-disc-id'


def test_lookupDiscRaisesErrorWhenDiscReadFails(mocker):
  """Test lookupDisc() raises MetadataError when disc read fails."""

  import discid

  mocker.patch('discid.read', side_effect=discid.DiscError('No disc'))

  provider = metadata.MetadataProvider()

  with pytest.raises(exceptions.MetadataError, match='Failed to read disc ID'):
    provider.lookupDisc('/dev/cdrom')


def test_lookupDiscRaisesErrorWhenMusicBrainzFails(mocker):
  """Test lookupDisc() raises MetadataError when MusicBrainz lookup fails."""

  import musicbrainzngs as mb

  mockDisc = MagicMock()
  mockDisc.id = 'test-disc-id'

  mocker.patch('discid.read', return_value=mockDisc)
  mocker.patch('musicbrainzngs.get_releases_by_discid', side_effect=mb.WebServiceError('API error'))

  provider = metadata.MetadataProvider()

  with pytest.raises(exceptions.MetadataError, match='MusicBrainz lookup failed'):
    provider.lookupDisc('/dev/cdrom')


def test_lookupDiscRaisesErrorWhenNoReleaseFound(mocker):
  """Test lookupDisc() raises MetadataError when no release found."""

  mockDisc = MagicMock()
  mockDisc.id = 'test-disc-id'

  mocker.patch('discid.read', return_value=mockDisc)
  mocker.patch('musicbrainzngs.get_releases_by_discid', return_value={'disc': {'release-list': []}})

  provider = metadata.MetadataProvider()

  with pytest.raises(exceptions.MetadataError, match='No releases found'):
    provider.lookupDisc('/dev/cdrom')


def test_parseRelease(mocker):
  """Test _parseRelease() converts MusicBrainz data to Album."""

  mockDisc = MagicMock()
  mockDisc.id = 'test-disc-id'

  mocker.patch('discid.read', return_value=mockDisc)

  release = {
    'title': 'Test Album',
    'artist-credit': [{'artist': {'name': 'Test Artist'}}],
    'date': '2025-01-01',
    'medium-list': [
      {
        'track-list': [
          {'recording': {'title': 'Track 1', 'length': 180000}},
          {'recording': {'title': 'Track 2', 'length': 240000}},
        ]
      }
    ]
  }
  mockResult = {'disc': {'release-list': [release]}}

  mocker.patch('musicbrainzngs.get_releases_by_discid', return_value=mockResult)

  provider = metadata.MetadataProvider()
  album = provider.lookupDisc('/dev/cdrom')

  assert album.title == 'Test Album'
  assert album.artist == 'Test Artist'
  assert album.year == '2025'
  assert len(album.tracks) == 2
  assert album.tracks[0].title == 'Track 1'
  assert album.tracks[0].duration == 180
  assert album.tracks[1].title == 'Track 2'
  assert album.tracks[1].duration == 240
