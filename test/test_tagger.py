# Copyright (C) 2003 Gregory J. Smethells
# Copyright (C) 2025 Gregory J. Smethells
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

"""Unit tests for tagger module."""

import pytest
import rip.exceptions as exceptions
import rip.metadata as metadata
import rip.tagger as tagger
from unittest.mock import MagicMock


def test_taggerInitialization():
  """Test Tagger initialization."""

  tag = tagger.Tagger()

  assert tag is not None


def test_tagFileRaisesErrorWhenFileNotFound():
  """Test tagFile() raises TaggingError when file doesn't exist."""

  tag = tagger.Tagger()
  track = metadata.Track(1, 'Test Track', 'Test Artist')
  album = metadata.Album('Test Album', 'Test Artist', [track])

  with pytest.raises(exceptions.TaggingError, match='File not found'):
    tag.tagFile('/nonexistent/file.mp3', track, album)


def test_tagFileRaisesErrorOnUnsupportedFormat(tmp_path):
  """Test tagFile() raises TaggingError for unsupported format."""

  testFile = tmp_path / 'test.unsupported'

  testFile.touch()

  tag = tagger.Tagger()
  track = metadata.Track(1, 'Test Track', 'Test Artist')
  album = metadata.Album('Test Album', 'Test Artist', [track])

  with pytest.raises(exceptions.TaggingError, match='Unsupported file format'):
    tag.tagFile(testFile, track, album)


def test_tagMp3File(tmp_path, mocker):
  """Test tagging MP3 file with ID3 tags."""

  testFile = tmp_path / 'test.mp3'

  testFile.touch()

  mockAudio = {}
  mockSave = MagicMock()
  mockAudioObj = MagicMock()
  mockAudioObj.__setitem__ = lambda self, key, value: mockAudio.__setitem__(key, value)
  mockAudioObj.__getitem__ = lambda self, key: mockAudio.__getitem__(key)
  mockAudioObj.save = mockSave

  mocker.patch('mutagen.File', return_value=mockAudioObj)
  mocker.patch('rip.tagger.EasyID3', return_value=mockAudioObj)

  tag = tagger.Tagger()
  track = metadata.Track(1, 'Test Track', 'Test Artist', 180)
  album = metadata.Album('Test Album', 'Album Artist', [track], year='2025', genre='Rock')

  tag.tagFile(testFile, track, album)
  assert mockAudio['title'] == 'Test Track'
  assert mockAudio['artist'] == 'Test Artist'
  assert mockAudio['album'] == 'Test Album'
  assert mockAudio['tracknumber'] == '1'
  assert mockAudio['date'] == '2025'
  assert mockAudio['genre'] == 'Rock'
  mockSave.assert_called_once()


def test_tagFlacFile(tmp_path, mocker):
  """Test tagging FLAC file with Vorbis comments."""

  testFile = tmp_path / 'test.flac'

  testFile.touch()

  mockAudio = {}
  mockSave = MagicMock()
  mockAudioObj = MagicMock()
  mockAudioObj.__setitem__ = lambda self, key, value: mockAudio.__setitem__(key, value)
  mockAudioObj.__getitem__ = lambda self, key: mockAudio.__getitem__(key)
  mockAudioObj.save = mockSave

  mocker.patch('rip.tagger.FLAC', return_value=mockAudioObj)

  tag = tagger.Tagger()
  track = metadata.Track(2, 'FLAC Track', 'FLAC Artist', 200)
  album = metadata.Album('FLAC Album', 'Album Artist', [track], year='2025')

  tag.tagFile(testFile, track, album)
  assert mockAudio['title'] == 'FLAC Track'
  assert mockAudio['artist'] == 'FLAC Artist'
  assert mockAudio['album'] == 'FLAC Album'
  assert mockAudio['tracknumber'] == '2'
  assert mockAudio['date'] == '2025'
  mockSave.assert_called_once()


def test_tagOpusFile(tmp_path, mocker):
  """Test tagging Opus file with Vorbis comments."""

  testFile = tmp_path / 'test.opus'

  testFile.touch()

  mockAudio = {}
  mockSave = MagicMock()
  mockAudioObj = MagicMock()
  mockAudioObj.__setitem__ = lambda self, key, value: mockAudio.__setitem__(key, value)
  mockAudioObj.__getitem__ = lambda self, key: mockAudio.__getitem__(key)
  mockAudioObj.save = mockSave

  mocker.patch('rip.tagger.OggOpus', return_value=mockAudioObj)

  tag = tagger.Tagger()
  track = metadata.Track(3, 'Opus Track', 'Opus Artist', 220)
  album = metadata.Album('Opus Album', 'Album Artist', [track])

  tag.tagFile(testFile, track, album)
  assert mockAudio['title'] == 'Opus Track'
  assert mockAudio['artist'] == 'Opus Artist'
  assert mockAudio['album'] == 'Opus Album'
  assert mockAudio['tracknumber'] == '3'
  mockSave.assert_called_once()


