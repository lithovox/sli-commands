# Settlement

Convert D-Settlement calculations (`.sli`) between the NEN-Koppejan and NEN-Bjerrum models.

[English](#english) | [Nederlands](#nederlands)

> **Note:** versions before v1.0 are not fully tested and may not be reliable. Always check the converted calculation.
>
> **Let op:** versies vóór v1.0 zijn niet volledig getest en mogelijk niet betrouwbaar. Controleer de omgezette berekening altijd.

## English

### Usage

```
slicmd -kj2bj <calculation.sli> <soils.csv>    Koppejan -> Bjerrum, writes <calculation>.bj.sli
slicmd -bj2kj <calculation.sli> <soils.csv>    Bjerrum -> Koppejan, writes <calculation>.kj.sli
slicmd -v                                      show the version
slicmd -h                                      show the help
```

Several files or wildcards are allowed, the soils file always comes last:

```
slicmd -kj2bj a.sli b.sli soils.csv
slicmd -kj2bj "C:\calculations\*.sli" soils.csv
slicmd -kj2bj "calculations/**/*.sli" soils.csv     (including subfolders)
```

- All soil parameters are taken from the soils file. Every soil in the calculation must be in it.
- Files that are already converted (`.bj.sli` for -kj2bj, `.kj.sli` for -bj2kj) are skipped. If one file fails, the others are still converted.
- -kj2bj switches to Darcy and linear strain, because NEN-Bjerrum requires them.
- An existing output file is overwritten.

Show the time-settlement curve of a vertical from the results of a calculation (`.sld`):

```
slicmd -i <calculation.sld> -vt <vertical>     time [days] and settlement [m], the first vertical is 1 (default)
```

### Soils file

A `;` separated file with one row per soil. See the example with dummy values in [examples/soils.csv](examples/soils.csv).

| Column | Meaning |
|---|---|
| `code` | soil name exactly as in D-Settlement |
| `yd`, `ys` | unit weight above / below the phreatic level [kN/m³] |
| `cp`, `cap`, `cs`, `cas` | Koppejan Cp, C'p, Cs, C's |
| `rr`, `cr`, `calpha` | Bjerrum RR, CR, Cα |
| `pop`, `ocr` | POP [kPa], OCR |
| `cv` | consolidation coefficient [m²/s] |
| `k` | vertical permeability [m/day] |

### Download

Latest build from master:

- [Windows (zip)](https://github.com/lithovox/sli-commands/releases/download/latest/slicmd-windows-x86_64.zip)
- [Linux (tar.gz)](https://github.com/lithovox/sli-commands/releases/download/latest/slicmd-linux-x86_64.tar.gz)

Unpack it and put `slicmd` in a folder on your PATH. Versioned releases are on the [releases page](https://github.com/lithovox/sli-commands/releases).

### Development

```
uv run pytest                                # tests

# release: bump the version (patch, minor or major), commit, tag and push
uv version --bump patch
git commit -am "Release $(uv version --short)"
git tag v$(uv version --short)
git push && git push --tags                  # GitHub builds and publishes the release
```

## Nederlands

### Gebruik

```
slicmd -kj2bj <berekening.sli> <grondsoorten.csv>    Koppejan -> Bjerrum, schrijft <berekening>.bj.sli
slicmd -bj2kj <berekening.sli> <grondsoorten.csv>    Bjerrum -> Koppejan, schrijft <berekening>.kj.sli
slicmd -v                                            toon de versie
slicmd -h                                            toon de help
```

Meerdere bestanden of wildcards zijn toegestaan, het grondsoortenbestand staat altijd als laatste:

```
slicmd -kj2bj a.sli b.sli grondsoorten.csv
slicmd -kj2bj "C:\berekeningen\*.sli" grondsoorten.csv
slicmd -kj2bj "berekeningen/**/*.sli" grondsoorten.csv     (inclusief submappen)
```

- Alle grondparameters komen uit het grondsoortenbestand. Elke grondsoort uit de berekening moet erin staan.
- Bestanden die al omgezet zijn (`.bj.sli` bij -kj2bj, `.kj.sli` bij -bj2kj) worden overgeslagen. Als één bestand mislukt, worden de andere toch omgezet.
- -kj2bj zet de berekening om naar Darcy en lineaire rek, omdat NEN-Bjerrum dat vereist.
- Een bestaand uitvoerbestand wordt overschreven.

Toon de tijd-zettingslijn van een verticaal uit de resultaten van een berekening (`.sld`):

```
slicmd -i <berekening.sld> -vt <verticaal>           tijd [dagen] en zetting [m], de eerste verticaal is 1 (standaard)
```

### Grondsoortenbestand

Een bestand gescheiden door `;` met één regel per grondsoort. Zie het voorbeeld met fictieve waarden in [examples/soils.csv](examples/soils.csv).

| Kolom | Betekenis |
|---|---|
| `code` | naam van de grondsoort, precies zoals in D-Settlement |
| `yd`, `ys` | volumegewicht boven / onder de freatische lijn [kN/m³] |
| `cp`, `cap`, `cs`, `cas` | Koppejan Cp, C'p, Cs, C's |
| `rr`, `cr`, `calpha` | Bjerrum RR, CR, Cα |
| `pop`, `ocr` | POP [kPa], OCR |
| `cv` | consolidatiecoëfficiënt [m²/s] |
| `k` | verticale doorlatendheid [m/dag] |

### Download

Laatste versie van master:

- [Windows (zip)](https://github.com/lithovox/sli-commands/releases/download/latest/slicmd-windows-x86_64.zip)
- [Linux (tar.gz)](https://github.com/lithovox/sli-commands/releases/download/latest/slicmd-linux-x86_64.tar.gz)

Pak het bestand uit en zet `slicmd` in een map die in je PATH staat. Releases met een versienummer staan op de [releasepagina](https://github.com/lithovox/sli-commands/releases).

### Ontwikkeling

```
uv run pytest                                # tests

# release: versie ophogen (patch, minor of major), committen, taggen en pushen
uv version --bump patch
git commit -am "Release $(uv version --short)"
git tag v$(uv version --short)
git push && git push --tags                  # GitHub bouwt en publiceert de release
```
