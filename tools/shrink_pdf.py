"""Shrink the capability pack: re-save the large photos as JPEG, touch nothing else. Then self-check."""
import re
import sys

import pypdf

src, out = sys.argv[1], sys.argv[2]

w = pypdf.PdfWriter(clone_from=src)
for page in w.pages:
    for im in page.images:
        pil = im.image
        if pil.size[0] >= 1000 and pil.mode in ("RGB", "L"):
            im.replace(pil, quality=86)
# No object pruning: the first attempt pruned a colour profile the logo still pointed at.
w.write(out)

# --- checks ---
old, new = pypdf.PdfReader(src), pypdf.PdfReader(out)
assert len(new.pages) == len(old.pages) == 2
for a, b in zip(old.pages, new.pages):
    assert a.extract_text() == b.extract_text(), "text changed"
    names_old = sorted(i.name.split(".")[0] for i in a.images)
    names_new = sorted(i.name.split(".")[0] for i in b.images)
    assert names_old == names_new, (names_old, names_new)
    for i in b.images:  # every image must decode, including the logo
        assert i.image.size[0] > 0

# every "N 0 R" reference in the raw file must point at an object that exists
raw = open(out, "rb").read()
defined = {int(m.group(1)) for m in re.finditer(rb"(?:^|[\r\n])(\d+) 0 obj", raw)}
refs = {int(m.group(1)) for m in re.finditer(rb"(\d+) 0 R", raw)}
missing = sorted(refs - defined)
print("objects", len(defined), "dangling refs", missing)
assert not missing, missing
import os

print(os.path.getsize(src), "->", os.path.getsize(out))
