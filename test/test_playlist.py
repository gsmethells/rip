# Copyright (C) 2003 Gregory J. Smethells
# Copyright (C) 2024 Gregory J. Smethells
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

"""Unit tests for playlist module."""

import pytest
import rip.exceptions as exceptions
import rip.playlist as playlist


def test_playlistGeneratorInitializesWithM3u():
  """Test PlaylistGenerator initializes with M3U format."""

  gen = playlist.PlaylistGenerator(format='m3u')

  assert gen.format == 'm3u'


def test_playlistGeneratorInitializesWithPls():
  """Test PlaylistGenerator initializes with PLS format."""

  gen = playlist.PlaylistGenerator(format='pls')

  assert gen.format == 'pls'


def test_playlistGeneratorRaisesErrorOnUnsupportedFormat():
  """Test PlaylistGenerator raises ValueError for unsupported format."""

  with pytest.raises(ValueError, match='Unsupported playlist format'):
    playlist.PlaylistGenerator(format='unsupported')


def test_generateM3uPlaylist(tmp_path):
  """Test generating M3U playlist."""

  file1 = tmp_path / 'track1.mp3'
  file2 = tmp_path / 'track2.mp3'

  file1.touch()
  file2.touch()

  playlistFile = tmp_path / 'playlist.m3u'
  gen = playlist.PlaylistGenerator(format='m3u')

  gen.generate([file1, file2], playlistFile)
  assert playlistFile.exists()

  content = playlistFile.read_text()

  assert '#EXTM3U' in content
  assert 'track1.mp3' in content
  assert 'track2.mp3' in content


def test_generateM3uPlaylistWithTitle(tmp_path):
  """Test generating M3U playlist with title."""

  file1 = tmp_path / 'track1.mp3'

  file1.touch()

  playlistFile = tmp_path / 'playlist.m3u'
  gen = playlist.PlaylistGenerator(format='m3u')

  gen.generate([file1], playlistFile, title='Test Playlist')

  content = playlistFile.read_text()

  assert '#PLAYLIST:Test Playlist' in content


def test_generateM3uPlaylistWithRelativePaths(tmp_path):
  """Test generating M3U playlist with relative paths."""

  musicDir = tmp_path / 'music'

  musicDir.mkdir()

  file1 = musicDir / 'track1.mp3'

  file1.touch()

  playlistFile = tmp_path / 'playlist.m3u'
  gen = playlist.PlaylistGenerator(format='m3u')

  gen.generate([file1], playlistFile, relativePaths=True)

  content = playlistFile.read_text()

  assert 'music/track1.mp3' in content or 'music\\track1.mp3' in content


def test_generatePlsPlaylist(tmp_path):
  """Test generating PLS playlist."""

  file1 = tmp_path / 'track1.mp3'
  file2 = tmp_path / 'track2.mp3'

  file1.touch()
  file2.touch()

  playlistFile = tmp_path / 'playlist.pls'
  gen = playlist.PlaylistGenerator(format='pls')

  gen.generate([file1, file2], playlistFile)
  assert playlistFile.exists()

  content = playlistFile.read_text()

  assert '[playlist]' in content

  assert 'NumberOfEntries=2' in content
  assert 'File1=' in content
  assert 'File2=' in content
  assert 'Version=2' in content


def test_generatePlsPlaylistWithRelativePaths(tmp_path):
  """Test generating PLS playlist with relative paths."""

  musicDir = tmp_path / 'music'

  musicDir.mkdir()

  file1 = musicDir / 'track1.mp3'

  file1.touch()

  playlistFile = tmp_path / 'playlist.pls'
  gen = playlist.PlaylistGenerator(format='pls')

  gen.generate([file1], playlistFile, relativePaths=True)

  content = playlistFile.read_text()

  assert 'music/track1.mp3' in content or 'music\\track1.mp3' in content


def test_generateRaisesErrorWhenNoValidFiles():
  """Test generate() raises RipError when no valid files provided."""

  gen = playlist.PlaylistGenerator(format='m3u')

  with pytest.raises(exceptions.RipError, match='No valid files'):
    gen.generate([], '/tmp/playlist.m3u')


def test_generateSkipsNonexistentFiles(tmp_path):
  """Test generate() skips files that don't exist."""

  file1 = tmp_path / 'existing.mp3'

  file1.touch()

  file2 = tmp_path / 'nonexistent.mp3'
  playlistFile = tmp_path / 'playlist.m3u'
  gen = playlist.PlaylistGenerator(format='m3u')

  gen.generate([file1, file2], playlistFile)

  content = playlistFile.read_text()

  assert 'existing.mp3' in content
  assert 'nonexistent.mp3' not in content


def test_generatePlaylistConvenienceFunction(tmp_path):
  """Test generatePlaylist() convenience function."""

  file1 = tmp_path / 'track1.mp3'

  file1.touch()

  playlistFile = tmp_path / 'playlist.m3u'

  playlist.generatePlaylist([file1], playlistFile, format='m3u', title='Test')
  assert playlistFile.exists()

  content = playlistFile.read_text()

  assert '#EXTM3U' in content
  assert '#PLAYLIST:Test' in content


def test_generateHandlesAbsolutePaths(tmp_path):
  """Test generate() handles absolute paths when relativePaths=False."""

  file1 = tmp_path / 'track1.mp3'

  file1.touch()

  playlistFile = tmp_path / 'playlist.m3u'
  gen = playlist.PlaylistGenerator(format='m3u')

  gen.generate([file1], playlistFile, relativePaths=False)

  content = playlistFile.read_text()

  assert str(file1) in content
