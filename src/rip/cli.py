# Copyright (C) 2003 Gregory J. Smethells
# Copyright (C) 2025 Gregory J. Smethells
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

"""
Command-line interface for rip.

Provides the main entry point and argument parsing for the rip CD ripper.
"""

import argparse
import logging
import rip
import rip.config as config
import rip.encoder as encoder
import rip.exceptions as exceptions
import rip.ripper as ripper
import rip.utils as utils
import sys
from pathlib import Path


def setupLogging(verbose=False, quiet=False):
  """
  Set up logging configuration.

  :param verbose: Enable verbose (DEBUG) logging
  :param quiet: Suppress all but ERROR logging
  :type verbose: bool
  :type quiet: bool
  """

  if quiet:
    level = logging.ERROR
  elif verbose:
    level = logging.DEBUG
  else:
    level = logging.INFO

  logging.basicConfig(level=level, format='%(levelname)s: %(message)s')


def parseArguments():
  """
  Parse command-line arguments.

  :rtype: argparse.Namespace
  """

  cfg = config.Config()
  parser = argparse.ArgumentParser(
    description='Modern CD ripper supporting MP3, FLAC, Opus, Ogg Vorbis, and AAC',
    epilog='For more information, visit: https://github.com/gsmethells/rip',
  )

  parser.add_argument(
    'tracks', nargs='*', help='Track numbers to rip (e.g., 1 3-5 7). If not specified, all tracks are ripped.'
  )

  formatGroup = parser.add_argument_group('format options')

  formatGroup.add_argument(
    '-f',
    '--format',
    choices=['mp3', 'flac', 'opus', 'ogg', 'm4a'],
    default=cfg.get('format', 'mp3'),
    help='Output format (default: %(default)s)',
  )
  formatGroup.add_argument(
    '-b',
    '--bitrate',
    type=int,
    default=cfg.getInt('kbps', 192),
    help='Bitrate in kbps for CBR encoding (default: %(default)s)',
  )
  formatGroup.add_argument('-q', '--quality', type=int, help='Quality setting for VBR encoding (format-specific)')
  formatGroup.add_argument('-V', '--vbr', action='store_true', help='Use variable bitrate encoding')
  formatGroup.add_argument('-w', '--wav', action='store_true', help='Rip to WAV only (no encoding)')

  deviceGroup = parser.add_argument_group('device options')

  deviceGroup.add_argument(
    '-d', '--device', default=cfg.get('dev', '/dev/cdrom'), help='CD device path (default: %(default)s)'
  )
  deviceGroup.add_argument('--list-devices', action='store_true', help='List available CD/DVD devices and exit')

  ripGroup = parser.add_argument_group('ripping options')

  ripGroup.add_argument(
    '-p', '--paranoia', action='store_true', default=True, help='Enable paranoia mode for error correction (default)'
  )
  ripGroup.add_argument('--no-paranoia', action='store_false', dest='paranoia', help='Disable paranoia mode')
  ripGroup.add_argument('-s', '--speed', type=int, help='CD read speed')

  metadataGroup = parser.add_argument_group('metadata options')

  metadataGroup.add_argument(
    '-c', '--cddb', action='store_true', help='Fetch metadata from MusicBrainz and auto-rename files'
  )
  metadataGroup.add_argument('-t', '--tag', action='store_true', help='Tag output files with metadata')

  outputGroup = parser.add_argument_group('output options')

  outputGroup.add_argument('-m', '--move', dest='outputDir', type=Path, help='Move output files to specified directory')
  outputGroup.add_argument(
    '-n', '--nounderscore', action='store_true', help='Use spaces instead of underscores in filenames'
  )
  outputGroup.add_argument('-g', '--generate', action='store_true', help='Generate playlist file')

  workflowGroup = parser.add_argument_group('workflow options')

  workflowGroup.add_argument(
    '-L', '--lazy', action='store_true', help='Lazy mode: fetch metadata, tag, and organize files'
  )
  workflowGroup.add_argument('-S', '--superlazy', action='store_true', help='Superlazy mode: lazy + auto-eject')
  workflowGroup.add_argument('-e', '--eject', action='store_true', help='Eject CD tray when finished')

  miscGroup = parser.add_argument_group('miscellaneous options')

  miscGroup.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
  miscGroup.add_argument('-Q', '--quiet', action='store_true', help='Suppress all output except errors')
  miscGroup.add_argument('--debug', action='store_true', help='Enable debug mode')
  miscGroup.add_argument('--version', action='version', version=f'rip {rip.__version__}')
  return parser.parse_args()


