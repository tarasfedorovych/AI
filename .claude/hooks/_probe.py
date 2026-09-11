import os
import sys
import tempfile

with open(os.path.join(tempfile.gettempdir(), "qa-pipeline-hook-probe.txt"), "a", encoding="utf-8") as f:
    f.write("fired cwd=%s argv0=%s stdin=%r\n" % (os.getcwd(), sys.argv[0], sys.stdin.read()[:80]))
