"""Deliver the finished front page for 22 November 2026.

The picture itself lives in the repository as entry.png (drawn when the
entry was built). This program only carries that file into the folder the
grader points at with MAKEFUN_OUTPUT_DIR, then proves the copy arrived
whole by comparing size and SHA-256 on both sides. It uses nothing but
the Python standard library, needs no network, and writes the same bytes
on every run.
"""

import hashlib
import os
import sys

PICTURE = "entry.png"
CHUNK = 65536
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1048576


def digest_of(path):
    """Return (byte count, lowercase hex SHA-256) of a file's contents."""
    hasher = hashlib.sha256()
    total = 0
    with open(path, "rb") as handle:
        while True:
            piece = handle.read(CHUNK)
            if not piece:
                break
            hasher.update(piece)
            total += len(piece)
    return total, hasher.hexdigest()


def bundle_dir():
    """Folder holding this script, i.e. the repository root."""
    return os.path.dirname(os.path.abspath(__file__))


def target_dir():
    """Output folder the grader provides, or fail with a clear message."""
    out = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out:
        raise SystemExit("MAKEFUN_OUTPUT_DIR is not set; nowhere to deliver the picture")
    return out


def carry_picture(origin, destination):
    """Stream origin to destination in chunks and make it world-readable."""
    with open(origin, "rb") as src, open(destination, "wb") as dst:
        while True:
            piece = src.read(CHUNK)
            if not piece:
                break
            dst.write(piece)
    os.chmod(destination, 0o644)


def main():
    source = os.path.join(bundle_dir(), PICTURE)
    if not os.path.isfile(source):
        raise SystemExit("missing bundled picture: " + PICTURE)
    with open(source, "rb") as probe:
        head = probe.read(len(PNG_MAGIC))
    if head != PNG_MAGIC:
        raise SystemExit("bundled picture is not a PNG file")

    before = digest_of(source)
    if before[0] > MAX_BYTES:
        raise SystemExit("bundled picture is over the 1 MiB limit")

    out_dir = target_dir()
    os.makedirs(out_dir, exist_ok=True)
    final_path = os.path.join(out_dir, PICTURE)
    carry_picture(source, final_path)

    after = digest_of(final_path)
    if after != before:
        raise SystemExit("copy check failed: destination differs from the bundled picture")
    with open(final_path, "rb") as probe:
        if probe.read(len(PNG_MAGIC)) != PNG_MAGIC:
            raise SystemExit("copy check failed: destination is not a PNG file")
    print("delivered %s: %d bytes, sha256 %s" % (PICTURE, after[0], after[1]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
