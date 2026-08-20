"""Mutation-test a guard: break the code on purpose and prove a test notices.

    python scripts/mutate.py mutations.json

REFUSES TO RUN ON A DIRTY WORKING TREE, which is the entire point of this file
existing. Reverting a mutation means `git checkout -- <file>`, and that restores
the last COMMIT — so if the fix you are testing is still uncommitted, the revert
throws the fix away along with the mutant. That has now happened five times in
this project. The rule "check git status first" was written down after the
third and ignored after the fourth, so it is enforced here instead of
remembered.

The mutations file is a JSON list:

    [
      {"name": "approve without a file is allowed",
       "file": "students/views.py",
       "old":  "if not sheet.has_project_file:",
       "new":  "if False:"},
      ...
    ]

Each is applied alone, the tests run, and the file is reverted before the next.
A mutation that leaves the suite GREEN is a guard that does not discriminate —
that is the finding, and it is printed as LIVES.
"""

import json
import subprocess
import sys
from pathlib import Path

PY = r".venv\Scripts\python.exe"


def sh(*args, **kw):
    return subprocess.run(args, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", **kw)


def dirty_paths():
    """Tracked files with uncommitted changes. Untracked files do not matter —
    `git checkout --` cannot destroy what git has never seen."""
    out = sh("git", "status", "--porcelain").stdout.splitlines()
    return [line[3:].strip() for line in out if line[:2] != "??"]


def run_tests(label):
    proc = sh(PY, "manage.py", "test", label, "-v0")
    text = proc.stdout + proc.stderr
    first = next((l for l in text.splitlines()
                  if l.startswith(("FAIL:", "ERROR:"))), "")
    return proc.returncode == 0, first


def main():
    if len(sys.argv) < 3:
        sys.exit("usage: python scripts/mutate.py <mutations.json> <test-label>")
    spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    label = sys.argv[2]

    # THE GATE. Not a warning.
    targets = {m["file"].replace("\\", "/") for m in spec}
    blocked = sorted(targets & {p.replace("\\", "/") for p in dirty_paths()})
    if blocked:
        sys.exit(
            "REFUSING: these files have uncommitted changes and are about to be\n"
            "reverted with `git checkout --`, which would delete that work:\n  "
            + "\n  ".join(blocked)
            + "\n\nCommit first. This has cost real work five times."
        )

    green, _ = run_tests(label)
    if not green:
        sys.exit("baseline is not green — fix that before mutating")
    print("baseline green\n")

    survivors = []
    for m in spec:
        path = Path(m["file"])
        src = path.read_text(encoding="utf-8")
        if m["old"] not in src:
            print("SKIP   %-52s (anchor not found)" % m["name"])
            continue
        path.write_text(src.replace(m["old"], m["new"], 1), encoding="utf-8")
        try:
            still_green, first = run_tests(label)
        finally:
            sh("git", "checkout", "HEAD", "--", str(path))
        if still_green:
            survivors.append(m["name"])
            print("LIVES  %-52s  <-- no test noticed" % m["name"])
        else:
            print("caught %-52s  %s" % (m["name"], first[:58]))

    left = dirty_paths()
    print("\n%d/%d caught" % (len(spec) - len(survivors), len(spec)))
    if left:
        print("WARNING: tree is not clean afterwards: %s" % left)
    if survivors:
        print("SURVIVORS — write a test for these:")
        for s in survivors:
            print("  -", s)
        sys.exit(1)


if __name__ == "__main__":
    main()
