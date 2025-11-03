# rip - Design Document

## Overview

`rip` is a CD ripper and encoder that provides a unified interface for ripping audio CDs and encoding them to various formats (MP3, FLAC, Opus, Ogg Vorbis, AAC). This is a modern Python rewrite of the original 2003 Perl script.

**Key Features:**
- Rip audio CDs using cdparanoia or cdda2wav
- Encode to multiple formats: MP3, FLAC, Opus, Ogg Vorbis, AAC/M4A
- Automatic metadata lookup via MusicBrainz
- Auto-rename and organize files based on metadata
- Batch processing support
- Playlist generation (M3U, PLS)
- ID3/tag support for all formats via mutagen

## Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI (argparse)                       │
│  Parse arguments, load config, orchestrate workflow         │
└──────────────┬──────────────────────────────────────────────┘
               │
               ├──> Config (configparser)
               │    Load ~/.riprc, provide defaults
               │
               ├──> Ripper (subprocess wrapper)
               │    ├─> cdparanoia
               │    └─> cdda2wav
               │
               ├──> Encoder (subprocess wrapper)
               │    ├─> lame (MP3)
               │    ├─> flac (FLAC)
               │    ├─> opusenc (Opus)
               │    ├─> oggenc (Ogg Vorbis)
               │    └─> fdkaac/qaac (AAC/M4A)
               │
               ├──> Metadata (MusicBrainz API)
               │    ├─> musicbrainzngs
               │    ├─> discid
               │    └─> pyacoustid (fallback)
               │
               ├──> Tagger (mutagen)
               │    Write ID3/Vorbis/FLAC tags
               │
               └──> Utils
                    Helpers for file ops, track parsing, etc.
```

### Module Organization

```
src/rip/
  __init__.py        - Package initialization, version info
  cli.py             - Command-line interface (argparse)
  config.py          - Configuration management (~/.riprc)
  ripper.py          - CD ripping logic (cdparanoia wrapper)
  encoder.py         - Audio encoding logic (lame/flac/opus/etc.)
  metadata.py        - MusicBrainz/AcoustID metadata lookup
  tagger.py          - File tagging with mutagen
  playlist.py        - M3U/PLS playlist generation
  utils.py           - Utility functions (track parsing, file ops)
  exceptions.py      - Custom exception classes

test/
  test_config.py     - Config class tests
  test_ripper.py     - Ripper class tests
  test_encoder.py    - Encoder class tests
  test_metadata.py   - Metadata lookup tests (mocked)
  test_tagger.py     - Tagger tests
  test_utils.py      - Utility function tests
```

## Important Design Decisions

### 1. Backward Compatibility with ~/.riprc

**Decision:** Keep the original `~/.riprc` format (key = value INI-style without sections)

**Rationale:**
- Seamless migration for existing users
- No breaking changes to configuration
- Familiar format
- Users can keep their existing config files

**Implementation:** Use `configparser` with a dummy `[DEFAULT]` section prepended when reading.

### 2. Python Standard Library First

**Decision:** Minimize external dependencies, prefer stdlib where possible

**Core dependencies:**
- `mutagen` - Required for multi-format tagging
- `musicbrainzngs` - Required for metadata lookup
- `discid` - Required for MusicBrainz disc identification

**Stdlib usage:**
- `argparse` - CLI parsing (not Click)
- `configparser` - Config file parsing
- `subprocess` - Wrapper for external tools
- `pathlib` - Path handling
- `logging` - Logging and error reporting

**Rationale:**
- Easier installation
- Fewer supply chain concerns
- More maintainable long-term
- Follows CLAUDE.md principles (KISS, YAGNI)

### 3. Subprocess Wrappers, Not Native Libraries

**Decision:** Wrap existing CLI tools (cdparanoia, lame, etc.) via subprocess, not native Python audio libraries

**Rationale:**
- Matches original Perl design
- These tools are battle-tested and high-quality
- Native Python audio encoding libraries are less mature
- Users already have these tools installed
- Simpler implementation
- Better error messages from the actual tools

**Implementation:** Use `subprocess.run()` with proper error handling and logging.

### 4. Modern Defaults, Backward Compatible

**Decision:** Default to Opus format but support all original formats

**Default format:** Opus (best quality-to-size ratio in 2025)
**Default bitrate:** 192 kbps (or quality 6 for VBR)
**Supported formats:** MP3, FLAC, Opus, Ogg Vorbis, AAC/M4A

**Rationale:**
- Opus is superior to MP3/Ogg Vorbis for modern use
- Users can still choose MP3/FLAC if preferred
- Gradually migrate users to better codec

### 5. MusicBrainz Instead of CDDB

**Decision:** Replace defunct CDDB with MusicBrainz API

**Primary:** MusicBrainz via discid
**Fallback:** AcoustID audio fingerprinting

**Rationale:**
- CDDB/freedb.org is defunct (shutdown ~2020)
- MusicBrainz is the modern standard
- AcoustID provides fallback for discs not in MB database
- Better metadata quality

### 6. Object-Oriented, Not Procedural

**Decision:** Use classes for Ripper, Encoder, Metadata, etc.

**Rationale:**
- Better separation of concerns
- Easier to test
- More maintainable than 2,303 lines of procedural Perl
- Follows Python best practices
- Matches CLAUDE.md guidelines

**Example:**
```python
class Ripper:
  def __init__(self, device):
    self.device = device
    self.tool = self._findRipper()

  def ripTrack(self, trackNum):
    # Implementation
