"""Converte il feed XML DealerK (myPortalXML) nel catalogo Veicoli di Meta (CSV).

Uso: python convert.py feed_dealerk.xml url_map.json meta_vehicles.csv

Nel CSV finiscono solo le auto che hanno una scheda su azzurrastore.it
(cioè lo stock trovato in url_map.json). vehicle_id = N. Stock del sito
(= externalId DealerK), lo stesso ID che il pixel invia in content_ids.
"""
import csv
import html
import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import date

import config

MAX_IMAGES = 20

BODY = {
    "berlina 2 vol.": "HATCHBACK", "suv": "SUV", "crossover": "CROSSOVER",
    "furgone": "VAN", "vettura furgonata": "VAN", "wagon": "WAGON",
    "monovolume": "MINIVAN", "multispazio": "MINIVAN", "cabriolet": "CONVERTIBLE",
    "fuoristrada": "SUV", "pick-up": "PICKUP", "coupé": "COUPE", "cabinato": "TRUCK",
}
FUEL = {"ibrido": "HYBRID", "diesel": "DIESEL", "benzina": "PETROL",
        "gpl": "OTHER", "metano": "OTHER", "elettrico": "ELECTRIC"}
FUEL_LABEL = {"ibrido": "Ibrida", "diesel": "Diesel", "benzina": "Benzina",
              "gpl": "Benzina/GPL", "elettrico": "Elettrica"}
PHEV_RE = re.compile(r"\b(phev|plug-?in|4xe|e-hybrid|hybrid\s*plug)\b", re.I)
GEAR = {"manuale": "MANUAL", "automatico": "AUTOMATIC"}
DRIVE = {"FRONT": "FWD", "RWD": "RWD", "PERMANENT_4WD": "AWD"}
TYPE_LABEL = {"NEW": "Nuova", "USED": "Usata", "KM0": "KM 0"}

COLUMNS = [
    "vehicle_id", "title", "description", "url", "make", "model", "trim", "year",
    "mileage.value", "mileage.unit", "price", "state_of_vehicle", "availability",
    "body_style", "fuel_type", "transmission", "drivetrain", "exterior_color",
    "date_first_on_lot", "dealer_name", "dealer_phone",
    "address.addr1", "address.city", "address.region", "address.postal_code",
    "address.country", "latitude", "longitude",
    "custom_label_0", "custom_label_1", "custom_label_2", "custom_label_3", "custom_label_4",
] + (["vin"] if config.INCLUDE_VIN else []) + [f"image[{i}].url" for i in range(MAX_IMAGES)]


def t(car, path):
    return (car.findtext(path) or "").strip()


def nice(s):
    """'FIAT' -> 'Fiat', ma lascia stare sigle brevi come 'DR', 'BMW', 'DS'."""
    return s.title() if len(s) > 3 and s.isupper() else s


def fuel_of(car):
    raw = t(car, "fuelType").lower()
    if raw == "ibrido" and PHEV_RE.search(t(car, "version")):
        return "PLUGIN_HYBRID", "Ibrida plug-in"
    return FUEL.get(raw, "OTHER"), FUEL_LABEL.get(raw, raw.capitalize())


def price_band(p):
    for limit, label in [(10000, "fino a 10k"), (15000, "10-15k"), (20000, "15-20k"),
                         (30000, "20-30k"), (45000, "30-45k")]:
        if p < limit:
            return label
    return "oltre 45k"


