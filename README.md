# rip - CD Ripper and Encoder

Modern Python rewrite of the classic Perl CD ripper, providing a unified interface for ripping audio CDs and encoding them to multiple formats.

## Features

- **Multiple Format Support**: MP3, FLAC, Opus, Ogg Vorbis, AAC/M4A
- **Metadata Lookup**: Automatic CD metadata from MusicBrainz (replaces defunct CDDB)
- **Audio Tagging**: ID3/Vorbis/MP4 tags for all supported formats
- **Flexible Workflows**: Manual, lazy, or superlazy modes
- **Playlist Generation**: M3U and PLS playlist creation
- **External Drive Support**: Works with USB CD/DVD drives
- **Backward Compatible**: Uses same `~/.riprc` config format as original

## Requirements

### Python & Dependencies

- Python 3.11 or later
- Python packages (installed automatically):
  - `mutagen` - Audio file tagging
  - `musicbrainzngs` - MusicBrainz metadata lookup
  - `discid` - CD disc identification

### External Tools

**CD Ripper** (one required):
- `cdparanoia` (recommended) - http://www.xiph.org/paranoia/
- `cdda2wav` - http://www.escape.de/users/colossus/cdda2wav.html

**Encoders** (at least one required):
- `lame` - MP3 encoding - http://lame.sourceforge.net/
- `flac` - FLAC encoding - https://xiph.org/flac/
- `opusenc` - Opus encoding (recommended) - https://opus-codec.org/
- `oggenc` - Ogg Vorbis encoding - https://xiph.org/vorbis/
- `fdkaac` or `qaac` - AAC/M4A encoding

**Optional**:
- `eject` - CD tray control

## Installation

### From Source

```bash
git clone https://github.com/gsmethells/rip.git
cd rip
pip install -e .
```

### From PyPI (when published)

```bash
pip install cd-ripper
```

## Quick Start

### Basic Usage

```bash
# Rip specific tracks to default format (Opus)
rip 1 2 3

# Rip all tracks from CD
rip

# Rip to MP3 at 320 kbps
rip --format mp3 --bitrate 320

# Rip to FLAC (lossless)
rip --format flac
```

### With Metadata

```bash
# Fetch metadata from MusicBrainz and auto-rename
rip --cddb

# Also tag the files
rip --cddb --tag
```

### Lazy Workflows

```bash
# Lazy mode: fetch metadata, tag files
rip --lazy

# Superlazy mode: lazy + auto-eject when done
rip --superlazy

# Short form (equivalent to --superlazy)
rip -S
```

### Other Options

```bash
# List available CD/DVD devices
rip --list-devices

# Use specific device
rip --device /dev/sr1

# Generate playlist
rip --cddb --tag --generate

# Output to specific directory
rip --move ~/Music/NewAlbum
```

## Configuration

Configuration is stored in `~/.riprc` (automatically created on first run):

```ini
# Default format (mp3, flac, opus, ogg, m4a)
format = "opus"

# Default bitrate (in kbps)
kbps = 192

# Default flags for lazy rips
lazy = "-c -t -e"

# Default flags for superlazy rips
superlazy = "-c -t -e"

# Default CD device
dev = "/dev/cdrom"

# Quality settings for VBR encoding
qualityOPUS = 6
qualityLAME = 2
qualityOGGENC = 9
```

## Command-Line Options

### Format Options
- `-f, --format` - Output format (mp3, flac, opus, ogg, m4a)
- `-b, --bitrate` - Bitrate in kbps for CBR encoding
- `-q, --quality` - Quality setting for VBR encoding
- `-V, --vbr` - Use variable bitrate encoding
- `-w, --wav` - Rip to WAV only (no encoding)

### Device Options
- `-d, --device` - CD device path
- `--list-devices` - List available CD/DVD devices

### Ripping Options
- `-p, --paranoia` - Enable paranoia mode (default)
- `--no-paranoia` - Disable paranoia mode
- `-s, --speed` - CD read speed

