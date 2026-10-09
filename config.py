"""Impostazioni del feed Meta per Azzurra Store. Modifica qui, non negli script."""

SITE = "https://azzurrastore.it"
SITEMAPS = [
    SITE + "/automobile-sitemap1.xml",
    SITE + "/automobile-sitemap2.xml",
]

# Prezzo da mostrare su Meta: deve coincidere con quello visibile sulla scheda del sito.
# "priceB2c" oppure "finalPrice" (nel feed DealerK differiscono su ~600 auto, soprattutto KM0).
PRICE_FIELD = "priceB2c"

# Meta accetta solo NEW / USED / CPO. Le KM0 sono immatricolate: di default USED,
# e vengono comunque etichettate "KM0" in custom_label_0 per creare set dedicati.
KM0_STATE = "USED"

# Il VIN (telaio) non è obbligatorio per l'Italia; lasciarlo False evita di pubblicarlo.
INCLUDE_VIN = False

# Sedi. Le auto con dealer "altro" nel feed DealerK prendono la sede di default.
# Le coordinate sono approssimative: verificale su Google Maps (tasto destro → copia coordinate).
SEDI = {
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
}
DEFAULT_SEDE = "cuneo"
# nome dealer nel feed DealerK -> chiave in SEDI
DEALER_TO_SEDE = {
    "azzurrastore": "moncalieri",
    "autoeservizio": "cuneo",
    "Auto&Servizio": "cuneo",
}

# Classi DealerK da escludere dal catalogo (le moto non hanno senso nel catalogo Veicoli)
EXCLUDE_CLASSES = {"moto"}

# Se il CSV risultante ha meno veicoli di così, il workflow si ferma e Meta
# continua a leggere l'ultimo CSV buono (evita di svuotare il catalogo per un errore).
MIN_ROWS = 300
