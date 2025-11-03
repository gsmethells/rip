# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0] - 2024-11-02

### Added
- Complete Python 3.11+ rewrite of the original Perl script
- MusicBrainz metadata integration (replaces defunct CDDB)
- Interactive release selection for multiple matches
- Support for Opus format (recommended default)
- Support for AAC/M4A format (via fdkaac or qaac)
- Multi-format audio tagging with mutagen library
- M3U and PLS playlist generation
- `--list-devices` flag to discover CD/DVD drives
- Comprehensive command-line help with `--help`
- Automatic `~/.riprc` creation with sensible defaults
- External USB CD/DVD drive support
- Modern logging and error handling
- Structured Album and Track data models

### Changed
- Default format changed from MP3 to Opus (better quality/size ratio)
- Default bitrate increased from 160 to 192 kbps
- Metadata source changed from CDDB to MusicBrainz
- Configuration file format remains backward compatible
- Improved error messages with proper exception handling
- Better Unicode support for international characters

### Removed
- Dependency on obsolete CDDB service
- Support for obsolete encoders (gogo, bladeenc, notlame)
- Manual stderr redirection to /tmp files

### Fixed
- Unicode handling in filenames and metadata
- Proper cleanup of temporary WAV files on interruption
- Better handling of special characters in filenames

### Technical
- Built with modern Python tooling (pyproject.toml, PEP 621)
- Code quality enforced with ruff and prism-blanklines
- Follows CLAUDE.md coding standards
- Modular architecture with clear separation of concerns
- Comprehensive docstrings with type annotations
- GPL-2.0-or-later license (same as original)

### Migration from 1.x
- Existing `~/.riprc` files work without modification
- All command-line flags from 1.x are supported
- New flags are optional and backward compatible
- MusicBrainz provides better metadata than CDDB

## [1.07] - 2003-01-15 (Perl Version - Legacy)

Final version of the original Perl implementation. See legacy CHANGELOG for full history.

### Notable Features (1.07)
- CDDB metadata support
- MP3, Ogg Vorbis, and FLAC encoding
- Lazy and superlazy workflows
- Multiple ripper support (cdparanoia, cdda2wav)
- Multiple encoder support (lame, oggenc, flac, gogo, bladeenc, notlame)
- Configurable via `~/.riprc`

[Unreleased]: https://github.com/gsmethells/rip/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/gsmethells/rip/releases/tag/v2.0.0
[1.07]: https://github.com/gsmethells/rip/releases/tag/v1.07
