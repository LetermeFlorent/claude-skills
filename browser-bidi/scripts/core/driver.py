import io
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

sys.dont_write_bytecode = True

from core.common import BIN_DIR, downloads_dir
from core.processes import powershell


CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
CFT = "https://googlechromelabs.github.io/chrome-for-testing"


def chrome_version():
    return powershell(f"(Get-Item '{CHROME}').VersionInfo.ProductVersion")


def build_of(version):
    return ".".join(version.split(".")[:3])


def fetch(url):
    with urllib.request.urlopen(url, timeout=120) as response:
        return response.read()


def ensure_driver():
    chrome = chrome_version()
    target = BIN_DIR / "chromedriver.exe"
    current = None
    if target.is_file():
        output = subprocess.run([str(target), "--version"], capture_output=True, text=True, timeout=30).stdout
        found = re.search(r"\d+\.\d+\.\d+\.\d+", output)
        current = found and found.group(0)
    if current and build_of(current) == build_of(chrome):
        return target, f"chromedriver {current} matches Chrome {chrome}"
    for key in (build_of(chrome), chrome.split(".")[0]):
        try:
            release = fetch(f"{CFT}/LATEST_RELEASE_{key}").decode("ascii").strip()
            break
        except urllib.error.HTTPError as error:
            if error.code != 404:
                raise
    else:
        raise LookupError(f"Chrome for Testing has no chromedriver for Chrome {chrome}")
    manifest = json.loads(fetch(f"{CFT}/{release}.json"))
    url = next(item["url"] for item in manifest["downloads"]["chromedriver"] if item["platform"] == "win64")
    with zipfile.ZipFile(io.BytesIO(fetch(url))) as archive:
        member = next(name for name in archive.namelist() if name.endswith("/chromedriver.exe"))
        target.parent.mkdir(parents=True, exist_ok=True)
        partial_file = target.with_name(target.name + ".part")
        partial_file.write_bytes(archive.read(member))
    os.replace(partial_file, target)
    return target, f"chromedriver {release} downloaded for Chrome {chrome}, replacing {current or 'nothing'}"


def write_prefs(profile):
    downloads = downloads_dir(profile)
    file = profile / "Default" / "Preferences"
    file.parent.mkdir(parents=True, exist_ok=True)
    downloads.mkdir(parents=True, exist_ok=True)
    prefs = json.loads(file.read_text(encoding="utf-8")) if file.is_file() else {}
    settings = prefs.setdefault("profile", {})
    settings.setdefault("default_content_setting_values", {}).update(
        {"geolocation": 2, "notifications": 2, "media_stream_camera": 2, "media_stream_mic": 2})
    settings["cookie_controls_mode"] = 1
    prefs.setdefault("download", {}).update(
        {"prompt_for_download": False, "directory_upgrade": True, "default_directory": str(downloads)})
    prefs["enable_do_not_track"] = True
    file.write_text(json.dumps(prefs), encoding="utf-8")