def build_row(car, url):
    make, model, version = nice(t(car, "make")), t(car, "model"), t(car, "version")
    vtype = t(car, "type")
    km = int(float(t(car, "km") or 0)) if vtype != "NEW" else 0
    reg = t(car, "registrationDate")  # MM/YYYY
    year = reg[-4:] if re.fullmatch(r"\d{2}/\d{4}", reg) else str(date.today().year)
    price = float(t(car, f"prices/{config.PRICE_FIELD}") or t(car, "prices/finalPrice") or 0)
    fuel, fuel_label = fuel_of(car)
    gear = t(car, "gear/gearType").lower()

    sede = config.SEDI[config.DEALER_TO_SEDE.get(t(car, "dealer/name"), config.DEFAULT_SEDE)]

    imgs = sorted(car.findall("images/image"),
                  key=lambda i: (i.get("main") != "true", int(i.get("index") or 999)))
    imgs = [i.text.strip() for i in imgs if (i.text or "").strip()][:MAX_IMAGES]

    equip = [re.sub(r"^[-\s]+", "", e.text or "").strip() for e in car.findall("equipments/equipment")]
    equip = [e for e in equip if e]
    facts = []
    if reg:
        facts.append(f"immatricolata {reg}")
    facts.append(f"{km:,} km".replace(",", "."))
    facts.append(fuel_label.lower())
    if gear:
        facts.append(f"cambio {gear}")
    if t(car, "exterior/color"):
        facts.append(f"colore {t(car, 'exterior/color').lower()}")
    desc_parts = [
        f"{make} {model} {version}".strip() + f" – {TYPE_LABEL.get(vtype, vtype)}.",
        ", ".join(facts).capitalize() + ".",
    ]
    if equip:
        desc_parts.append("Dotazioni: " + ", ".join(equip[:15]) + ".")
    desc_parts.append(f"Disponibile da {sede['name']}.")

    row = {
        "vehicle_id": car.get("externalId"),
        "title": f"{make} {model} {version}".strip()[:150],
        "description": " ".join(desc_parts)[:5000],
        "url": url,
        "make": make,
        "model": model,
        "trim": version,
        "year": year,
        "mileage.value": km,
        "mileage.unit": "KM",
        "price": f"{price:.2f} EUR",
        "state_of_vehicle": config.KM0_STATE if vtype == "KM0" else vtype,
        "availability": "AVAILABLE" if t(car, "status") == "FREE" else "PENDING",
        "body_style": BODY.get(t(car, "bodyType").lower(), "OTHER"),
        "fuel_type": fuel,
        "transmission": GEAR.get(gear, "OTHER"),
        "drivetrain": DRIVE.get(t(car, "tractionType"), "OTHER"),
        "exterior_color": t(car, "exterior/color") or "n.d.",
        "date_first_on_lot": t(car, "enteredInStockDate")[:10],
        "dealer_name": sede["name"],
        "dealer_phone": sede["phone"],
        "address.addr1": sede["addr1"], "address.city": sede["city"],
        "address.region": sede["region"], "address.postal_code": sede["postal_code"],
        "address.country": sede["country"],
        "latitude": sede["latitude"], "longitude": sede["longitude"],
        "custom_label_0": TYPE_LABEL.get(vtype, vtype),           # Nuova / Usata / KM 0
        "custom_label_1": price_band(price),                      # fascia prezzo
        "custom_label_2": "Commerciale" if t(car, "vehicleClass") == "lcv" else "Auto",
        "custom_label_3": fuel_label,
        "custom_label_4": sede["city"],
    }
    if config.INCLUDE_VIN:
        row["vin"] = t(car, "vin")
    for i, u in enumerate(imgs):
        row[f"image[{i}].url"] = u
    return row


def main(feed_path, map_path, out_path):
    cars = ET.parse(feed_path).getroot().findall("car")
    url_map = {}
    for url, v in json.load(open(map_path)).items():
        if v.get("stock"):
            url_map[v["stock"]] = url

    rows, skipped = [], {"senza scheda sul sito": 0, "classe esclusa": 0,
                         "senza foto": 0, "senza prezzo pubblico": 0}
    for car in cars:
        if t(car, "vehicleClass") in config.EXCLUDE_CLASSES:
            skipped["classe esclusa"] += 1
            continue
        url = url_map.get(car.get("externalId"))
        if not url:
            skipped["senza scheda sul sito"] += 1
            continue
        if not car.findall("images/image"):
            skipped["senza foto"] += 1
            continue
        row = build_row(car, url)
        if row["price"].startswith("0.00"):
            skipped["senza prezzo pubblico"] += 1
            continue
        rows.append(row)

    print(f"feed DealerK: {len(cars)} veicoli | nel catalogo Meta: {len(rows)} | scartati: {skipped}")
    if len(rows) < config.MIN_ROWS:
        # protezione: un feed DealerK vuoto o rotto non deve svuotare il catalogo Meta
        sys.exit(f"Solo {len(rows)} veicoli (minimo {config.MIN_ROWS}): CSV non aggiornato")

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main(*sys.argv[1:4])
