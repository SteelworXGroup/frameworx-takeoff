# FrameWorX Takeoff

Internal PDF take-off app for FrameWorX estimating. It is a branded build of
[Open PDF Studio](https://github.com/OpenAEC-Foundation/open-pdf-studio) by the
OpenAEC Foundation, used with the FrameWorX Estimator workbook.

This repository does not hold a copy of the app's source code. It holds the
FrameWorX branding and a build recipe that applies it to a pinned release of
Open PDF Studio.

## What is in here

| Path | Purpose |
|---|---|
| `UPSTREAM_VERSION` | The Open PDF Studio release the build is based on |
| `brand/icon.png` | FrameWorX icon, used for the app and installer icons |
| `brand/frameworx-takeoff.opdstools` | The take-off tool set the app starts with |
| `brand/apply_brand.py` | Renames the app and applies the items above |
| `.github/workflows/build.yml` | Builds the Mac and Windows installers |

## Building

Run the **Build FrameWorX Takeoff** workflow from the Actions tab, or push a
change to `brand/` or `UPSTREAM_VERSION`. The Mac disk image and the Windows
installer are attached to the finished run as artifacts.

To move to a newer Open PDF Studio release, change the tag in
`UPSTREAM_VERSION` and run the build again.

## Known limits

- The installers are not signed with an Apple or Microsoft certificate, so
  macOS and Windows warn on first launch.
- The app does not update itself. A new version means a new build.

## Licence

Open PDF Studio is licensed under LGPL-3.0, and its licence files ship inside
the built app unchanged. The branding files in this repository belong to
SteelworX Group Pty Ltd.
