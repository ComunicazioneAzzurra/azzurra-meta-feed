"""Costruisce la mappa N. Stock -> URL scheda per un sito (azzurrastore.it, brokerautomobili.com…).

Il feed DealerK non contiene l'URL reale della scheda (vdpLink = "nochannel"),
mentre ogni scheda del sito mostra "N. Stock", che coincide con l'externalId del feed.
Lo script legge le sitemap, scarica solo le schede nuove (o vecchie di 7+ giorni)
e salva la mappa nel file indicato in config.SITES, così le esecuzioni successive sono veloci.

Uso: python crawl_site.py <sito>      (sito = chiave in config.SITES, es. azzurrastore, broker)
"""
import html
import json
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

import config

UA = "Mozilla/5.0 (compatible; AzzurraStoreMetaFeed/1.0)"
REFRESH_DAYS = 7
MAX_FETCH_PER_RUN = 2500
DELAY = 0.3

STOCK_RE = re.compile(r"N\.\s*Stock\s*:?\s*(\d{5,10})", re.I)


def get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def extract_stock(page_html):
    text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", page_html, flags=re.S | re.I)
    text = html.unescape(re.sub(r"<[^>]+>", " ", text))
    text = re.sub(r"\s+", " ", text)
    m = STOCK_RE.search(text)
    return m.group(1) if m else None


def sitemap_urls(cfg):
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = []
    for sm in cfg["sitemaps"]:
        root = ET.fromstring(get(sm))
        for loc in root.findall(".//s:loc", ns):
            u = loc.text.strip()
            if "/automobile/" in u and u.rstrip("/") != cfg["site"] + "/automobile":
                urls.append(u)
    return urls


def main(site_key):
    cfg = config.site_config(site_key)
    path = cfg["map_file"]
    try:
        cache = json.load(open(path))
    except FileNotFoundError:
        cache = {}  # url -> {"stock": "...", "checked": "ISO date"}

    live = set(sitemap_urls(cfg))
    for u in list(cache):
        if u not in live:
            del cache[u]

    now = datetime.now(timezone.utc)
    stale = now - timedelta(days=REFRESH_DAYS)
    todo = [u for u in live if u not in cache]
    todo += sorted(
        (u for u in live if u in cache and datetime.fromisoformat(cache[u]["checked"]) < stale),
        key=lambda u: cache[u]["checked"],
    )
    todo = todo[:MAX_FETCH_PER_RUN]

    ok = fail = 0
    for u in todo:
        try:
            stock = extract_stock(get(u))
            cache[u] = {"stock": stock, "checked": now.isoformat()}
            ok += stock is not None
            fail += stock is None
        except Exception as e:  # pagina giù o timeout: riprova alla prossima esecuzione
            print("ERR", u, e, file=sys.stderr)
        time.sleep(DELAY)

    json.dump(cache, open(path, "w"), indent=1, sort_keys=True)
    print(f"[{site_key}] sitemap: {len(live)} schede | scaricate ora: {len(todo)} "
          f"(stock trovato {ok}, non trovato {fail}) | in mappa: "
          f"{sum(1 for v in cache.values() if v['stock'])}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "azzurrastore")
