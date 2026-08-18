# outnest-site

Merksite voor **Outnest** op `outnest.eu`, het bedrijf achter
`ikwiltuinmeubelen.nl` en `gartenmoebelfuerdich.de`.

Twee doelen. Eerst het merk bouwen, met één plek die uitlegt wat Outnest is.
En daarnaast de mailadressen legitimeren: wie een mail krijgt van `@outnest.eu`
en de URL intikt, komt op een echte, herkenbare bedrijfspagina uit in plaats
van op een geparkeerd domein.

## Wat het is

Eén statische pagina, geen build-stap, geen dependencies. Alles staat in
`index.html` (HTML + CSS + een klein stukje JS).

```
index.html          Nederlandse pagina, tevens de bron voor de vertalingen
de/index.html       gegenereerd, niet met de hand aanpassen
en/index.html       gegenereerd, niet met de hand aanpassen
build/generate.py   maakt de/ en en/ uit index.html
build/translations.json  Duitse en Engelse teksten
llms.txt            samenvatting voor AI-zoekmachines
assets/fonts.css    @font-face-regels, verwijzen lokaal
assets/fonts/*.woff2 Fraunces + DM Sans, zelf gehost
assets/logo-outnest.svg  logo met fill="currentColor"
assets/favicon.svg  logo op donkergroen
assets/logo-outnest.png  512×512 logo op groen, voor JSON-LD
assets/og.jpg       social-preview 1200×630
assets/img/*.webp   de foto's (zie hieronder)
build/og-source.html  bron van og.jpg (wordt niet gepubliceerd)
server.js           statische webserver zonder dependencies
```

## Foto's

Alle beeld komt uit de eigen Shopify-bibliotheek, verkleind en als WebP
opgeslagen in `assets/img/`. Samen ongeveer 940 KB.

| bestand | wat | bron |
|---|---|---|
| `hero-1800.webp` / `hero-900.webp` | hero-achtergrond, avondtuin met lichtjes | Barcelona-loungeset, lifestyle |
| `shop-nl.webp` | kaart ikwiltuinmeubelen.nl | Menorca Avalon tuinset |
| `shop-de.webp` | kaart gartenmoebelfuerdich.de | hero van de Duitse shop |
| `bezorging.webp` | de eigen bezorgwagens | Shopify Files |
| `showroom.webp` | het pand aan De Bleek 2 | `locatie-ikwiltuinmeubelen.nl.png` |

De hero draait op een CSS-wash over de foto. Die wash is niet cosmetisch:
hij zorgt dat de zandkleurige tekst leesbaar blijft. Gemeten haalt hij nu
5,8:1 op desktop en 6,9:1 op mobiel, ruim boven de WCAG AA-eis van 4,5:1.
**Vervang je de hero-foto, meet dat contrast dan opnieuw** en trek de wash
zo nodig aan.

Geef elke `<img>` altijd `width` en `height` mee, zodat de ruimte
gereserveerd is voor de foto geladen is. De CSS zet `height:auto` op alle
`img`; laat die regel staan, anders wint het height-attribuut en rekt het
beeld uit.

## Lokaal draaien

```bash
npm start
```

Of zonder Node:

```bash
python3 -m http.server 4321
```

## Deployen

**De site draait live op GitHub Pages**, vanaf de `main`-branch van deze repo.
Push naar `main` en de site is binnen een minuut bijgewerkt. Daarom staat de
repo publiek: op een gratis GitHub-plan werkt Pages alleen vanaf een publieke
repo. `CNAME` legt het domein vast, `.nojekyll` slaat de Jekyll-stap over.

De DNS staat bij TransIP en wijst sinds 17 augustus 2026 naar GitHub:

```
@    3600  A     185.199.108.153
@    3600  A     185.199.109.153
@    3600  A     185.199.110.153
@    3600  A     185.199.111.153
@    3600  AAAA  2606:50c0:8000::153
@    3600  AAAA  2606:50c0:8001::153
@    3600  AAAA  2606:50c0:8002::153
@    3600  AAAA  2606:50c0:8003::153
www  3600  CNAME jeroen-acherhuis.github.io.
```

Daarvoor stond er een enkel `A` naar `37.97.254.27` en een `AAAA` naar
`2a01:7c8:3:1337::27`, allebei de parkeerpagina van TransIP.

**Kom nooit aan de andere records.** Dit domein draagt de mail van het hele
bedrijf: `MX` naar Google Workspace, `SPF`, `DMARC` en DKIM-records voor Google,
SendGrid en Shopify. Ook `ops.outnest.eu` hangt eraan, dat is de Railway-app.
Ga je toch iets wijzigen, gebruik dan eerst Bulkopties in het TransIP-paneel:
daar zit "Herstel een vorige versie", wat een werkende terugrolknop is.

`server.js` en `railway.json` zitten er nog in voor het geval de site ooit naar
Railway moet. Voor GitHub Pages zijn ze niet in gebruik.

## Talen

Drie echte pagina's, geen JavaScript-schakelaar:

| URL | taal |
|---|---|
| `/` | Nederlands |
| `/de/` | Duits |
| `/en/` | Engels |

Dat is bewust zo. Eerder stonden alle talen op één URL en wisselde JavaScript
de tekst om. Zoekmachines zagen daardoor alleen de Nederlandse versie; de
Duitse en Engelse tekst zat wel in de pagina, maar in een `<script>` en dus
niet als indexeerbare inhoud. Nu heeft elke taal een eigen URL, verwijzen ze
met `hreflang` naar elkaar, en zijn de taalknoppen gewone links die Google kan
volgen.

**`index.html` is de bron.** Daar staat de Nederlandse tekst in. De andere twee
pagina's worden eruit gegenereerd:

```bash
python3 build/generate.py
```

Tekst aanpassen gaat zo. Nederlands wijzig je in `index.html`, bij het element
met `data-i18n="..."`. Duits en Engels staan in `build/translations.json` onder
dezelfde sleutel. Daarna het script draaien, anders lopen `/de/` en `/en/`
achter. Het script waarschuwt als een sleutel in een taal ontbreekt.

Kom niet met de hand aan `de/index.html` of `en/index.html`; die worden
overschreven.

Let op bij het toevoegen van teksten met opmaak erin: de generator zoekt het
bijbehorende sluittag door nesting te tellen, juist omdat de hero-tekst een
`<strong>` bevat. Zet nooit een icoon of link binnen een `data-i18n`-element,
want de hele inhoud wordt vervangen. Daarom staat de pijl in de webshopkaarten
buiten de vertaalde `<span>`.

## og.jpg opnieuw maken

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --hide-scrollbars --window-size=1200,630 \
  --screenshot=/tmp/og.png "file://$PWD/build/og-source.html"
python3 -c "from PIL import Image; Image.open('/tmp/og.png').convert('RGB').save('assets/og.jpg','JPEG',quality=84,optimize=True)"
```

## Meten

**Google Search Console** staat aan als domein-property `sc-domain:outnest.eu`.
Die dekt http, https, www en alle subdomeinen in één. Verificatie ging
automatisch via de Google-verificatie die al in de DNS stond, dus daar hoefde
geen record voor bij. `sitemap.xml` is ingediend.

**Google Analytics 4** meet sinds 18 augustus 2026 op property `outnest.eu`
in het GA-account `Outnest`, webstream "Merksite outnest.eu", metings-ID
`G-C82FY5DH04`. Die staat bovenin het script in `index.html`:

```js
var GA_ID = "G-C82FY5DH04";
```

Maak je die leeg, dan laadt er geen Google-script meer en verdwijnt ook de
cookiemelding. Handig om meten tijdelijk uit te zetten.

De opzet is toestemming-eerst, en dat is geen keuze maar een eis: GA4 zet
cookies en de site richt zich op Nederland, België en Duitsland. Consent Mode
staat standaard op `denied` voor alles wat met analytics en advertenties te
maken heeft, `gtag.js` wordt pas ingeladen nadat iemand op Akkoord klikt, en de
keuze blijft in `localStorage` staan. Wie weigert, wordt niet gemeten.

Zet dus nooit een kale `gtag.js` in de `<head>`; dan meet je vóór toestemming
en dat mag niet.

## SEO

Wat er staat, en waarom:

Elke taal heeft een eigen URL met eigen `title`, `description`, `canonical` en
`og:locale`, en alle drie verwijzen met `hreflang` naar elkaar plus een
`x-default` naar het Nederlands. `sitemap.xml` bevat alle drie de URLs met
diezelfde hreflang-annotaties.

De structured data is een `@graph` met drie nodes: `Organization` (met `vatID`
en `taxID`, dat koppelt het domein aan het KvK-nummer), `WebSite`, en
`FurnitureStore` voor de showroom aan De Bleek 2. Openingstijden staan er
bewust niet in, die worden op de shop onderhouden en zijn hier niet
geverifieerd.

De hero is een CSS-achtergrond en wordt daardoor pas ontdekt nadat de CSS is
geparsed. Er staat daarom een `preload` op, met een `media`-conditie zodat
mobiel de kleine versie voorlaadt en desktop de grote. Vervang je de
hero-afbeelding, pas dan ook die twee preload-regels aan.

`llms.txt` staat in de root voor AI-zoekmachines. Houd die in lijn met de
pagina als er iets aan de bedrijfsgegevens verandert.

## Gecontroleerde bedrijfsgegevens

Overgenomen uit het Impressum van de Shopify-shop, niet zelf verzonnen:

| | |
|---|---|
| Rechtspersoon | Oude Wesselink Tuinmeubelen B.V. |
| Adres | De Bleek 2, 7468 DL Enter, Nederland |
| KvK | 61413585 |
| BTW | NL854331712B01 |
| Telefoon NL | 0546 - 633 464 |
| Telefoon DE | +49 5941 7964999 |
| E-mail NL | info@ikwiltuinmeubelen.nl |
| E-mail DE | info@gartenmoebelfuerdich.de |

Deze staan ook als `Organization` JSON-LD in de pagina, inclusief `vatID` en
`taxID`. Dat is precies wat zoekmachines nodig hebben om `outnest.eu` aan het
bedrijf te koppelen.

## Nog openstaand

- **Zakelijk mailadres.** Het blok "Zakelijk & leveranciers" verwijst nu naar
  de klantenservice, omdat niet vaststaat dat er al een `info@outnest.eu`-postvak
  is. Zodra dat er is: adres in het blok zetten en als derde `contactPoint`
  (`contactType: "sales"`) in de JSON-LD.
- **"Outnest is het merk van…"** is bewust zo geformuleerd. Als Outnest als
  handelsnaam bij de KvK staat, mag daar "handelsnaam" staan; dat is niet
  geverifieerd.
- **Openingstijden** staan er niet in. Die worden doorgelinkt naar de
  showroompagina van de shop, zodat ze op één plek onderhouden worden.
- **Teksten.** Geen kastlijntjes, geen opsommingen in lopende tekst, geen
  wollige marketingzinnen. Kopjes zijn gewone labels ("Contact", "Showroom",
  "Onze webshops"), geen bedachte oneliners. De eerste versie had koppen als
  "Wie je waarvoor hebt" en "Twee winkels, één magazijn"; die zijn eruit omdat
  ze klinken als iets dat een tekstgenerator verzint. Houd dat zo.
