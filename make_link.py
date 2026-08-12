#!/usr/bin/env python3
"""Собирает ссылку happ://routing/onadd/<base64> из routing.json.

    python3 make_link.py                       # взять LastUpdated из файла
    python3 make_link.py --touch               # проставить LastUpdated = сейчас
    python3 make_link.py --geosite-url https://…/geosite.dat --touch

--touch обязателен, когда обновилось содержимое geosite.dat: Happ перекачивает
геофайлы, только если LastUpdated в профиле новее сохранённого на устройстве.
"""
import argparse
import base64
import json
import pathlib
import time

ap = argparse.ArgumentParser()
ap.add_argument("-f", "--file", default="routing.json")
ap.add_argument("--geosite-url")
ap.add_argument("--geoip-url")
ap.add_argument("--touch", action="store_true", help="LastUpdated = текущий unix time")
ap.add_argument("--add", action="store_true", help="happ://routing/add/ вместо onadd")
args = ap.parse_args()

path = pathlib.Path(args.file)
cfg = json.loads(path.read_text())

if args.geosite_url:
    cfg["Geositeurl"] = args.geosite_url
if args.geoip_url:
    cfg["Geoipurl"] = args.geoip_url
if args.touch:
    cfg["LastUpdated"] = str(int(time.time()))

if cfg["Geositeurl"].startswith("ЗАМЕНИТЬ"):
    raise SystemExit("сначала укажите реальный Geositeurl (--geosite-url или в routing.json)")

path.write_text(json.dumps(cfg, ensure_ascii=False, indent=4) + "\n")

payload = base64.b64encode(json.dumps(cfg, ensure_ascii=False, separators=(",", ":")).encode()).decode()
verb = "add" if args.add else "onadd"
link = f"happ://routing/{verb}/{payload}"
print(link)
print(f"\n({len(link)} символов, LastUpdated={cfg['LastUpdated']})")
