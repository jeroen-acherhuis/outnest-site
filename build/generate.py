#!/usr/bin/env python3
"""
Maakt de/index.html en en/index.html uit index.html plus build/translations.json.

index.html is de bron en bevat de Nederlandse tekst. Elk element met een
data-i18n sleutel wordt vervangen door de vertaling. Draai dit script na elke
tekstwijziging, anders lopen de vertaalde pagina's achter.

    python3 build/generate.py
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://outnest.eu"
OG_LOCALE = {"nl": "nl_NL", "de": "de_DE", "en": "en_GB"}
PAD = {"nl": "/", "de": "/de/", "en": "/en/"}

DESCRIPTION = {
    "de": ("Outnest ist die Marke von Oude Wesselink Tuinmeubelen B.V. aus Enter, Niederlande. "
           "Wir verkaufen Gartenmöbel über gartenmoebelfuerdich.de in Deutschland und über "
           "ikwiltuinmeubelen.nl in den Niederlanden und Belgien."),
    "en": ("Outnest is the brand of Oude Wesselink Tuinmeubelen B.V. in Enter, the Netherlands. "
           "We sell garden furniture through ikwiltuinmeubelen.nl in the Netherlands and Belgium "
           "and through gartenmoebelfuerdich.de in Germany."),
}
OG_TITLE = {"de": "Outnest, Gartenmöbel aus Enter", "en": "Outnest, garden furniture from Enter"}
OG_DESC = {
    "de": "Das Unternehmen hinter gartenmoebelfuerdich.de und ikwiltuinmeubelen.nl.",
    "en": "The company behind ikwiltuinmeubelen.nl and gartenmoebelfuerdich.de.",
}


def vervang_inhoud(html: str, woorden: dict, taal: str) -> str:
    """Vervangt de inhoud van elk element met een data-i18n sleutel.

    Zoekt het bijbehorende sluittag door nesting te tellen. Dat is nodig omdat
    sommige teksten zelf opmaak bevatten (de <strong> in de hero); een simpele
    zoektocht naar het eerste </ stopt daar halverwege en laat de rest van de
    oude taal staan.
    """
    ontbrekend = []
    uit = []
    pos = 0
    patroon = re.compile(r'<(\w+)([^>]*\sdata-i18n(?:-html)?="([^"]+)"[^>]*)>')

    while True:
        m = patroon.search(html, pos)
        if not m:
            uit.append(html[pos:])
            break
        tag, sleutel = m.group(1), m.group(3)
        uit.append(html[pos:m.end()])

        # bijbehorend sluittag zoeken, rekening houdend met dezelfde tag erbinnen
        diepte, i = 1, m.end()
        open_re = re.compile(rf'<{tag}\b', re.I)
        sluit_re = re.compile(rf'</{tag}\s*>', re.I)
        while diepte:
            o, c = open_re.search(html, i), sluit_re.search(html, i)
            if not c:
                raise SystemExit(f"geen sluittag </{tag}> gevonden voor sleutel {sleutel}")
            if o and o.start() < c.start():
                diepte += 1
                i = o.end()
            else:
                diepte -= 1
                i = c.start() if diepte else c.start()
                if diepte:
                    i = c.end()
        if sleutel in woorden:
            uit.append(woorden[sleutel])
        else:
            ontbrekend.append(sleutel)
            uit.append(html[m.end():i])
        pos = i

    if ontbrekend:
        print(f"  LET OP: {taal} mist vertalingen voor {sorted(set(ontbrekend))}", file=sys.stderr)
    return "".join(uit)


def vertaal(html: str, woorden: dict, taal: str, titel: str) -> str:
    html = vervang_inhoud(html, woorden, taal)
    html = html.replace('<html lang="nl">', f'<html lang="{taal}">')
    html = re.sub(r'<title>.*?</title>', f'<title>{titel}</title>', html, flags=re.S)
    html = re.sub(r'(<meta name="description" content=")[^"]*(")',
                  lambda m: m.group(1) + DESCRIPTION[taal] + m.group(2), html)
    html = html.replace('<link rel="canonical" href="https://outnest.eu/">',
                        f'<link rel="canonical" href="{SITE}{PAD[taal]}">')
    html = html.replace('<meta property="og:url" content="https://outnest.eu/">',
                        f'<meta property="og:url" content="{SITE}{PAD[taal]}">')
    html = re.sub(r'(<meta property="og:title" content=")[^"]*(")',
                  lambda m: m.group(1) + OG_TITLE[taal] + m.group(2), html)
    html = re.sub(r'(<meta property="og:description" content=")[^"]*(")',
                  lambda m: m.group(1) + OG_DESC[taal] + m.group(2), html)
    html = html.replace('<meta property="og:locale" content="nl_NL">',
                        f'<meta property="og:locale" content="{OG_LOCALE[taal]}">')
    html = html.replace('"inLanguage": "nl-NL"', f'"inLanguage": "{OG_LOCALE[taal].replace("_", "-")}"')
    html = html.replace('<a href="/" hreflang="nl" aria-current="true">',
                        '<a href="/" hreflang="nl" aria-current="false">')
    html = html.replace(f'<a href="{PAD[taal]}" hreflang="{taal}" aria-current="false">',
                        f'<a href="{PAD[taal]}" hreflang="{taal}" aria-current="true">')
    html = html.replace(f'<html lang="{taal}">',
                        f'<html lang="{taal}">\n<!-- Gegenereerd door build/generate.py. Niet met de hand aanpassen. -->')
    return html



SITEMAP_PADEN = ("sitemap.xml", "sitemap-pages.xml")


def schrijf_sitemaps():
    """Schrijft de sitemap naar meerdere paden vanuit één definitie.

    Twee paden omdat Google de status van een sitemap-URL blijvend kan
    vasthouden na één mislukte leespoging: opnieuw indienen op hetzelfde pad
    doet niets, en een variant met querystring wordt genormaliseerd. Een nieuw
    pad is de enige manier om een verse leespoging te forceren. Beide bestanden
    komen hier uit dezelfde lijst, zodat ze niet uit elkaar kunnen lopen.
    """
    alts = "".join(
        f'\n    <xhtml:link rel="alternate" hreflang="{t}" href="{SITE}{PAD[t]}"/>'
        for t in ("nl", "de", "en")
    ) + f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}{PAD["nl"]}"/>'

    blokken = []
    for taal, prio in (("nl", "1.0"), ("de", "0.8"), ("en", "0.8")):
        blokken.append(
            f"  <url>\n    <loc>{SITE}{PAD[taal]}</loc>{alts}"
            f"\n    <changefreq>monthly</changefreq>\n    <priority>{prio}</priority>\n  </url>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(blokken)
        + "\n</urlset>\n"
    )
    for naam in SITEMAP_PADEN:
        (ROOT / naam).write_text(xml)
        print(f"  {naam} geschreven ({len(blokken)} urls)")


def main():
    bron = (ROOT / "index.html").read_text()
    vert = json.loads((ROOT / "build" / "translations.json").read_text())
    for taal in ("de", "en"):
        map_ = ROOT / taal
        map_.mkdir(exist_ok=True)
        uit = vertaal(bron, vert[taal], taal, vert["titles"][taal])
        (map_ / "index.html").write_text(uit)
        print(f"  {taal}/index.html geschreven ({len(uit)} tekens)")
    schrijf_sitemaps()


if __name__ == "__main__":
    main()
