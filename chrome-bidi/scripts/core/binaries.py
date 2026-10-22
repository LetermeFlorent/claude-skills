import ctypes
import io
import json
import os
import platform
import re
import subprocess
import urllib.error
import urllib.request
import winreg
import zipfile
from pathlib import Path

from core.common import BIN_DIR

CFT_BASE = "https://googlechromelabs.github.io/chrome-for-testing"
APP_PATHS = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
BEACON = r"Software\Google\Chrome\BLBeacon"
CHROME_RELATIVE = Path("Google", "Chrome", "Application", "chrome.exe")
INSTALL_ROOTS = ("ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA")
DRIVER_NAME = "chromedriver.exe"
DOWNLOAD_TIMEOUT = 120
PROBE_TIMEOUT = 30
HTTP_NOT_FOUND = 404
VERSION_NAME = "version"
VERSION = re.compile(r"\d+\.\d+\.\d+\.\d+")


def chrome_exe():
    for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        try:
            with winreg.OpenKey(hive, APP_PATHS) as key:
                found = Path(winreg.QueryValue(key, None).strip('"'))
        except OSError:
            continue
        if found.is_file():
            return found
    for variable in INSTALL_ROOTS:
        found = Path(os.environ.get(variable, "")) / CHROME_RELATIVE
        if os.environ.get(variable) and found.is_file():
            return found
    raise FileNotFoundError("chrome.exe is neither in App Paths nor under Program Files")


def file_version(path):
    library = ctypes.WinDLL(VERSION_NAME)
    size = library.GetFileVersionInfoSizeW(str(path), None)
    if not size:
        raise OSError(f"no version resource in {path}")
    data = ctypes.create_string_buffer(size)
    library.GetFileVersionInfoW(str(path), 0, size, data)
    pointer, length = ctypes.c_void_p(), ctypes.c_uint()
    if not library.VerQueryValueW(data, "\\", ctypes.byref(pointer), ctypes.byref(length)):
        raise OSError(f"unreadable version resource in {path}")
    fields = ctypes.cast(pointer, ctypes.POINTER(ctypes.c_uint32))
    high, low = fields[2], fields[3]
    return f"{high >> 16}.{high & 0xFFFF}.{low >> 16}.{low & 0xFFFF}"


def chrome_version():
    try:
        return file_version(chrome_exe())
    except OSError:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, BEACON) as key:
            return winreg.QueryValueEx(key, VERSION_NAME)[0]


def build_of(version):
    return ".".join(version.split(".")[:3])


def driver_version(path):
    done = subprocess.run([str(path), "--version"], capture_output=True, text=True, timeout=PROBE_TIMEOUT)
    found = VERSION.search(done.stdout)
    return found.group(0) if found else None


def fetch(url):
    with urllib.request.urlopen(url, timeout=DOWNLOAD_TIMEOUT) as response:
        return response.read()


def matching_release(chrome):
    for key in (build_of(chrome), chrome.split(".")[0]):
        try:
            return fetch(f"{CFT_BASE}/LATEST_RELEASE_{key}").decode("ascii").strip()
        except urllib.error.HTTPError as error:
            if error.code != HTTP_NOT_FOUND:
                raise
    raise LookupError(f"Chrome for Testing has no chromedriver for Chrome {chrome}")


def install(release, target):
    wanted = "win64" if platform.machine().endswith("64") else "win32"
    manifest = json.loads(fetch(f"{CFT_BASE}/{release}.json"))
    url = next(item["url"] for item in manifest["downloads"]["chromedriver"] if item["platform"] == wanted)
    with zipfile.ZipFile(io.BytesIO(fetch(url))) as archive:
        member = next(name for name in archive.namelist() if name.endswith("/" + DRIVER_NAME))
        target.parent.mkdir(parents=True, exist_ok=True)
        partial = target.with_name(target.name + ".part")
        partial.write_bytes(archive.read(member))
    os.replace(partial, target)


def ensure_driver():
    chrome = chrome_version()
    target = BIN_DIR / DRIVER_NAME
    current = driver_version(target) if target.is_file() else None
    if current and build_of(current) == build_of(chrome):
        return target, f"chromedriver {current} matches Chrome {chrome}"
    release = matching_release(chrome)
    install(release, target)
    return target, f"chromedriver {release} downloaded for Chrome {chrome}, replacing {current or 'nothing'}"
