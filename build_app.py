"""Rebuild the hostable app folder and the single-file standalone copy from pay-ahead-demo.html.

Run:  python build_app.py
"""
import base64
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "pay-ahead-demo.html")
APP = os.path.join(HERE, "app")

src = open(SRC, encoding="utf-8").read()
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


def page(icons):
    return BASE_HEAD.format(icons=icons) + head_part + "</head>\n<body>\n" + body_part + "\n</body>\n</html>\n"


# 1) Hostable app folder (upload the whole folder to any static host)
app_icons = """<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="192x192" href="icon-192.png">
<link rel="icon" type="image/svg+xml" href="icon.svg">
<link rel="manifest" href="manifest.webmanifest">"""
open(os.path.join(APP, "index.html"), "w", encoding="utf-8").write(page(app_icons))
manifest = {
    "name": "Stockyard Pay Ahead Demo",
    "short_name": "Pay Ahead",
    "start_url": "./",
    "scope": "./",
    "display": "standalone",
    "background_color": "#eceef1",
    "theme_color": "#c4302b",
    "icons": [
        {"src": "apple-touch-icon.png", "sizes": "180x180", "type": "image/png"},
        {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "icon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any"},
    ],
}
open(os.path.join(APP, "manifest.webmanifest"), "w", encoding="utf-8").write(json.dumps(manifest, indent=2))

# 2) Single-file copy with the icon embedded (handy for AirDrop / email / desktop browsers)
png = base64.b64encode(open(os.path.join(APP, "apple-touch-icon.png"), "rb").read()).decode()
one_icons = f"""<link rel="apple-touch-icon" href="data:image/png;base64,{png}">
<link rel="icon" type="image/png" href="data:image/png;base64,{png}">"""
open(os.path.join(HERE, "Stockyard Pay Ahead Demo (standalone).html"), "w", encoding="utf-8").write(page(one_icons))
print("Built app/index.html, app/manifest.webmanifest and the standalone file.")
