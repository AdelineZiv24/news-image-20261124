# "The World in One Page — Tuesday Edition" — a one-image summary of
# Tuesday 24 November 2026's world news, built for make.fun's
# news-image-20261124 competition.
#
# The picture itself lives in this repository as entry.png (a newspaper front
# page drawn with frontpage.html and rendered by tools/render.py). This
# program's whole job is to deliver those exact bytes to the grader: it copies
# entry.png, from beside this file, to entry.png inside the output directory.
# It runs offline, with the standard library only, and writes the same bytes
# on every run, so two runs always produce identical output.
#
# Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
#   mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.png"


def output_dir() -> Path:
    """The grader's /output, or MAKEFUN_OUTPUT_DIR when set."""
    return Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))


def main() -> None:
    target_dir = output_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / "entry.png"
    shutil.copyfile(SOURCE, target)
    print(f"wrote {target} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
