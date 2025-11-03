# Copyright (C) 2003 Gregory J. Smethells
# Copyright (C) 2025 Gregory J. Smethells
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

"""
Audio encoding functionality for rip.

Provides encoding to multiple formats: MP3, FLAC, Opus, Ogg Vorbis, and AAC.
Automatically discovers available encoders and wraps them with a unified interface.
"""

import logging
import rip.exceptions as exceptions
import rip.utils as utils
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class Encoder:
  """
  Audio encoder supporting multiple formats.

  Automatically detects which encoders are available and provides a unified
  interface for encoding WAV files to compressed formats.
  """

  FORMAT_MP3 = 'mp3'
  FORMAT_FLAC = 'flac'
  FORMAT_OPUS = 'opus'
  FORMAT_OGG = 'ogg'
  FORMAT_M4A = 'm4a'
  LAME = 'lame'
  FLAC = 'flac'
  OPUSENC = 'opusenc'
  OGGENC = 'oggenc'
  FDKAAC = 'fdkaac'
  QAAC = 'qaac'

  def __init__(self, format='opus', bitrate=192, quality=None, vbr=False, quiet=False):
    """
    Initialize the encoder.

    :param format: Output format (mp3, flac, opus, ogg, m4a)
    :param bitrate: Bitrate in kbps (for CBR encoding)
    :param quality: Quality setting (for VBR encoding, format-specific)
    :param vbr: Use variable bitrate encoding
    :param quiet: Suppress encoder output
    :type format: str
    :type bitrate: int
    :type quality: int or None
    :type vbr: bool
    :type quiet: bool
    :raises: EncoderNotFoundError if no encoder found for format
    """

    self.format = format.lower()
    self.bitrate = bitrate
    self.quality = quality
    self.vbr = vbr
    self.quiet = quiet
    self.tool = None
    self.toolPath = None

    self._findEncoder()

  def _findEncoder(self):
    """
    Find available encoder for the requested format.

    :raises: EncoderNotFoundError if no encoder found
    """

    if self.format == self.FORMAT_MP3:
      toolPath = utils.findTool(self.LAME)

      if toolPath:
        self.tool = self.LAME
        self.toolPath = toolPath

        logger.info(f'Found encoder: {self.LAME} at {toolPath}')
        return

      raise exceptions.EncoderNotFoundError('No MP3 encoder found. Please install lame.')
    elif self.format == self.FORMAT_FLAC:
      toolPath = utils.findTool(self.FLAC)

      if toolPath:
        self.tool = self.FLAC
        self.toolPath = toolPath

        logger.info(f'Found encoder: {self.FLAC} at {toolPath}')
        return

      raise exceptions.EncoderNotFoundError('No FLAC encoder found. Please install flac.')
    elif self.format == self.FORMAT_OPUS:
      toolPath = utils.findTool(self.OPUSENC)

      if toolPath:
        self.tool = self.OPUSENC
        self.toolPath = toolPath

        logger.info(f'Found encoder: {self.OPUSENC} at {toolPath}')
        return

      raise exceptions.EncoderNotFoundError('No Opus encoder found. Please install opus-tools.')
    elif self.format == self.FORMAT_OGG:
      toolPath = utils.findTool(self.OGGENC)

      if toolPath:
        self.tool = self.OGGENC
        self.toolPath = toolPath

        logger.info(f'Found encoder: {self.OGGENC} at {toolPath}')
        return

      raise exceptions.EncoderNotFoundError('No Ogg Vorbis encoder found. Please install vorbis-tools.')
    elif self.format == self.FORMAT_M4A:
      for tool in [self.FDKAAC, self.QAAC]:
        toolPath = utils.findTool(tool)

        if toolPath:
          self.tool = tool
          self.toolPath = toolPath

          logger.info(f'Found encoder: {tool} at {toolPath}')
          return

      raise exceptions.EncoderNotFoundError('No AAC encoder found. Please install fdkaac or qaac.')
    else:
      raise exceptions.EncodingError(f'Unsupported format: {self.format}')

  def encode(self, inputPath, outputPath):
    """
    Encode WAV file to target format.

    :param inputPath: Input WAV file path
    :param outputPath: Output file path
    :type inputPath: Path or str
    :type outputPath: Path or str
    :raises: EncodingError if encoding fails
    """

    inputPath = Path(inputPath)
    outputPath = Path(outputPath)

    if not inputPath.exists():
      raise exceptions.EncodingError(f'Input file not found: {inputPath}')

    if self.tool == self.LAME:
      self._encodeWithLame(inputPath, outputPath)
    elif self.tool == self.FLAC:
      self._encodeWithFlac(inputPath, outputPath)
    elif self.tool == self.OPUSENC:
      self._encodeWithOpusenc(inputPath, outputPath)
    elif self.tool == self.OGGENC:
      self._encodeWithOggenc(inputPath, outputPath)
    elif self.tool in [self.FDKAAC, self.QAAC]:
      self._encodeWithAac(inputPath, outputPath)
    else:
      raise exceptions.EncoderNotFoundError('No encoder tool configured')

  def _encodeWithLame(self, inputPath, outputPath):
    """
    Encode with LAME MP3 encoder.

    :param inputPath: Input WAV file path
    :param outputPath: Output MP3 file path
    :type inputPath: Path
    :type outputPath: Path
    :raises: EncodingError if encoding fails
    """

    cmd = [self.toolPath]

    if self.vbr or self.quality is not None:
      quality = self.quality if self.quality is not None else 2

      cmd.extend(['-V', str(quality)])
    else:
      cmd.extend(['-b', str(self.bitrate)])

    if self.quiet:
      cmd.append('--quiet')

    cmd.append(str(inputPath))
    cmd.append(str(outputPath))
    logger.info('Encoding to MP3 with LAME')
    logger.debug(f'Command: {" ".join(cmd)}')

    try:
      subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
      raise exceptions.EncodingError(f'LAME encoding failed: {e.stderr}') from e

  def _encodeWithFlac(self, inputPath, outputPath):
    """
    Encode with FLAC encoder.

    :param inputPath: Input WAV file path
    :param outputPath: Output FLAC file path
    :type inputPath: Path
    :type outputPath: Path
    :raises: EncodingError if encoding fails
    """

    cmd = [self.toolPath]
    compressionLevel = 5

    if self.quality is not None:
      compressionLevel = max(0, min(8, self.quality))

    cmd.extend(['-' + str(compressionLevel)])

    if self.quiet:
      cmd.append('--silent')

    cmd.extend(['-o', str(outputPath)])
    cmd.append(str(inputPath))
    logger.info('Encoding to FLAC')
    logger.debug(f'Command: {" ".join(cmd)}')

    try:
      subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
      raise exceptions.EncodingError(f'FLAC encoding failed: {e.stderr}') from e

  def _encodeWithOpusenc(self, inputPath, outputPath):
    """
    Encode with opusenc Opus encoder.

    :param inputPath: Input WAV file path
    :param outputPath: Output Opus file path
    :type inputPath: Path
    :type outputPath: Path
    :raises: EncodingError if encoding fails
    """

    cmd = [self.toolPath]

    if self.vbr or self.quality is not None:
      quality = self.quality if self.quality is not None else 6

      cmd.extend(['--vbr', '--comp', str(quality)])
    else:
      cmd.extend(['--bitrate', str(self.bitrate)])

    if self.quiet:
      cmd.append('--quiet')

    cmd.append(str(inputPath))
    cmd.append(str(outputPath))
    logger.info('Encoding to Opus with opusenc')
    logger.debug(f'Command: {" ".join(cmd)}')

    try:
      subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
      raise exceptions.EncodingError(f'opusenc encoding failed: {e.stderr}') from e

  def _encodeWithOggenc(self, inputPath, outputPath):
    """
    Encode with oggenc Ogg Vorbis encoder.

    :param inputPath: Input WAV file path
    :param outputPath: Output Ogg file path
    :type inputPath: Path
    :type outputPath: Path
    :raises: EncodingError if encoding fails
    """

    cmd = [self.toolPath]

    if self.vbr or self.quality is not None:
      quality = self.quality if self.quality is not None else 6

      cmd.extend(['-q', str(quality)])
    else:
      cmd.extend(['-b', str(self.bitrate)])

    if self.quiet:
      cmd.append('-Q')

    cmd.extend(['-o', str(outputPath)])
    cmd.append(str(inputPath))
    logger.info('Encoding to Ogg Vorbis with oggenc')
    logger.debug(f'Command: {" ".join(cmd)}')

    try:
      subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
      raise exceptions.EncodingError(f'oggenc encoding failed: {e.stderr}') from e

  def _encodeWithAac(self, inputPath, outputPath):
    """
    Encode with fdkaac or qaac AAC encoder.

    :param inputPath: Input WAV file path
    :param outputPath: Output M4A file path
    :type inputPath: Path
    :type outputPath: Path
    :raises: EncodingError if encoding fails
    """

    cmd = [self.toolPath]

    if self.tool == self.FDKAAC:
      if self.vbr or self.quality is not None:
        quality = self.quality if self.quality is not None else 4

        cmd.extend(['-m', str(quality)])
      else:
        cmd.extend(['-b', str(self.bitrate)])

      cmd.extend(['-o', str(outputPath)])
      cmd.append(str(inputPath))
    elif self.tool == self.QAAC:
      if self.vbr or self.quality is not None:
        quality = self.quality if self.quality is not None else 90

        cmd.extend(['-V', str(quality)])
      else:
        cmd.extend(['-c', str(self.bitrate)])

      cmd.extend(['-o', str(outputPath)])
      cmd.append(str(inputPath))
    else:
      raise exceptions.EncodingError(f'Unknown AAC encoder: {self.tool}')

    logger.info(f'Encoding to AAC with {self.tool}')
    logger.debug(f'Command: {" ".join(cmd)}')

    try:
      subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
      raise exceptions.EncodingError(f'{self.tool} encoding failed: {e.stderr}') from e

  def getExtension(self):
    """
    Get file extension for the current format.

    :rtype: str
    """

    return self.format
