# -*- coding: utf-8 -*-
"""Deprecated compatibility wrapper.
Official script: refresh_core_v3_runtime_files_20260413_0256.py
Boundary: wrapper only; not a full package rebuild entry.
"""
from __future__ import annotations
import runpy
from pathlib import Path
TARGET = Path(__file__).resolve().with_name('refresh_core_v3_runtime_files_20260413_0256.py')
if __name__ == '__main__':
    runpy.run_path(str(TARGET), run_name='__main__')
