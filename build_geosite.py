#!/usr/bin/env python3
"""Собирает единый geosite.dat: база RoscomVPN + категории из runetfreedom.

Happ принимает только ОДИН Geositeurl, поэтому обе базы надо слить в один файл.

Использование:
    python3 build_geosite.py [-o dist/geosite.dat]
"""
import argparse
import hashlib
import json
import pathlib
import urllib.request

from geosite_lib import count_domains, split_entries

BASE_URL = "https://github.com/hydraponique/roscomvpn-geosite/releases/latest/download/geosite.dat"
RF_API = "https://api.github.com/repos/runetfreedom/russia-blocked-geosite/releases/latest"
RF_ASSET = "geosite-ru-only.dat"

# Что доливаем из runetfreedom. Имена совпадают с тем, что пишем в правилах Happ.
EXTRA = ["CATEGORY-ADS-ALL", "RU-AVAILABLE-ONLY-INSIDE"]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "happ-routing-builder"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default="dist/geosite.dat")
    args = ap.parse_args()

    print("качаю базовый geosite (RoscomVPN)…")
    base = fetch(BASE_URL)

    release = json.loads(fetch(RF_API))
    asset = next(a for a in release["assets"] if a["name"] == RF_ASSET)
    print(f"качаю {RF_ASSET} из релиза runetfreedom {release['tag_name']} "
          f"({asset['size'] / 1e6:.1f} МБ)…")
    extra_raw = fetch(asset["browser_download_url"])

    base_entries = split_entries(base)
    extra_entries = {name: raw for name, raw in split_entries(extra_raw)}

    have = {name for name, _ in base_entries}
    merged = list(base_entries)
    for name in EXTRA:
        if name not in extra_entries:
            raise SystemExit(f"категории {name} нет в {RF_ASSET}")
        if name in have:
            raise SystemExit(f"конфликт имён: {name} уже есть в базовом файле")
        merged.append((name, extra_entries[name]))

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    blob = b"".join(raw for _, raw in merged)
    out.write_bytes(blob)
    digest = hashlib.sha256(blob).hexdigest()
    out.with_suffix(".dat.sha256").write_text(f"{digest}  geosite.dat\n")

    print(f"\n{out} — {len(blob) / 1e6:.2f} МБ, {len(merged)} категорий")
    for name, raw in merged:
        mark = "+" if name in EXTRA else " "
        print(f" {mark} geosite:{name.lower()} ({count_domains(raw)})")
    print(f"\nsha256: {digest}")
    print("Не забудьте обновить LastUpdated в routing.json после публикации файла.")


if __name__ == "__main__":
    main()
