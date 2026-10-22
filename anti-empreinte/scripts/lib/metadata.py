import json
import re
import zipfile

from common import ENCODING, DECODE_ERRORS
from signatures import GENERATORS, PROVENANCE

OFFICE_PARTS = ("docProps/app.xml", "docProps/core.xml", "meta.xml")
FIELD = re.compile(r"<(?:\w+:)?(Application|AppVersion|creator|lastModifiedBy|generator|Company|TotalTime|"
                   r"revision|editing-cycles)>([^<]*)<", re.IGNORECASE)
PDF_FIELD = re.compile(rb"/(Producer|Creator)\s*\(([^)]{0,200})\)|<(?:pdf:Producer|xmp:CreatorTool)>([^<]{0,200})<")
MAX_IMAGE = 25 * 1024 * 1024
ZERO_TIME = {"0", "1", "PT0S"}


def office(path):
    found = []
    try:
        with zipfile.ZipFile(path) as archive:
            names = set(archive.namelist())
            text = " ".join(archive.read(part).decode(ENCODING, DECODE_ERRORS) for part in OFFICE_PARTS
                            if part in names)
    except (OSError, zipfile.BadZipFile, KeyError):
        return ["unreadable archive"]
    fields = {name.lower(): value.strip() for name, value in FIELD.findall(text)}
    for name, value in fields.items():
        if value and GENERATORS.search(value):
            found.append(f"{name} = {value}")
    if fields.get("totaltime") in ZERO_TIME and fields.get("revision", "1") == "1":
        found.append("no editing time and a single revision")
    return found


def pdf(path):
    try:
        raw = path.read_bytes()
    except OSError:
        return ["unreadable file"]
    found = []
    for name, value, xmp in PDF_FIELD.findall(raw):
        text = (value or xmp).decode("latin-1", DECODE_ERRORS)
        label = name.decode() if name else "xmp"
        if GENERATORS.search(text):
            found.append(f"{label} = {text}")
    return sorted(set(found))


def notebook(path):
    try:
        cells = json.loads(path.read_text(encoding=ENCODING)).get("cells", [])
    except (OSError, ValueError, AttributeError):
        return ["unreadable notebook"]
    counts = [cell.get("execution_count") for cell in cells if cell.get("cell_type") == "code"]
    if len(counts) < 2:
        return []
    if all(count is None for count in counts):
        return ["every execution_count is empty"]
    if counts == list(range(1, len(counts) + 1)):
        return ["execution_count runs 1 to n with no gap"]
    return []


def image(path):
    try:
        if path.stat().st_size > MAX_IMAGE:
            return []
        raw = path.read_bytes()
    except OSError:
        return ["unreadable image"]
    return [label for label, marker in PROVENANCE if marker in raw]


def document(path):
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return pdf(path)
    if suffix == ".ipynb":
        return notebook(path)
    return office(path)
