# happ-routing

Добавление списков [runetfreedom/russia-blocked-geosite](https://github.com/runetfreedom/russia-blocked-geosite)
(реклама + домены, доступные только изнутри РФ) в routing-профиль Happ.

## Почему нельзя просто дать ссылку на .txt

В профиле Happ ровно одно поле `Geositeurl` и одно `Geoipurl` — второй источник не подключить,
а `.txt` из релизов runetfreedom Happ не понимает: нужен бинарный `geosite.dat` (protobuf).
Вписать домены прямо в `BlockSites` тоже нельзя: в `category-ads-all` 148 872 домена.

Решение: собрать **один** `geosite.dat` = база RoscomVPN + нужные категории runetfreedom
и положить его на свой хостинг.

## Как пользоваться

```bash
python3 build_geosite.py                  # dist/geosite.dat (~3.9 МБ, 25 категорий)
# залить dist/geosite.dat в свой репозиторий/релиз или на свой сервер
python3 make_link.py --geosite-url https://<адрес>/geosite.dat --touch
```

Ссылка печатается в stdout; отдавать её пользователям через тело подписки или HTTP-заголовок
`routing:` (см. `docs` Happ). `--touch` ставит `LastUpdated` = сейчас — **без этого Happ
не перекачает геофайлы**, у него на устройстве останется старый.

Что появляется в правилах:

| правило | где | доменов |
|---|---|---|
| `geosite:category-ads-all` | `BlockSites` | 148 872 |
| `geosite:ru-available-only-inside` | `DirectSites` | 167 |

## Вариант без своего хостинга

Только для «доступных изнутри РФ» — их мало, они влезают в саму ссылку:

```bash
python3 inline_direct.py --only-new       # routing-inline.json, +30 доменов в DirectSites
python3 make_link.py -f routing-inline.json --touch
```

Реклама этим способом не добавляется.

## Грабли

* **Имя профиля.** При импорте профиль с совпадающим `Name` перезаписывается. Текущее имя
  `RoscomVPN` — чужое; для своего сервиса лучше своё, иначе затрёте пользователю чужой профиль
  (и наоборот).
* **Лимит загрузки 3 минуты.** Если геофайлы не скачались за 3 минуты, Happ останавливает
  процесс и помечает профиль красным. Поэтому берётся `geosite-ru-only.dat` (5,4 МБ), а не
  полный `geosite.dat` runetfreedom (73 МБ).
* **`UseChunkFiles: true`** вырезает из .dat только используемые категории — нужно для iOS
  (лимит 50 МБ памяти у расширения). Оставлять включённым.
* **`RouteOrder: block-proxy-direct`** — блокировка проверяется первой, поэтому домен из
  `category-ads-all` заблокируется, даже если он есть в whitelist. Пересечения с текущим
  профилем: `webvisor.com`, `yandexmetrica.com`, `yandexadexchange.net`, `vk-analytics.ru`
  (whitelist), `api-adservices.apple.com`, `iadsdk.apple.com` (apple). Если что-то из этого
  ломает сайты — исключений в Happ нет, придётся вырезать домены из категории при сборке.
* **Обновления.** runetfreedom пересобирает списки каждые 6 часов. Свой файл надо пересобирать
  и каждый раз поднимать `LastUpdated` — для этого `.github/workflows/build-geosite.yml`.
