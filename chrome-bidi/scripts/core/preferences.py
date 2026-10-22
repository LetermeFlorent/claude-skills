import json

from core.common import ENCODING, downloads_dir

REFUSED = 2
PREFS = {("download", "prompt_for_download"): False, ("download", "directory_upgrade"): True,
         ("profile", "default_content_setting_values", "geolocation"): REFUSED,
         ("profile", "default_content_setting_values", "notifications"): REFUSED,
         ("profile", "default_content_setting_values", "media_stream_camera"): REFUSED,
         ("profile", "default_content_setting_values", "media_stream_mic"): REFUSED,
         ("profile", "cookie_controls_mode"): 1, ("enable_do_not_track",): True}


def write_prefs(profile):
    downloads = downloads_dir(profile)
    file = profile / "Default" / "Preferences"
    file.parent.mkdir(parents=True, exist_ok=True)
    downloads.mkdir(parents=True, exist_ok=True)
    prefs = json.loads(file.read_text(encoding=ENCODING)) if file.is_file() else {}
    for path, value in {**PREFS, ("download", "default_directory"): str(downloads)}.items():
        node = prefs
        for key in path[:-1]:
            node = node.setdefault(key, {})
        node[path[-1]] = value
    file.write_text(json.dumps(prefs), encoding=ENCODING)
    return downloads
