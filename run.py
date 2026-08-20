"""Convenience wrapper to run the main entrypoint.

Historically this project used `run.py`; the canonical entrypoint is now
`main.py`. Keep `run.py` as a small wrapper so older instructions still work.
"""
from main import main


if __name__ == "__main__":
    # Run the canonical main entrypoint only once.
    main()
