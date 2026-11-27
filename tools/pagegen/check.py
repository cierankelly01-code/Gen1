"""Check that the page generators still reproduce the page sources in site/_src/pages.

Runs generate.py and generate_own_pages.py into a temporary folder (never into the repo) and
compares every page they write with the file of the same name in site/_src/pages, ignoring
CRLF/LF line endings. Fails with a list of the pages that differ, so a hand edit to a generated
page (or a generator change that was never run) is caught before the next generate overwrites it.

Run from anywhere:  python tools/pagegen/check.py        (add -v to print the differing lines)
Exit code 0 = in step, 1 = drift or a generator failed. Standard library only.
"""
import difflib
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAGES = HERE.parents[1] / "site" / "_src" / "pages"
GENERATORS = ("generate.py", "generate_own_pages.py")


def norm(path):
    return path.read_bytes().replace(b"\r\n", b"\n")


def main():
    verbose = "-v" in sys.argv[1:]
    problems, seen = [], {}
    for script in GENERATORS:
        with tempfile.TemporaryDirectory(prefix="pagegen-check-") as tmp:
            run = subprocess.run([sys.executable, "-E", "-s", str(HERE / script), tmp], capture_output=True, text=True)
            if run.returncode != 0:
                print(f"FAIL: {script} did not run:\n{run.stderr}")
                return 1
            pages = sorted(Path(tmp).glob("*"))
            if not pages:
                print(f"FAIL: {script} wrote no pages")
                return 1
            for gen in pages:
                if gen.name in seen:
                    problems.append((gen.name, f"written by both {seen[gen.name]} and {script}"))
                    continue
                seen[gen.name] = script
                live = PAGES / gen.name
                if not live.exists():
                    problems.append((gen.name, f"{script} writes it, but site/_src/pages has no such page (remove it from the generator)"))
                    continue
                a, b = norm(gen), norm(live)
                if a == b:
                    continue
                al, bl = a.decode("utf-8").split("\n"), b.decode("utf-8").split("\n")
                diff = list(difflib.unified_diff(al, bl, "generated", "site/_src/pages", n=0, lineterm=""))
                changed = sum(1 for d in diff if d[:1] in "+-" and d[:3] not in ("+++", "---"))
                problems.append((gen.name, f"{script} output differs from site/_src/pages ({changed} changed lines)"))
                if verbose:
                    sys.stdout.buffer.write(("\n".join(diff) + "\n").encode("utf-8"))

    if problems:
        print(f"FAIL: {len(problems)} generated page(s) out of step with site/_src/pages:")
        for name, why in problems:
            print(f"  {name}: {why}")
        print("Fix: put the change in tools/pagegen (not in the page), or if the page was edited on purpose,\n"
              "copy that edit into the generator. Then re-run: python tools/pagegen/check.py  (-v shows the lines)")
        return 1
    print(f"OK: {len(seen)} generated pages match site/_src/pages "
          f"({', '.join(f'{s}: {sum(1 for v in seen.values() if v == s)}' for s in GENERATORS)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
