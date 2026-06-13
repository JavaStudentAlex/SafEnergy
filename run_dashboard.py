#!/usr/bin/env python
import subprocess
import sys

if __name__ == "__main__":
    try:
        subprocess.run(["uv", "run", "streamlit", "run", "src/safenergy/api/dashboard.py"], check=True)
    except KeyboardInterrupt:
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
