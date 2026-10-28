#!/usr/bin/env python3
"""Generate installed references from canonical source documents; verify drift."""

import argparse
import hashlib
import json
import posixpath
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/imagen-studio"
MIRRORS = {
    "docs/source-methods/design-visual-asset.md": "references/design-visual-asset.md",
    "docs/source-methods/image-ascii-art.md": "references/image-ascii-art.md",
    "context/image-production-policy.md": "references/image-production-policy.md",
    "context/imagen-awareness.md": "references/imagen-awareness.md",
    "schemas/artifact-manifest.schema.json": "references/artifact-manifest.schema.json",
}
SOURCE_REPO = "amplifier-bundle-imagen"
SOURCE_COMMIT = "ec6da7d9b45be033a23ccd37cafc419ffffdeda9"


def generated():
    outputs = {}
    records = []
    for source, dest in MIRRORS.items():
        path = ROOT / source
        raw = path.read_bytes()
        output = raw
        if path.suffix == ".md":

            def fix(match, source=source, dest=dest):
                ref = match[2]
                uri = urlsplit(ref)
                if uri.scheme or uri.netloc or not uri.path:
                    return match[0]
                key = posixpath.normpath(posixpath.join(posixpath.dirname(source), uri.path))
                if key in MIRRORS:
                    target = posixpath.relpath(MIRRORS[key], posixpath.dirname(dest))
                else:
                    target = (
                        "https://github.com/michaeljabbour/"
                        + SOURCE_REPO
                        + "/blob/"
                        + SOURCE_COMMIT
                        + "/"
                        + key
                    )
                return (
                    "["
                    + match[1]
                    + "]("
                    + target
                    + (("#" + uri.fragment) if uri.fragment else "")
                    + ")"
                )

            output = re.sub(r"(?<!!)\[([^\]]+)\]\(([^)\s]+)\)", fix, raw.decode()).encode()
        outputs[SKILL / dest] = output
        records.append(
            {
                "source": source,
                "destination": dest,
                "source_sha256": hashlib.sha256(raw).hexdigest(),
                "output_sha256": hashlib.sha256(output).hexdigest(),
            }
        )
    outputs[SKILL / "reference-sources.json"] = (json.dumps(records, indent=2) + "\n").encode()
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for path, content in generated().items():
        if args.check:
            if not path.is_file() or path.read_bytes() != content:
                raise SystemExit("Reference drift: " + str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    print("reference mirrors verified" if args.check else "reference mirrors generated")


if __name__ == "__main__":
    main()
