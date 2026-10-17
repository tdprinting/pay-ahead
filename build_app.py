"""Rebuild the iPhone web app (app/) and the single-file standalone copy from pay-ahead-demo.html.

Run:  python build_app.py              (local build, version "dev")
      python build_app.py 1.0.20261017.5   (what GitHub Actions runs)
"""
import base64
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "pay-ahead-demo.html")
APP = os.path.join(HERE, "app")
THREE_CDN = '<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>'
THREE_LOCAL = os.path.join(HERE, "vendor", "three.min.js")

version = sys.argv[1] if len(sys.argv) > 1 else "dev"

src = open(SRC, encoding="utf-8").read()
assert THREE_CDN in src, "three.js script tag not found in pay-ahead-demo.html"
src = src.replace('<span class="app-version"></span>', f'<span class="app-version"> Version {version}.</span>')
split = src.index('<div class="wrap">')
head_part, body_part = src[:split], src[split:]

BASE_HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Pay Ahead">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="theme-color" content="#eceef1" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0f1319" media="(prefers-color-scheme: dark)">
<meta name="description" content="Interactive Pay Ahead walkthrough for pharmacy pickup.">
{icons}
<style>:root{{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}body{{margin:0}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
"""


def page(icons, three_tag, extra_body=""):
    body = body_part.replace(THREE_CDN, three_tag)
    return BASE_HEAD.format(icons=icons) + head_part + "</head>\n<body>\n" + body + extra_body + "\n</body>\n</html>\n"


# ---------- 1) iPhone web app: app/ (published to GitHub Pages) ----------
os.makedirs(os.path.join(APP, "vendor"), exist_ok=True)
shutil.copyfile(THREE_LOCAL, os.path.join(APP, "vendor", "three.min.js"))
app_icons = """<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="192x192" href="icon-192.png">
<link rel="icon" type="image/svg+xml" href="icon.svg">
<link rel="manifest" href="manifest.webmanifest">"""
sw_register = """
<script>
  // Offline support: the service worker keeps a copy so the app opens with no signal.
  if ("serviceWorker" in navigator && location.protocol.startsWith("http")) {
    window.addEventListener("load", () => navigator.serviceWorker.register("sw.js").catch(() => {}));
  }
</script>"""
open(os.path.join(APP, "index.html"), "w", encoding="utf-8").write(page(app_icons, '<script src="vendor/three.min.js"></script>', sw_register))

manifest = {
    "name": "Pay Ahead Demo",
    "short_name": "Pay Ahead",
    "id": "./",
    "start_url": "./",
    "scope": "./",
    "display": "standalone",
    "orientation": "portrait",
    "background_color": "#0d1117",
    "theme_color": "#c4302b",
    "icons": [
        {"src": "apple-touch-icon.png", "sizes": "180x180", "type": "image/png"},
        {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "icon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any"},
    ],
}
open(os.path.join(APP, "manifest.webmanifest"), "w", encoding="utf-8").write(json.dumps(manifest, indent=2))

SW = """// Pay Ahead service worker: version __VERSION__
// The page itself is fetched fresh when online (so updates show up right away) and from the cache when offline.
const CACHE = "pay-ahead-__VERSION__";
const CORE = ["./", "index.html", "manifest.webmanifest", "apple-touch-icon.png", "icon-192.png", "icon.svg", "vendor/three.min.js"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k.startsWith("pay-ahead-") && k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);

  if (req.mode === "navigate") {
    e.respondWith(
      fetch(req)
        .then((res) => { const copy = res.clone(); caches.open(CACHE).then((c) => c.put("index.html", copy)); return res; })
        .catch(() => caches.match("index.html"))
    );
    return;
  }
  if (url.origin === self.location.origin) {
    e.respondWith(caches.match(req).then((hit) => hit || fetch(req).then((res) => {
      const copy = res.clone(); caches.open(CACHE).then((c) => c.put(req, copy)); return res;
    })));
    return;
  }
  if (url.hostname === "fonts.googleapis.com" || url.hostname === "fonts.gstatic.com") {
    e.respondWith(caches.open(CACHE).then((c) => c.match(req).then((hit) => {
      const net = fetch(req).then((res) => { c.put(req, res.clone()); return res; }).catch(() => hit);
      return hit || net;
    })));
  }
});
"""
open(os.path.join(APP, "sw.js"), "w", encoding="utf-8").write(SW.replace("__VERSION__", version))

# ---------- 2) Single-file copy: icon and 3D library built in (email / AirDrop / offline) ----------
png = base64.b64encode(open(os.path.join(APP, "apple-touch-icon.png"), "rb").read()).decode()
one_icons = f"""<link rel="apple-touch-icon" href="data:image/png;base64,{png}">
<link rel="icon" type="image/png" href="data:image/png;base64,{png}">"""
three_js = open(THREE_LOCAL, encoding="utf-8").read()
assert "</script" not in three_js
open(os.path.join(HERE, "Stockyard Pay Ahead Demo (standalone).html"), "w", encoding="utf-8").write(page(one_icons, "<script>\n" + three_js + "\n</script>"))

print(f"Built version {version}: app/ (index.html, sw.js, manifest, vendor/three.min.js) and the standalone file.")
