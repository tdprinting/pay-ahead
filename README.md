# Pay Ahead Demo

An interactive, phone-style walkthrough that shows pharmacy patients how to pay for their prescriptions ahead of time and pick them up with a QR code. It runs in about 30 seconds, works in any browser, and is sized for iPhone and iPad.

The brand ("Stockyard Pharmacy"), patients, prescriptions and prices are all made up for demonstration.

## Use it on iPhone / iPad

Open **https://tdprinting.github.io/pay-ahead/** in **Safari**, tap **Share → Add to Home Screen**, and it runs
full screen like an app (and keeps working without a signal after the first open). Every push to `main`
rebuilds it automatically and publishes a new [Release](https://github.com/tdprinting/pay-ahead/releases/latest)
with a one-file copy you can AirDrop.

## What it shows

1. A "ready for pickup" text arrives. The patient taps the link.
2. They confirm their name and date of birth, pick prescriptions, and pay with a card.
3. A second text brings a pickup QR code.
4. At the store they go to the green Pay Ahead line (or the Counseling Window).
5. A 3D scene shows the code being scanned and the bag handed over at the counter.
6. A short summary of the benefits closes it out.

Press **Play** to watch it, or tap along on the phone. The slider sets the length (15 to 60 seconds).

## Files

| File | What it is |
| --- | --- |
| `pay-ahead-demo.html` | The main source file. Edit this one. |
| `app/` | The iPhone web app (icon, offline support). Published to GitHub Pages automatically. |
| `.github/workflows/iphone.yml` | The automatic build: publishes the site and creates a Release on every push. |
| `vendor/three.min.js` | Local copy of the three.js 3D library (r128, MIT license) so the 3D scene works offline. |
| `Stockyard Pay Ahead Demo (standalone).html` | One-file copy to email or AirDrop. |
| `build_app.py` | Run `python build_app.py` after editing to refresh `app/` and the standalone copy. |
| `HOW TO PUT IT ON AN IPHONE.txt` | Step-by-step for adding it to an iPhone home screen. |

Names, prescriptions, prices and sample patients are under **Demo settings** near the top of the script in `pay-ahead-demo.html`.
