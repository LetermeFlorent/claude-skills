from urllib.parse import urlsplit

from actions.shared import url_of
from core.binaries import chrome_version

DEFAULT_VIEWPORT_HEIGHT = 900
MOBILE_SIZE = (390, 844)
MOBILE_DPR = 3
MOBILE_AGENT = ("Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/{major}.0.0.0 Mobile Safari/537.36")
GEO_ACCURACY = 10
OFF = "off"
SET_VIEWPORT = "browsingContext.setViewport"
SET_USER_AGENT = "emulation.setUserAgentOverride"
SET_GEOLOCATION = "emulation.setGeolocationOverride"
SET_PERMISSION = "permissions.setPermission"
GEOLOCATION = "geolocation"


def viewport(page):
    width, _, height = page.value.lower().partition("x")
    size = {"width": int(width), "height": int(height) if height else DEFAULT_VIEWPORT_HEIGHT}
    page.call(SET_VIEWPORT, {"context": page.context, "viewport": size})
    print(f"viewport {size['width']} x {size['height']}")


def mobile(page):
    width, height = MOBILE_SIZE
    page.call(SET_VIEWPORT, {"context": page.context, "viewport": {"width": width, "height": height},
                             "devicePixelRatio": MOBILE_DPR})
    agent = MOBILE_AGENT.format(major=chrome_version().split(".")[0])
    page.call(SET_USER_AGENT, {"contexts": [page.context], "userAgent": agent})
    print(f"mobile mode {width}x{height}, reload the page for the user agent")


def desktop(page):
    page.call(SET_VIEWPORT, {"context": page.context, "viewport": None, "devicePixelRatio": None})
    page.call(SET_USER_AGENT, {"contexts": [page.context], "userAgent": None})
    print("desktop mode")


def geo(page):
    parts = urlsplit(url_of(page))
    origin = f"{parts.scheme}://{parts.netloc}"
    if page.value == OFF:
        page.call(SET_GEOLOCATION, {"contexts": [page.context], "coordinates": None})
        page.call(SET_PERMISSION, {"descriptor": {"name": GEOLOCATION}, "state": "denied", "origin": origin})
        print("real geolocation, denied")
        return
    latitude, longitude = (float(part) for part in page.value.split(","))
    page.call(SET_PERMISSION, {"descriptor": {"name": GEOLOCATION}, "state": "granted", "origin": origin})
    page.call(SET_GEOLOCATION, {"contexts": [page.context], "coordinates": {
        "latitude": latitude, "longitude": longitude, "accuracy": GEO_ACCURACY}})
    print(f"simulated position {latitude},{longitude} for {origin}")


def override(method, field):
    def apply(page):
        value = None if page.value == OFF else page.value
        page.call(method, {"contexts": [page.context], field: value})
        print(f"{field}: {value or 'default'}")
    return apply


ACTIONS = {"viewport": viewport, "mobile": mobile, "desktop": desktop, "geo": geo,
           "locale": override("emulation.setLocaleOverride", "locale"),
           "timezone": override("emulation.setTimezoneOverride", "timezone")}
