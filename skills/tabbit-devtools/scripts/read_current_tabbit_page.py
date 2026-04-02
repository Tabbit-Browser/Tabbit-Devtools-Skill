#!/usr/bin/env python3

import pathlib
import runpy


if __name__ == "__main__":
    runpy.run_path(
        str(pathlib.Path(__file__).resolve().with_name("discover_tabbit_cdp.py")),
        run_name="__main__",
    )
