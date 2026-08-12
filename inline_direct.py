#!/usr/bin/env python3
"""Вариант без своего geosite.dat: вписать домены категории прямо в правила.

Годится для маленьких списков (ru-available-only-inside — 167 доменов),
но не для рекламы: 148 тыс. доменов в ссылку не влезут.

    python3 inline_direct.py                        # обновить routing-inline.json
    python3 inline_direct.py --only-new             # только домены, которых нет в whitelist
"""
import argparse
import json
import pathlib
import urllib.request

from geosite_lib import domains_of, split_entries

RF_API = "https://api.github.com/repos/runetfreedom/russia-blocked-geosite/releases/latest"
BASE_URL = "https://github.com/hydraponique/roscomvpn-geosite/releases/latest/download/geosite.dat"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "happ-routing-builder"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


ap = argparse.ArgumentParser()
ap.add_argument("--only-new", action="store_true",
                help="выкинуть домены, которые уже покрыты whitelist/category-ru базового geosite")
ap.add_argument("-o", "--out", default="routing-inline.json")
args = ap.parse_args()

release = json.loads(fetch(RF_API))
asset = next(a for a in release["assets"] if a["name"] == "geosite-ru-only.dat")
rf = dict(split_entries(fetch(asset["browser_download_url"])))
inside = [v for _, v in domains_of(rf["RU-AVAILABLE-ONLY-INSIDE"])]

if args.only_new:
    base = dict(split_entries(fetch(BASE_URL)))
    covered = set()
    for cat in ("WHITELIST", "CATEGORY-RU", "CATEGORY-GEOBLOCK-RU", "PRIVATE"):
        covered |= {v for _, v in domains_of(base[cat])}
    inside = [d for d in inside if d not in covered]

cfg = json.loads(pathlib.Path("routing.json").read_text())
cfg["Geositeurl"] = "https://cdn.jsdelivr.net/gh/hydraponique/roscomvpn-geosite@202604152235/release/geosite.dat"
cfg["DirectSites"] = [s for s in cfg["DirectSites"] if s != "geosite:ru-available-only-inside"]
cfg["DirectSites"] += [f"domain:{d}" for d in inside]
cfg["BlockSites"] = [s for s in cfg["BlockSites"] if s != "geosite:category-ads-all"]

pathlib.Path(args.out).write_text(json.dumps(cfg, ensure_ascii=False, indent=4) + "\n")
print(f"{args.out}: +{len(inside)} доменов в DirectSites (релиз {release['tag_name']})")
print("дальше: python3 make_link.py -f", args.out, "--touch")
