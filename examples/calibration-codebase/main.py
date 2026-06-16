#!/usr/bin/env python3
"""Top-level launcher so the toolchain can run as `python main.py ...`."""

import sys

from stacklang.cli import main

if __name__ == "__main__":
    sys.exit(main())