### Metadata Options
- `-c, --cddb` - Fetch metadata from MusicBrainz
- `-t, --tag` - Tag output files with metadata

### Output Options
- `-m, --move` - Move output files to specified directory
- `-n, --nounderscore` - Use spaces instead of underscores in filenames
- `-g, --generate` - Generate playlist file

### Workflow Options
- `-L, --lazy` - Lazy mode (fetch metadata, tag, organize)
- `-S, --superlazy` - Superlazy mode (lazy + auto-eject)
- `-e, --eject` - Eject CD when finished

### Miscellaneous
- `-v, --verbose` - Enable verbose output
- `-Q, --quiet` - Suppress all output except errors
- `--debug` - Enable debug mode
- `--version` - Show version and exit
- `-h, --help` - Show help message

## Examples

### Complete Album Rip

```bash
# Superlazy: rip entire CD, fetch metadata, tag, organize, and eject
rip -S
```

This will:
1. Query MusicBrainz for CD metadata
2. Rip all tracks from the CD
3. Encode to Opus (or your configured format)
4. Tag files with album/artist/track information
5. Eject the CD when done

### High-Quality MP3 Collection

```bash
# VBR MP3 at quality level 0 (highest)
rip --format mp3 --vbr --quality 0 --cddb --tag
```

### Archival FLAC Rip

```bash
# Lossless FLAC with metadata
rip --format flac --cddb --tag --move ~/Music/Archive
```

### Specific Tracks

```bash
# Rip tracks 1, 3-5, and 7 to high-bitrate Opus
rip --format opus --bitrate 256 1 3-5 7
```

## Migration from Perl Version

The Python version is **fully backward compatible** with the original Perl version:

- ✅ Same `~/.riprc` configuration format
- ✅ Same command-line flags (with some new additions)
- ✅ Same workflows (lazy/superlazy)
- ✅ Better metadata (MusicBrainz vs defunct CDDB)
- ✅ More formats supported (Opus, AAC/M4A)

Your existing `~/.riprc` will work without changes.

## Development

### Setup Development Environment

```bash
git clone https://github.com/gsmethells/rip.git
cd rip
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

### Code Quality

```bash
# Run linting
ruff check src/rip/

# Run formatting
ruff format src/rip/

# Check blank line rules
prism --check src/rip/

# Fix blank line violations
prism src/rip/
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=rip --cov-report=html
```

## Architecture

```
src/rip/
  cli.py         - Command-line interface (argparse)
  config.py      - Configuration management (~/.riprc)
  ripper.py      - CD ripping (cdparanoia/cdda2wav wrapper)
  encoder.py     - Audio encoding (multi-format)
  metadata.py    - MusicBrainz metadata lookup
  tagger.py      - Audio file tagging (mutagen)
  playlist.py    - Playlist generation (M3U/PLS)
  utils.py       - Utility functions
  exceptions.py  - Custom exception classes
```

See [design.md](design.md) for detailed architecture documentation.

## License

GNU General Public License v2.0 or later

Copyright (C) 2003 Gregory J. Smethells
Copyright (C) 2024 Gregory J. Smethells

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

See [COPYING](COPYING) for full license text.

## Credits

- Original Perl version (2003) by Gregory J. Smethells
- Python rewrite (2024) by Gregory J. Smethells
- Uses [MusicBrainz](https://musicbrainz.org/) for metadata
- Uses [mutagen](https://mutagen.readthedocs.io/) for audio tagging

## Support

- **Issues**: https://github.com/gsmethells/rip/issues
- **Documentation**: See `design.md` and `CLAUDE.md`

## History

**rip 2.0.0** (2024) - Complete Python rewrite
- Modern Python 3.11+ codebase
- MusicBrainz metadata (replaces defunct CDDB)
- Multi-format tagging with mutagen
- Opus and AAC/M4A support
- Improved error handling and logging

**rip 1.07** (2003) - Final Perl version
- Original Perl implementation
- CDDB metadata support
- MP3, Ogg Vorbis, FLAC support
