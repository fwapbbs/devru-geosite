# devru-geosite

Файл `geosite.dat` со списками доменов для маршрутизации трафика в Xray-совместимых клиентах
(Happ, v2rayNG, v2rayN и другие).

Пересобирается автоматически каждые 6 часов.

## Что внутри

25 категорий: базовый набор для российских пользователей плюс два больших списка.

| Категория | Доменов | Назначение |
|---|---|---|
| `geosite:category-ads-all` | ~149 000 | реклама и трекеры — блокировка |
| `geosite:ru-available-only-inside` | ~170 | сайты, доступные только с российских IP — прямое подключение |
| `geosite:whitelist`, `geosite:category-ru` | | российские ресурсы — прямое подключение |
| `geosite:category-geoblock-ru` | | ресурсы, закрытые для российских IP — через прокси |
| `geosite:youtube`, `geosite:telegram`, `geosite:github`, `geosite:google-play` | | через прокси |
| `geosite:steam`, `geosite:apple`, `geosite:microsoft`, `geosite:epicgames`, `geosite:riot`, `geosite:origin`, `geosite:escapefromtarkov`, `geosite:faceit`, `geosite:twitch`, `geosite:pinterest` | | прямое подключение |
| `geosite:win-spy`, `geosite:torrent`, `geosite:category-ads`, `geosite:twitch-ads` | | телеметрия, торренты, реклама |

Полный список категорий с количеством доменов печатается при сборке.

## Скачать

Свежая версия — во вкладке [Releases](../../releases). Прямые ссылки:

```
https://cdn.jsdelivr.net/gh/fwapbbs/devru-geosite@<тег>/release/geosite.dat
https://github.com/fwapbbs/devru-geosite/releases/latest/download/geosite.dat
```

Рядом лежит `geosite.dat.sha256` для проверки целостности.

## Как подключить

**Happ.** В релизе есть `link.txt` — готовая ссылка `happ://routing/onadd/…`, которая добавляет
профиль маршрутизации `DevRu` вместе с этим файлом. Ссылку достаточно открыть на устройстве.

**Xray / v2ray.** Указать файл как `geosite.dat` в каталоге ресурсов ядра и ссылаться на
категории в правилах маршрутизации:

```json
{ "type": "field", "domain": ["geosite:category-ads-all"], "outboundTag": "block" },
{ "type": "field", "domain": ["geosite:ru-available-only-inside"], "outboundTag": "direct" }
```

## Собрать самому

```bash
python3 build_geosite.py -o dist/geosite.dat
```

Зависимостей нет, нужен только Python 3.

## Источники

* [hydraponique/roscomvpn-geosite](https://github.com/hydraponique/roscomvpn-geosite) — базовый набор категорий
* [runetfreedom/russia-blocked-geosite](https://github.com/runetfreedom/russia-blocked-geosite) — реклама и домены, доступные только внутри РФ