def test_tagOggFile(tmp_path, mocker):
  """Test tagging Ogg Vorbis file with Vorbis comments."""

  testFile = tmp_path / 'test.ogg'

  testFile.touch()

  mockAudio = {}
  mockSave = MagicMock()
  mockAudioObj = MagicMock()
  mockAudioObj.__setitem__ = lambda self, key, value: mockAudio.__setitem__(key, value)
  mockAudioObj.__getitem__ = lambda self, key: mockAudio.__getitem__(key)
  mockAudioObj.save = mockSave

  mocker.patch('rip.tagger.OggVorbis', return_value=mockAudioObj)

  tag = tagger.Tagger()
  track = metadata.Track(4, 'Ogg Track', 'Ogg Artist', 190)
  album = metadata.Album('Ogg Album', 'Album Artist', [track])

  tag.tagFile(testFile, track, album)
  assert mockAudio['title'] == 'Ogg Track'
  assert mockAudio['artist'] == 'Ogg Artist'
  assert mockAudio['album'] == 'Ogg Album'
  assert mockAudio['tracknumber'] == '4'
  mockSave.assert_called_once()


def test_tagM4aFile(tmp_path, mocker):
  """Test tagging M4A/AAC file with MP4 tags."""

  testFile = tmp_path / 'test.m4a'

  testFile.touch()

  mockAudio = {}
  mockSave = MagicMock()
  mockAudioObj = MagicMock()
  mockAudioObj.__setitem__ = lambda self, key, value: mockAudio.__setitem__(key, value)
  mockAudioObj.__getitem__ = lambda self, key: mockAudio.__getitem__(key)
  mockAudioObj.save = mockSave

  mocker.patch('rip.tagger.MP4', return_value=mockAudioObj)

  tag = tagger.Tagger()
  track = metadata.Track(5, 'AAC Track', 'AAC Artist', 210)
  album = metadata.Album('AAC Album', 'Album Artist', [track], year='2025', genre='Pop')

  tag.tagFile(testFile, track, album)
  assert mockAudio['\xa9nam'] == 'AAC Track'
  assert mockAudio['\xa9ART'] == 'AAC Artist'
  assert mockAudio['\xa9alb'] == 'AAC Album'
  assert mockAudio['trkn'] == [(5, 0)]
  assert mockAudio['\xa9day'] == '2025'
  assert mockAudio['\xa9gen'] == 'Pop'
  mockSave.assert_called_once()


def test_tagFileUsesAlbumArtistWhenTrackArtistUnknown(tmp_path, mocker):
  """Test tagFile() uses album artist when track artist is Unknown."""

  testFile = tmp_path / 'test.mp3'

  testFile.touch()

  mockAudio = {}
  mockSave = MagicMock()
  mockAudioObj = MagicMock()
  mockAudioObj.__setitem__ = lambda self, key, value: mockAudio.__setitem__(key, value)
  mockAudioObj.__getitem__ = lambda self, key: mockAudio.__getitem__(key)
  mockAudioObj.save = mockSave

  mocker.patch('mutagen.File', return_value=mockAudioObj)
  mocker.patch('rip.tagger.EasyID3', return_value=mockAudioObj)

  tag = tagger.Tagger()
  track = metadata.Track(1, 'Track', 'Unknown Artist')
  album = metadata.Album('Album', 'Album Artist', [track])

  tag.tagFile(testFile, track, album)
  assert mockAudio['artist'] == 'Album Artist'


def test_tagFileRaisesErrorOnException(tmp_path, mocker):
  """Test tagFile() raises TaggingError when tagging fails."""

  testFile = tmp_path / 'test.mp3'

  testFile.touch()
  mocker.patch('rip.tagger.EasyID3', side_effect=Exception('Tagging failed'))

  tag = tagger.Tagger()
  track = metadata.Track(1, 'Test', 'Artist')
  album = metadata.Album('Album', 'Artist', [track])

  with pytest.raises(exceptions.TaggingError, match='Failed to tag MP3 file'):
    tag.tagFile(testFile, track, album)
