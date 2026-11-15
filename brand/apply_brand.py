#!/usr/bin/env python3
"""Apply FrameWorX Takeoff branding to a checkout of Open PDF Studio.

Usage: apply_brand.py <upstream checkout> <brand folder>

Changes the visible app name, the window title, the bundle identifier, where
the app looks for updates, and the tool set offered on first run. Icons are
regenerated separately by `tauri icon`. The upstream licence files are left in
place.
"""
import json
import pathlib
import shutil
import sys

OLD = "Open PDF Studio"
NEW = "FrameWorX Takeoff"
IDENTIFIER = "au.com.steelworxgroup.frameworxtakeoff"
# The branded build must not install the upstream project's releases over
# itself, so it looks for updates in the SteelworX repository instead.
UPDATE_URL = "https://github.com/SteelworXGroup/frameworx-takeoff/releases/latest/download/latest.json"


def must_replace(path, old, new, count=None):
    text = path.read_text(encoding="utf-8")
    found = text.count(old)
    if found == 0 or (count is not None and found != count):
        sys.exit(f"brand: expected {count or 'some'} x {old!r} in {path}, found {found}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def main():
    src = pathlib.Path(sys.argv[1]).resolve()
    brand = pathlib.Path(sys.argv[2]).resolve()
    app = src / "open-pdf-studio"

    # 1. Tauri configuration: name, identifier, window title, update source.
    conf_path = app / "src-tauri" / "tauri.conf.json"
    conf = json.loads(conf_path.read_text(encoding="utf-8"))
    conf["productName"] = NEW
    conf["identifier"] = IDENTIFIER
    for window in conf["app"]["windows"]:
        window["title"] = NEW
    # Update packages need the upstream project's private signing key, which
    # this build does not have, so none are produced.
    conf["bundle"]["createUpdaterArtifacts"] = False
    conf["bundle"]["publisher"] = "SteelworX Group Pty Ltd"
    conf["plugins"]["updater"]["endpoints"] = [UPDATE_URL]
    conf_path.write_text(json.dumps(conf, indent=2) + "\n", encoding="utf-8")

    # 2. Visible name in the page title, the window title and the translations.
    must_replace(app / "index.html", f"<title>{OLD}</title>", f"<title>{NEW}</title>", 1)
    must_replace(
        app / "js" / "ui" / "chrome" / "tabs.js",
        "`" + OLD + " v${appVersion()}`",
        "`" + NEW + " v${appVersion()}`",
        1,
    )
    renamed = 0
    for path in (app / "js" / "i18n" / "locales").rglob("*.json"):
        text = path.read_text(encoding="utf-8")
        if OLD in text:
            path.write_text(text.replace(OLD, NEW), encoding="utf-8")
            renamed += 1
    if renamed == 0:
        sys.exit("brand: no translation files mention the app name")

    # 3. In-app logo (About dialog).
    shutil.copyfile(brand / "icon.png", app / "public" / "icon.png")

    # 4. Standard tool sets: every file in brand/toolsets, in file-name order.
    #    They are offered on first run, and any that is missing from a stored
    #    list is added back when the app starts, so new standard sets reach
    #    people who already have the app.
    sets = []
    for path in sorted((brand / "toolsets").glob("*.opdstools")):
        tool_set = json.loads(path.read_text(encoding="utf-8"))["toolSet"]
        set_id = "fwx-" + path.stem.split("-", 1)[1]
        sets.append({"id": set_id, "name": tool_set["name"], "items": tool_set["items"]})
    if not sets:
        sys.exit("brand: no tool sets found in brand/toolsets")
    seed = {"version": 1, "sets": sets}
    tools_js = app / "js" / "annotations" / "tool-sets.js"
    must_replace(
        tools_js,
        "  if (text == null || !String(text).trim()) return { ok: true, raw: null };",
        "  if (text == null || !String(text).trim()) return { ok: true, raw: FRAMEWORX_DEFAULT_CATALOG };",
        1,
    )
    must_replace(
        tools_js,
        "  return { ok: true, raw: data };",
        "  return { ok: true, raw: withFrameworxDefaults(data) };",
        1,
    )
    with tools_js.open("a", encoding="utf-8") as fh:
        fh.write("\n// FrameWorX Takeoff: standard tool sets.\n")
        fh.write("const FRAMEWORX_DEFAULT_CATALOG = " + json.dumps(seed) + ";\n")
        fh.write(
            "function withFrameworxDefaults(data) {\n"
            "  const have = new Set(data.sets.map((s) => s && s.id));\n"
            "  const missing = FRAMEWORX_DEFAULT_CATALOG.sets.filter((s) => !have.has(s.id));\n"
            "  return missing.length ? { ...data, sets: [...data.sets, ...missing] } : data;\n"
            "}\n"
        )

    # 5. One schedule that exports everything the Estimator reads, first in
    #    the list so it is the default choice.
    templates_js = app / "js" / "quantities" / "schedule-templates.js"
    must_replace(
        templates_js,
        "export const STANDARD_SCHEDULE_TEMPLATES = [\n",
        "export const STANDARD_SCHEDULE_TEMPLATES = [\n"
        "  {\n"
        "    id: 'frameworx',\n"
        "    nameKey: 'schedules.tpl.frameworx',\n"
        "    config: {\n"
        "      categories: ['area', 'line-based', 'count'],\n"
        "      fields: ['label', 'length', 'area', 'count', 'countCat', 'page'],\n"
        "      sort: [{ field: 'label', dir: 'asc', group: false }],\n"
        "      itemize: true,\n"
        "    },\n"
        "  },\n",
        1,
    )
    named = 0
    for path in (app / "js" / "i18n" / "locales").glob("*/properties.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        tpl = data.get("schedules", {}).get("tpl")
        if isinstance(tpl, dict):
            tpl["frameworx"] = "FrameWorX take-off"
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            named += 1
    if named == 0:
        sys.exit("brand: could not name the FrameWorX schedule in any language")

    print(f"brand: applied {NEW} ({renamed} translation files, {len(sets)} tool sets)")


if __name__ == "__main__":
    main()
