"""Benny's Buildings — Multifamily Investment Analyzer

Entry point for the desktop application.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app import BennysApp


def main():
    app = BennysApp()
    app.mainloop()


if __name__ == "__main__":
    main()
