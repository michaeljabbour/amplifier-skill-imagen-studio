"""Exercise the installed-location converter using a synthetic local fixture."""

import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def test_local_gradient_converts_to_text_html_and_back_to_png(tmp_path):
    source = tmp_path / "synthetic-gradient.png"
    image = Image.new("L", (32, 16))
    image.putdata([x * 255 // 31 for _ in range(16) for x in range(32)])
    image.save(source)
    converter = ROOT / "skills/imagen-studio/scripts/asciiart.py"
    text = tmp_path / "gradient.txt"
    webpage = tmp_path / "gradient.html"
    output = tmp_path / "rasterized.png"
    subprocess.run(
        [
            sys.executable,
            str(converter),
            "to-ascii",
            str(source),
            "--width",
            "16",
            "--out",
            str(text),
            "--html",
            str(webpage),
        ],
        check=True,
        capture_output=True,
    )
    lines = text.read_text().splitlines()
    assert len(lines) == 4
    assert all(len(line) == 16 for line in lines)
    assert len(set("".join(lines))) > 1
    assert "<!doctype html>" in webpage.read_text().lower()
    assert "<pre>" in webpage.read_text()
    subprocess.run(
        [sys.executable, str(converter), "to-image", str(text), "--out", str(output)],
        check=True,
        capture_output=True,
    )
    with Image.open(output) as raster:
        assert raster.format == "PNG"
        assert min(raster.size) > 0