```

### 7. Exceptions for Error Handling

**Decision:** Use custom exception classes, not print+exit

**Custom exceptions:**
- `RipError` - Base exception
- `RipperNotFoundError` - No ripper tool available
- `EncoderNotFoundError` - No encoder tool available
- `MetadataError` - Metadata lookup failed
- `DeviceError` - CD device not found/accessible

**Rationale:**
- Follows CLAUDE.md control flow rules
- Better error propagation
- Easier to test
- More Pythonic

### 8. Logging, Not stderr Redirection

**Decision:** Use Python's `logging` module, not manual stderr redirection to /tmp files

**Rationale:**
- The Perl version redirects stderr to /tmp/rip-stderr
- Python logging is more flexible and standard
- Can configure log levels (DEBUG, INFO, WARNING, ERROR)
- No temp files to clean up
- Follows CLAUDE.md observability guidelines

### 9. Progressive Enhancement

**Decision:** Build MVP first (Phase 1-3), add advanced features later (Phase 4-5)

**MVP (Weeks 1-5):**
- Basic ripping and encoding
- MusicBrainz metadata
- File tagging
- Lazy/superlazy workflows

**Future enhancements:**
- Parallel ripping/encoding
- Batch mode (multiple CDs)
- Resume support
- Album art embedding
- GUI frontend

## Data Flow

### Simple Workflow (rip 1 2 3)
```
1. CLI parses args: tracks [1, 2, 3]
2. Config loads ~/.riprc defaults
3. For each track:
   a. Ripper.ripTrack() → temp.wav
   b. Encoder.encode(temp.wav) → track.opus
   c. Clean up temp.wav
```

### Lazy Workflow (rip -c)
```
1. CLI parses args: -c flag set
2. Config loads ~/.riprc defaults
3. Metadata.lookup(device) → Album object
4. For each track in album:
   a. Ripper.ripTrack() → temp.wav
   b. Encoder.encode(temp.wav) → proper_name.opus
   c. Tagger.tag(proper_name.opus, track_metadata)
   d. Clean up temp.wav
```

### Superlazy Workflow (rip -S)
```
1. CLI parses args: -S flag set
2. Config loads ~/.riprc superlazy defaults
3. Metadata.lookup(device) → Album object
4. Create directory: Artist/Album/
5. For each track:
   a. Ripper.ripTrack() → temp.wav
   b. Encoder.encode(temp.wav) → Artist/Album/NN - Title.opus
   c. Tagger.tag(file, metadata)
   d. Clean up temp.wav
6. Generate playlist in Artist/Album/
7. Eject CD tray (if -e flag)
```

## Testing Strategy

### Unit Tests
- **Config**: Test .riprc parsing, defaults, edge cases
- **Ripper**: Mock subprocess.run(), test command generation
- **Encoder**: Mock subprocess.run(), test format selection
- **Metadata**: Mock MusicBrainz API responses
- **Tagger**: Test with temporary files
- **Utils**: Test track parsing, filename sanitization

### Integration Tests
- End-to-end workflow with mock CD data
- Test lazy/superlazy modes
- Test error handling and recovery

### Manual Testing
- Test with actual CDs and drives
- Verify metadata lookup
- Verify audio quality
- Test on multiple Linux distributions

## Security Considerations

1. **Input Validation:**
   - Sanitize all filenames (remove shell-unsafe characters)
   - Validate track numbers (1-99 range)
   - Validate device paths (no path traversal)

2. **Subprocess Safety:**
   - Use `subprocess.run()` with list args (not shell=True)
   - Never interpolate user input into shell commands
   - Properly escape all arguments

3. **File Operations:**
   - Use pathlib for safe path operations
   - Check permissions before writing
   - Use tempfile for temporary files

## Performance Considerations

1. **Sequential processing** (Phase 1-3): Rip one track at a time
2. **Parallel processing** (Phase 4): Use asyncio to rip multiple tracks simultaneously
3. **Metadata caching**: Cache MusicBrainz lookups locally to reduce API calls
4. **Lazy evaluation**: Only lookup metadata when needed (not for WAV-only rips)

## Dependencies

### Required External Tools
- **Ripper:** cdparanoia (primary) or cdda2wav (fallback)
- **Encoders:** lame (MP3), flac (FLAC), opusenc (Opus), oggenc (Ogg), fdkaac/qaac (AAC)
- **Optional:** eject (CD tray control)

### Python Dependencies
```toml
[project]
dependencies = [
  "mutagen>=1.47.0",
  "musicbrainzngs>=0.7.1",
  "discid>=1.2.0",
]

[project.optional-dependencies]
acoustid = ["pyacoustid>=1.3.0"]
progress = ["rich>=13.0.0"]
dev = ["pytest>=7.0.0", "pytest-cov>=4.0.0", "pytest-mock>=3.12.0", "ruff>=0.1.0"]
```

## Migration from Perl Version

### For Users
1. Install Python version: `pip install cd-ripper` (or from source)
2. Keep existing ~/.riprc (fully compatible)
3. Python version auto-upgrades config on first run
4. All original flags work identically

### For Developers
- Perl script remains in repo as reference
- Translation notes in each Python module
- Changelog documents differences

## Open Questions / Future Decisions

1. **Progress bars:** Use rich or tqdm? (Optional dependency)
2. **Album art:** Embed from MusicBrainz CAA? (Phase 4)
3. **Parallel encoding:** asyncio or multiprocessing? (Phase 4)
4. **GUI:** Add optional tkinter GUI? (Phase 5)
5. **Distribution:** PyPI package name? (cd-ripper vs rip vs audio-ripper)

## Version History

- **v2.0.0-dev** (2025-11): Initial Python rewrite
- **v1.07** (2003-01): Final Perl version
