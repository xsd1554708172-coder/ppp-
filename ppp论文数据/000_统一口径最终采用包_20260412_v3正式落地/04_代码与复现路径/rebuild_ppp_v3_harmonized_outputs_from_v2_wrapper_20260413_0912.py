from pathlib import Path
import runpy

SCRIPT = Path(__file__).with_name('refresh_core_v3_runtime_files_20260413_0912.py')
runpy.run_path(str(SCRIPT), run_name='__main__')
