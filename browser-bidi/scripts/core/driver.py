import io
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
import winreg
import zipfile
from pathlib import Path

sys.dont_write_bytecode = True

from core.common import BIN_DIR, downloads_dir
from core.processes import powershell


CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
CFT = "https://googlechromelabs.github.io/chrome-for-testing"
GECKO = "https://github.com/mozilla/geckodriver/releases"
APP_PATH = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe"


def find_firefox():
    for root in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
        try:
            with winreg.OpenKey(root, APP_PATH) as key:
                found = Path(winreg.QueryValue(key, None).strip('"'))
        except OSError:
            continue
        if found.is_file():
            return found
    for variable in ("ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA"):
        found = Path(os.environ.get(variable, "")) / "Mozilla Firefox" / "firefox.exe"
        if os.environ.get(variable) and found.is_file():
            return found
    raise FileNotFoundError("Firefox is not installed: no firefox.exe in App Paths, Program Files or LOCALAPPDATA")


def chrome_version():
    return powershell(f"(Get-Item '{CHROME}').VersionInfo.ProductVersion")


def build_of(version):
    return ".".join(version.split(".")[:3])


def fetch(url):
    with urllib.request.urlopen(url, timeout=120) as response:
        return response.read()


def ensure_chromedriver():
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
    unzip_to(target, fetch(url))
    return target, f"chromedriver {release} downloaded for Chrome {chrome}, replacing {current or 'nothing'}"


def unzip_to(target, data):
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        member = next(name for name in archive.namelist() if name.rsplit("/", 1)[-1] == target.name)
        target.parent.mkdir(parents=True, exist_ok=True)
        partial_file = target.with_name(f"{target.name}.{os.getpid()}.part")
        partial_file.write_bytes(archive.read(member))
    os.replace(partial_file, target)


def ensure_gecko():
    target = BIN_DIR / "geckodriver.exe"
    if not target.is_file():
        with urllib.request.urlopen(f"{GECKO}/latest", timeout=120) as response:
            tag = response.url.rstrip("/").rsplit("/", 1)[-1]
        unzip_to(target, fetch(f"{GECKO}/download/{tag}/geckodriver-{tag}-win64.zip"))
    output = subprocess.run([str(target), "--version"], capture_output=True, text=True, timeout=30).stdout
    return target, (output.splitlines() or ["geckodriver"])[0]


def ensure_driver(browser):
    return ensure_gecko() if browser == "firefox" else ensure_chromedriver()


def write_prefs(profile, browser):
    if browser == "firefox":
        write_firefox_prefs(profile)
    else:
        write_chrome_prefs(profile)


def write_firefox_prefs(profile):
    downloads = downloads_dir(profile)
    profile.mkdir(parents=True, exist_ok=True)
    downloads.mkdir(parents=True, exist_ok=True)
    prefs = {"marionette.port": 0, "browser.shell.checkDefaultBrowser": False, "browser.aboutwelcome.enabled": False,
             "browser.startup.homepage_override.mstone": "ignore", "startup.homepage_welcome_url": "about:blank",
             "datareporting.policy.dataSubmissionPolicyBypassNotification": True,
             "toolkit.telemetry.reportingpolicy.firstRun": False, "browser.sessionstore.resume_from_crash": False,
             "browser.translations.automaticallyPopup": False, "permissions.default.geo": 2,
             "permissions.default.desktop-notification": 2, "permissions.default.camera": 2,
             "permissions.default.microphone": 2, "network.cookie.cookieBehavior": 1,
             "privacy.donottrackheader.enabled": True, "browser.download.folderList": 2,
             "browser.download.useDownloadDir": True, "browser.download.dir": str(downloads),
             "browser.download.always_ask_before_handling_new_types": False}
    lines = [f"user_pref({json.dumps(name)}, {json.dumps(value)});" for name, value in prefs.items()]
    (profile / "user.js").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_chrome_prefs(profile):
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
