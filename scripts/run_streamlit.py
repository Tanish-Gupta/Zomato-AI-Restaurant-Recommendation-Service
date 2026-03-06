"""
Launch the Streamlit restaurant recommendation UI.
Run from project root:
    python -m scripts.run_streamlit
"""
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
app_path = PROJECT_ROOT / "src" / "phase4_ui" / "streamlit_app.py"
env = {**os.environ, "PYTHONPATH": str(PROJECT_ROOT)}

if __name__ == "__main__":
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(app_path), "--server.port=8501"],
        cwd=str(PROJECT_ROOT),
        env=env,
    )
