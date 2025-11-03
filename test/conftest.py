# Copyright (C) 2003 Gregory J. Smethells
# Copyright (C) 2024 Gregory J. Smethells
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

"""Pytest configuration and fixtures."""

import sys
from unittest.mock import MagicMock

mockDiscid = MagicMock()
mockDiscid.DiscError = Exception
sys.modules['discid'] = mockDiscid
