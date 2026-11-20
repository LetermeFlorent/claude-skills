import glob
import os
import shutil
import subprocess
import sys
from pathlib import Path

TOOL = "blender-3d"
ENCODING = "utf-8"
INTERRUPTED = 130
FAILED = 1
REFUSED = 2
MARK = "@@ "
ENV_VAR = "BLENDER_EXE"
KEEP_PREFS = "BLENDER_KEEP_PREFS"
LOW_PRIORITY = getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0)
INSIDE = Path(__file__).resolve().parent / "inside"
BLEND = ".blend"
SEARCH = ("~/Tools/blender-*/blender.exe", "C:/Program Files/Blender Foundation/*/blender.exe",
          "~/Tools/blender-*/blender", "/opt/blender*/blender", "/Applications/Blender.app/Contents/MacOS/Blender")

def guard(main, hint):
    sys.stdout.reconfigure(encoding=ENCODING, errors="replace")
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(INTERRUPTED)
    except Exception as error:
        print(f"{TOOL}: {type(error).__name__}: {error}")
        print(f"by hand: {hint}")
        sys.exit(FAILED)


def refuse(problems):
    for problem in problems:
        print(f"refused: {problem}")
    sys.exit(REFUSED)


def find_blender(env=None, which=shutil.which, matches=glob.glob):
    env = os.environ if env is None else env
    if env.get(ENV_VAR):
        return env[ENV_VAR] if Path(env[ENV_VAR]).is_file() else None
    found = which("blender")
    if found:
        return found
    for pattern in SEARCH:
        hits = sorted(matches(os.path.expanduser(pattern)))
        if hits:
            return hits[-1]
    return None


def blender_or_refuse():
    exe = find_blender()
    if not exe:
        refuse([f"no Blender found: install it or set {ENV_VAR} to blender.exe or the blender binary"])
    return exe


def command(exe, source, inside, args):
    opened = [str(source)] if source and str(source).lower().endswith(BLEND) else []
    startup = [] if os.environ.get(KEEP_PREFS) == "1" else ["--factory-startup"]
    return [exe, "--background", *startup, *opened, "--python-exit-code", str(FAILED),
            "--python", str(INSIDE / inside), "--", *map(str, args)]


def existing(path, problems, what):
    if path != "-" and not Path(path).is_file():
        problems.append(f"{what} not found: {path}")
    return path if path == "-" else str(Path(path).resolve())


def launch(source, inside, rest, timeout):
    exe = blender_or_refuse()
    return run(command(exe, None if source == "-" else source, inside, rest), timeout)


def run(argv, timeout):
    try:
        done = subprocess.run(argv, capture_output=True, text=True, encoding=ENCODING, errors="replace",
                              timeout=timeout, creationflags=LOW_PRIORITY)
    except subprocess.TimeoutExpired:
        return None, f"Blender still running after {timeout} s, stopped"
    return done.returncode, done.stdout + done.stderr


def useful(output):
    return [line[len(MARK):] for line in output.splitlines() if line.startswith(MARK)]


def errors(output):
    lines = output.splitlines()
    start = next((i for i, line in enumerate(lines) if line.startswith("Traceback")), None)
    if start is not None:
        return lines[start:]
    return [line for line in lines if line.startswith(("Error", "ERROR")) or "Error:" in line]


def report(code, output):
    if code is None:
        print(f"failed: {output}")
        sys.exit(FAILED)
    for line in useful(output):
        print(line)
    if code != 0:
        print(f"failed: Blender exit code {code}")
        for line in errors(output):
            print(f"  {line}")
        sys.exit(FAILED)
