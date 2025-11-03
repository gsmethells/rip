# Copyright (C) 2003 Gregory J. Smethells
# Copyright (C) 2025 Gregory J. Smethells
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

"""Unit tests for encoder module."""

import pytest
import rip.encoder as encoder
import rip.exceptions as exceptions
import subprocess


def test_encoderFindsMp3Encoder(mocker):
  """Test Encoder finds lame for MP3 encoding."""

  mocker.patch('rip.utils.findTool', return_value='/usr/bin/lame')

  enc = encoder.Encoder(format='mp3')

  assert enc.tool == encoder.Encoder.LAME
  assert enc.toolPath == '/usr/bin/lame'


def test_encoderFindsFlacEncoder(mocker):
  """Test Encoder finds flac for FLAC encoding."""

  mocker.patch('rip.utils.findTool', return_value='/usr/bin/flac')

  enc = encoder.Encoder(format='flac')

  assert enc.tool == encoder.Encoder.FLAC
  assert enc.toolPath == '/usr/bin/flac'


def test_encoderFindsOpusEncoder(mocker):
  """Test Encoder finds opusenc for Opus encoding."""

  mocker.patch('rip.utils.findTool', return_value='/usr/bin/opusenc')

  enc = encoder.Encoder(format='opus')

  assert enc.tool == encoder.Encoder.OPUSENC
  assert enc.toolPath == '/usr/bin/opusenc'


def test_encoderFindsOggEncoder(mocker):
  """Test Encoder finds oggenc for Ogg Vorbis encoding."""

  mocker.patch('rip.utils.findTool', return_value='/usr/bin/oggenc')

  enc = encoder.Encoder(format='ogg')

  assert enc.tool == encoder.Encoder.OGGENC
  assert enc.toolPath == '/usr/bin/oggenc'


def test_encoderFindsAacEncoder(mocker):
  """Test Encoder finds fdkaac or qaac for AAC encoding."""

  mocker.patch('rip.utils.findTool', side_effect=['/usr/bin/fdkaac'])

  enc = encoder.Encoder(format='m4a')

  assert enc.tool == encoder.Encoder.FDKAAC
  assert enc.toolPath == '/usr/bin/fdkaac'


def test_encoderRaisesErrorWhenEncoderNotFound(mocker):
  """Test Encoder raises EncoderNotFoundError when encoder not available."""

  mocker.patch('rip.utils.findTool', return_value=None)

  with pytest.raises(exceptions.EncoderNotFoundError):
    encoder.Encoder(format='mp3')


def test_encoderRaisesErrorOnUnsupportedFormat(mocker):
  """Test Encoder raises EncodingError for unsupported format."""

  mocker.patch('rip.utils.findTool', return_value='/usr/bin/lame')

  with pytest.raises(exceptions.EncodingError):
    encoder.Encoder(format='unsupported')


def test_encodeWithLame(tmp_path, mocker):
  """Test encode() with lame MP3 encoder."""

  inputFile = tmp_path / 'input.wav'

  inputFile.touch()

  outputFile = tmp_path / 'output.mp3'

  mocker.patch('rip.utils.findTool', return_value='/usr/bin/lame')

  mockRun = mocker.patch('subprocess.run')
  enc = encoder.Encoder(format='mp3', bitrate=192)

  enc.encode(inputFile, outputFile)
  mockRun.assert_called_once()

  args = mockRun.call_args[0][0]

  assert '/usr/bin/lame' in args
  assert '-b' in args
  assert '192' in args


def test_encodeWithLameVbr(tmp_path, mocker):
  """Test encode() with lame in VBR mode."""

  inputFile = tmp_path / 'input.wav'

  inputFile.touch()

  outputFile = tmp_path / 'output.mp3'

  mocker.patch('rip.utils.findTool', return_value='/usr/bin/lame')

  mockRun = mocker.patch('subprocess.run')
  enc = encoder.Encoder(format='mp3', vbr=True, quality=2)

  enc.encode(inputFile, outputFile)

  args = mockRun.call_args[0][0]

  assert '-V' in args
  assert '2' in args


def test_encodeWithFlac(tmp_path, mocker):
  """Test encode() with flac encoder."""

  inputFile = tmp_path / 'input.wav'

  inputFile.touch()

  outputFile = tmp_path / 'output.flac'

  mocker.patch('rip.utils.findTool', return_value='/usr/bin/flac')

  mockRun = mocker.patch('subprocess.run')
  enc = encoder.Encoder(format='flac', quality=5)

  enc.encode(inputFile, outputFile)
  mockRun.assert_called_once()

  args = mockRun.call_args[0][0]

  assert '/usr/bin/flac' in args
  assert '-5' in args


def test_encodeWithOpus(tmp_path, mocker):
  """Test encode() with opusenc."""

  inputFile = tmp_path / 'input.wav'

  inputFile.touch()

  outputFile = tmp_path / 'output.opus'

  mocker.patch('rip.utils.findTool', return_value='/usr/bin/opusenc')

  mockRun = mocker.patch('subprocess.run')
  enc = encoder.Encoder(format='opus', bitrate=192)

  enc.encode(inputFile, outputFile)
  mockRun.assert_called_once()

  args = mockRun.call_args[0][0]

  assert '/usr/bin/opusenc' in args
  assert '--bitrate' in args
  assert '192' in args


def test_encodeRaisesErrorWhenInputNotFound(tmp_path, mocker):
  """Test encode() raises EncodingError when input file doesn't exist."""

  inputFile = tmp_path / 'nonexistent.wav'
  outputFile = tmp_path / 'output.mp3'

  mocker.patch('rip.utils.findTool', return_value='/usr/bin/lame')

  enc = encoder.Encoder(format='mp3')

  with pytest.raises(exceptions.EncodingError):
    enc.encode(inputFile, outputFile)


def test_encodeRaisesErrorOnSubprocessFailure(tmp_path, mocker):
  """Test encode() raises EncodingError when subprocess fails."""

  inputFile = tmp_path / 'input.wav'

  inputFile.touch()

  outputFile = tmp_path / 'output.mp3'

  mocker.patch('rip.utils.findTool', return_value='/usr/bin/lame')
  mocker.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'cmd', stderr='error'))

  enc = encoder.Encoder(format='mp3')

  with pytest.raises(exceptions.EncodingError):
    enc.encode(inputFile, outputFile)


def test_getExtensionReturnsCorrectFormat(mocker):
  """Test getExtension() returns the format."""

  mocker.patch('rip.utils.findTool', return_value='/usr/bin/lame')

  enc = encoder.Encoder(format='mp3')

  assert enc.getExtension() == 'mp3'
