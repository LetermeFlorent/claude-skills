import hashlib
import json
from pathlib import Path

ENCODING = "utf-8"


def read_json(path):
    path = Path(path)
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding=ENCODING))
    except ValueError:
        return {}
    return data if isinstance(data, dict) else {}


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding=ENCODING)


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
