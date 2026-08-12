"""Минимальный парсер/сборщик geosite.dat (protobuf GeoSiteList).

Формат:
    GeoSiteList { repeated GeoSite entry = 1; }
    GeoSite     { string country_code = 1; repeated Domain domain = 2; }

Нам не нужен protobuf-рантайм: entry на верхнем уровне лежат подряд,
поэтому категории можно резать и склеивать как сырые байты.
"""


def read_varint(buf, i):
    shift = 0
    result = 0
    while True:
        b = buf[i]
        i += 1
        result |= (b & 0x7F) << shift
        shift += 7
        if not b & 0x80:
            return result, i


def write_varint(value):
    out = bytearray()
    while True:
        b = value & 0x7F
        value >>= 7
        if value:
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)


def split_entries(raw):
    """[(имя категории, сырые байты entry вместе с тегом и длиной)]"""
    entries = []
    i = 0
    while i < len(raw):
        start = i
        tag, i = read_varint(raw, i)
        if tag != 0x0A:
            raise ValueError(f"неожиданный тег {tag:#x} на позиции {start}")
        length, i = read_varint(raw, i)
        body = raw[i:i + length]
        i += length
        j = 0
        _, j = read_varint(body, j)          # тег country_code
        name_len, j = read_varint(body, j)
        name = body[j:j + name_len].decode()
        entries.append((name.upper(), raw[start:i]))
    return entries


def count_domains(entry_raw):
    _, i = read_varint(entry_raw, 0)
    length, i = read_varint(entry_raw, i)
    body = entry_raw[i:i + length]
    j = 0
    _, j = read_varint(body, j)
    name_len, j = read_varint(body, j)
    j += name_len
    n = 0
    while j < len(body):
        _, j = read_varint(body, j)
        dlen, j = read_varint(body, j)
        j += dlen
        n += 1
    return n


def make_entry(name, domains, dtype=2):
    """Собрать категорию из списка доменов. dtype: 0 plain, 1 regex, 2 domain, 3 full."""
    body = bytearray()
    encoded = name.upper().encode()
    body += b"\x0a" + write_varint(len(encoded)) + encoded
    for d in domains:
        dv = d.encode()
        dom = b"\x08" + write_varint(dtype) + b"\x12" + write_varint(len(dv)) + dv
        body += b"\x12" + write_varint(len(dom)) + dom
    return b"\x0a" + write_varint(len(body)) + bytes(body)


def domains_of(entry_raw):
    types = {0: "plain", 1: "regex", 2: "domain", 3: "full"}
    _, i = read_varint(entry_raw, 0)
    length, i = read_varint(entry_raw, i)
    body = entry_raw[i:i + length]
    j = 0
    _, j = read_varint(body, j)
    name_len, j = read_varint(body, j)
    j += name_len
    out = []
    while j < len(body):
        _, j = read_varint(body, j)
        dlen, j = read_varint(body, j)
        d = body[j:j + dlen]
        j += dlen
        k = 0
        _, k = read_varint(d, k)
        dtype, k = read_varint(d, k)
        _, k = read_varint(d, k)
        vlen, k = read_varint(d, k)
        out.append((types.get(dtype, dtype), d[k:k + vlen].decode()))
    return out
