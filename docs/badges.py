import os
from pathlib import Path

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir)

from log_generator import __version__  # noqa
from pybadges import badge  # noqa

DOCS_PATH = Path("docs")

with open(DOCS_PATH / Path("version_badge.svg"), "w") as svg:
    svg.write(badge(left_text="version", right_text=__version__, right_color="red"))
