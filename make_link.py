#!/usr/bin/env python3
"""Собирает ссылку и JSON-профиль маршрутизации из routing.json.

    python3 make_link.py --client happ --geosite-url https://…/geosite.dat --touch
    python3 make_link.py --client incy --json-out dist/incy-profile.json --touch

Базовый routing.json написан в формате Happ. Для INCY профиль преобразуется:
RouteOrder в INCY не документирован (порядок правил фиксирован в клиенте), а обрезка
геофайлов называется useChunkFiles и имеет тип boolean, а не строку.

--touch обязателен, когда изменилось содержимое geosite.dat: клиент перекачивает
геофайлы только при возросшем LastUpdated.
"""
import argparse
import base64
import json
import pathlib
import time

SCHEMES = {"happ": "happ", "incy": "incy"}

ap = argparse.ArgumentParser()
ap.add_argument("-f", "--file", default="routing.json")
ap.add_argument("-c", "--client", choices=SCHEMES, default="happ")
ap.add_argument("--geosite-url")
ap.add_argument("--geoip-url")
ap.add_argument("--touch", action="store_true", help="LastUpdated = текущий unix time")
ap.add_argument("--add", action="store_true", help="routing/add вместо routing/onadd")
ap.add_argument("--json-out", help="куда записать готовый профиль (для autorouting в INCY)")
ap.add_argument("--save", action="store_true", help="записать изменения обратно в routing.json")
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

if args.save:
    path.write_text(json.dumps(cfg, ensure_ascii=False, indent=4) + "\n")

if args.client == "incy":
    cfg.pop("RouteOrder", None)
    cfg.pop("UseChunkFiles", None)
    cfg["useChunkFiles"] = True

if args.json_out:
    out = pathlib.Path(args.json_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(cfg, ensure_ascii=False, indent=4) + "\n")

payload = base64.b64encode(json.dumps(cfg, ensure_ascii=False, separators=(",", ":")).encode()).decode()
verb = "add" if args.add else "onadd"
link = f"{SCHEMES[args.client]}://routing/{verb}/{payload}"
print(link)
print(f"\n({len(link)} символов, LastUpdated={cfg['LastUpdated']})")
