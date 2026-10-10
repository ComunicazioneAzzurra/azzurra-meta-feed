"""Impostazioni dei feed Meta (uno per sito). Modifica qui, non negli script."""

# ---------------------------------------------------------------------------
# Impostazioni comuni
# ---------------------------------------------------------------------------

# Prezzo da mostrare su Meta: deve coincidere con quello visibile sulla scheda del sito.
# "priceB2c" oppure "finalPrice" (nel feed DealerK differiscono su ~600 auto, soprattutto KM0).
PRICE_FIELD = "priceB2c"

# Meta accetta solo NEW / USED / CPO. Le KM0 sono immatricolate: di default USED,
# e vengono comunque etichettate "KM 0" in custom_label_0 per creare set dedicati.
KM0_STATE = "USED"

# Il VIN (telaio) non è obbligatorio per l'Italia; lasciarlo False evita di pubblicarlo.
INCLUDE_VIN = False

# Classi DealerK da escludere dal catalogo (le moto non hanno senso nel catalogo Veicoli)
EXCLUDE_CLASSES = {"moto"}

# Se il CSV risultante ha meno veicoli di così, il workflow si ferma e Meta
# continua a leggere l'ultimo CSV buono (evita di svuotare il catalogo per un errore).
MIN_ROWS = 300

# ---------------------------------------------------------------------------
# Siti
#   map_file: cache N. Stock -> URL scheda
#   output:   CSV letto da Meta (percorso dentro il repository)
#   sedi:     le auto con dealer non riconosciuto prendono default_sede.
#             Coordinate approssimative: verificale su Google Maps
#             (tasto destro sul punto -> copia coordinate).
# ---------------------------------------------------------------------------

SITES = {
    "azzurrastore": {
        "site": "https://azzurrastore.it",
        "brand": "Azzurra Store",
        "map_file": "url_map.json",
        "output": "docs/meta_vehicles.csv",
        "sedi": {
            "cuneo": {
                "name": "Azzurra Store Cuneo",
                "addr1": "Via della Motorizzazione, 1",
                "city": "Cuneo",
                "region": "Piemonte",
                "postal_code": "12100",
                "country": "IT",
                "latitude": 44.3907,
                "longitude": 7.5560,
                "phone": "+39 0171 412112",
            },
            "moncalieri": {
                "name": "Azzurra Store Moncalieri",
                "addr1": "Corso Trieste, 140",
                "city": "Moncalieri",
                "region": "Piemonte",
                "postal_code": "10024",
                "country": "IT",
                "latitude": 45.0003,
                "longitude": 7.6825,
                "phone": "+39 0171 412112",
            },
        },
        "default_sede": "cuneo",
        # nome dealer nel feed DealerK -> chiave in sedi
        "dealer_to_sede": {
            "azzurrastore": "moncalieri",
            "autoeservizio": "cuneo",
            "Auto&Servizio": "cuneo",
        },
    },
    "broker": {
        "site": "https://brokerautomobili.com",
        "brand": "Broker Automobili",
        "map_file": "url_map_broker.json",
        "output": "docs/broker/meta_vehicles.csv",
        # Il feed DealerK indica come sede solo Albenga; le altre sedi Broker
        # (Sanremo, Cairo Montenotte, Genova) non sono distinguibili dal feed.
        "sedi": {
            "albenga": {
                "name": "Broker Automobili Albenga",
                "addr1": "Regione Poca, 18",
                "city": "Albenga",
                "region": "Liguria",
                "postal_code": "17031",
                "country": "IT",
                "latitude": 44.0617,
                "longitude": 8.2005,
                "phone": "+39 019 9388009",
            },
        },
        "default_sede": "albenga",
        "dealer_to_sede": {},
    },
}


def site_config(key):
    if key not in SITES:
        raise SystemExit(f"Sito sconosciuto: {key}. Disponibili: {', '.join(SITES)}")
    cfg = dict(SITES[key])
    cfg["sitemaps"] = [cfg["site"] + "/automobile-sitemap1.xml",
                       cfg["site"] + "/automobile-sitemap2.xml"]
    return cfg
