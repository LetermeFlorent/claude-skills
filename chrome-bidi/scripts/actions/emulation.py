import sys
from urllib.parse import urlsplit

sys.dont_write_bytecode = True

from core.driver import chrome_version
from actions.page import url_of


MOBILE_AGENT = ("Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/{major}.0.0.0 Mobile Safari/537.36")


def viewport(page):
    width, _, height = page.value.lower().partition("x")
    size = {"width": int(width), "height": int(height) if height else 900}
    page.call("browsingContext.setViewport", {"context": page.context, "viewport": size})
    print(f"viewport {size['width']} x {size['height']}")


def mobile(page):
    page.call("browsingContext.setViewport", {"context": page.context, "viewport": {"width": 390, "height": 844},
                                              "devicePixelRatio": 3})
    agent = MOBILE_AGENT.format(major=chrome_version().split(".")[0])
    page.call("emulation.setUserAgentOverride", {"contexts": [page.context], "userAgent": agent})
    print("mobile mode 390x844, reload the page for the user agent")


def desktop(page):
    page.call("browsingContext.setViewport", {"context": page.context, "viewport": None, "devicePixelRatio": None})
    page.call("emulation.setUserAgentOverride", {"contexts": [page.context], "userAgent": None})
    print("desktop mode")


def geo(page):
    parts = urlsplit(url_of(page))
    origin = f"{parts.scheme}://{parts.netloc}"
    permission = {"descriptor": {"name": "geolocation"}, "origin": origin}
    if page.value == "off":
        page.call("emulation.setGeolocationOverride", {"contexts": [page.context], "coordinates": None})
        page.call("permissions.setPermission", {**permission, "state": "denied"})
        print("real geolocation, denied")
        return
    latitude, longitude = (float(part) for part in page.value.split(","))
    page.call("permissions.setPermission", {**permission, "state": "granted"})
    page.call("emulation.setGeolocationOverride", {"contexts": [page.context], "coordinates": {
        "latitude": latitude, "longitude": longitude, "accuracy": 10}})
    print(f"simulated position {latitude},{longitude} for {origin}")


def override(method, field):
    def apply(page):
        value = None if page.value == "off" else page.value
        page.call(method, {"contexts": [page.context], field: value})
        print(f"{field}: {value or 'default'}")
    return apply


ACTIONS = {"viewport": viewport, "mobile": mobile, "desktop": desktop, "geo": geo,
           "locale": override("emulation.setLocaleOverride", "locale"),
           "timezone": override("emulation.setTimezoneOverride", "timezone")}
