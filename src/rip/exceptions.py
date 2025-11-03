# Copyright (C) 2003 Gregory J. Smethells
# Copyright (C) 2025 Gregory J. Smethells
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

"""
Custom exception classes for rip.

This module defines domain-specific exceptions for CD ripping and encoding operations.
"""


class RipError(Exception):
  """Base exception for all rip-related errors."""

  pass


class RipperNotFoundError(RipError):
  """Raised when no CD ripper tool is found on PATH."""

  pass


class EncoderNotFoundError(RipError):
  """Raised when no encoder tool is found for the requested format."""

  pass


class MetadataError(RipError):
  """Raised when metadata lookup fails."""

  pass


class DeviceError(RipError):
  """Raised when CD device is not found or not accessible."""

  pass


class TrackError(RipError):
  """Raised when track number is invalid or track cannot be read."""

  pass


class EncodingError(RipError):
  """Raised when encoding fails."""

  pass


class TaggingError(RipError):
  """Raised when file tagging fails."""

  pass


class ConfigError(RipError):
  """Raised when configuration is invalid."""

  pass