def ripTracks(args):
  """
  Main ripping logic.

  :param args: Parsed command-line arguments
  :type args: argparse.Namespace
  """

  logger = logging.getLogger(__name__)

  try:
    cd = ripper.Ripper(
      device=args.device, paranoia=args.paranoia, speed=args.speed, quiet=args.quiet, verbose=args.verbose
    )
  except exceptions.RipError as e:
    logger.error(str(e))
    sys.exit(1)

  if args.tracks:
    try:
      trackList = utils.parseTracks(args.tracks)
    except exceptions.TrackError as e:
      logger.error(str(e))
      sys.exit(1)
  else:
    try:
      trackCount = cd.queryTracks()
      trackList = list(range(1, trackCount + 1))

      logger.info(f'Found {trackCount} tracks on CD')
    except exceptions.TrackError as e:
      logger.error(f'Failed to query CD: {e}')
      sys.exit(1)

  if args.outputDir:
    utils.ensureDirectory(args.outputDir)

  if not args.wav:
    try:
      enc = encoder.Encoder(
        format=args.format, bitrate=args.bitrate, quality=args.quality, vbr=args.vbr, quiet=args.quiet
      )
    except exceptions.EncoderNotFoundError as e:
      logger.error(str(e))
      sys.exit(1)

  for trackNum in trackList:
    tempWav = utils.getTempWavPath(trackNum)

    try:
      logger.info(f'Ripping track {trackNum}...')
      cd.ripTrack(trackNum, tempWav)

      if args.wav:
        if args.outputDir:
          outputPath = args.outputDir / f'track_{trackNum:02d}.wav'
        else:
          outputPath = Path(f'track_{trackNum:02d}.wav')

        tempWav.rename(outputPath)
        logger.info(f'Created: {outputPath}')
      else:
        if args.outputDir:
          outputFilename = f'track_{trackNum:02d}.{args.format}'
          outputPath = args.outputDir / outputFilename
        else:
          outputPath = Path(f'track_{trackNum:02d}.{args.format}')

        logger.info(f'Encoding to {args.format.upper()}...')
        enc.encode(tempWav, outputPath)
        logger.info(f'Created: {outputPath}')
        tempWav.unlink()
    except exceptions.RipError as e:
      logger.error(f'Track {trackNum} failed: {e}')

      if tempWav.exists():
        tempWav.unlink()

      continue

  if args.eject:
    logger.info('Ejecting CD...')

    try:
      import subprocess

      subprocess.run(['eject', str(args.device)], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
      logger.warning('Failed to eject CD (eject command not found or failed)')


def main():
  """Main entry point for rip command."""

  args = parseArguments()

  setupLogging(verbose=args.verbose or args.debug, quiet=args.quiet)

  logger = logging.getLogger(__name__)

  if args.list_devices:
    devices = utils.findCdDevices()

    if devices:
      print('Available CD/DVD devices:')

      for device in devices:
        print(f'  {device}')
    else:
      print('No CD/DVD devices found.')

    sys.exit(0)

  if args.superlazy:
    args.lazy = True
    args.eject = True

  if args.lazy:
    args.cddb = True
    args.tag = True

  try:
    ripTracks(args)
  except KeyboardInterrupt:
    logger.info('\nInterrupted by user.')
    sys.exit(1)
  except Exception as e:
    logger.error(f'Unexpected error: {e}')

    if args.debug:
      raise

    sys.exit(1)


if __name__ == '__main__':
  main()
