#!/usr/bin/env python3
"""Convert legacy YAML (title_cs/title_en/desc_cs/desc_en/tags_cs/tags_en)
to new nested format (title.cs/title.en/desc.cs/desc.en/tags.cs/tags.en).

Usage:  python3 tools/convert_yaml.py data/03_network.yaml ...
"""
import sys
from pathlib import Path
import yaml

LANGS_LEGACY = ["cs", "en"]


def convert_entry(entry: dict) -> dict:
    out = {"id": entry.get("id")}
    # title
    title = {}
    for lang in LANGS_LEGACY:
        key = f"title_{lang}"
        if key in entry:
            title[lang] = entry[key]
    if title:
        out["title"] = title
    # tags
    tags = {}
    for lang in LANGS_LEGACY:
        key = f"tags_{lang}"
        if key in entry:
            tags[lang] = entry[key]
    if tags:
        out["tags"] = tags
    # commands
    out["commands"] = []
    for c in entry.get("commands", []):
        new_c = {"cmd": c.get("cmd", "")}
        desc = {}
        for lang in LANGS_LEGACY:
            key = f"desc_{lang}"
            if key in c:
                desc[lang] = c[key]
        if desc:
            new_c["desc"] = desc
        out["commands"].append(new_c)
    return out


def convert_file(path: Path) -> None:
    with open(path) as f:
        data = yaml.safe_load(f) or []
    # Skip if already converted
    if data and isinstance(data[0].get("title"), dict):
        print(f"  (already new format: {path.name})")
        return
    converted = [convert_entry(e) for e in data]
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            converted,
            f,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
            width=120,
        )
    print(f"  ✓ {path.name}")


if __name__ == "__main__":
    paths = [Path(p) for p in sys.argv[1:]]
    if not paths:
        paths = sorted(Path("data").glob("*.yaml"))
    for p in paths:
        convert_file(p)
