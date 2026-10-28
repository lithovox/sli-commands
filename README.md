# Settlement

Convert D-Settlement calculations (`.sli`) between the NEN-Koppejan and NEN-Bjerrum models.

[English](#english) | [Nederlands](#nederlands)

## English

### Usage

```
kj2bj <calculation.sli> <soils.csv>    Koppejan -> Bjerrum, writes <calculation>.bj.sli
bj2kj <calculation.sli> <soils.csv>    Bjerrum -> Koppejan, writes <calculation>.kj.sli
```

- All soil parameters are taken from the soils file. Every soil in the calculation must be in it.
- kj2bj switches to Darcy and linear strain, because NEN-Bjerrum requires them.
- An existing output file is overwritten.

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

### Installation

Download the zip (Windows) or tar.gz (Linux) from the GitHub releases and put `kj2bj` and `bj2kj` in a folder on your PATH.

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
kj2bj <berekening.sli> <grondsoorten.csv>    Koppejan -> Bjerrum, schrijft <berekening>.bj.sli
bj2kj <berekening.sli> <grondsoorten.csv>    Bjerrum -> Koppejan, schrijft <berekening>.kj.sli
```

- Alle grondparameters komen uit het grondsoortenbestand. Elke grondsoort uit de berekening moet erin staan.
- kj2bj zet de berekening om naar Darcy en lineaire rek, omdat NEN-Bjerrum dat vereist.
- Een bestaand uitvoerbestand wordt overschreven.

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

### Installatie

Download de zip (Windows) of tar.gz (Linux) van de GitHub releases en zet `kj2bj` en `bj2kj` in een map die in je PATH staat.

### Ontwikkeling

```
uv run pytest                                # tests

# release: versie ophogen (patch, minor of major), committen, taggen en pushen
uv version --bump patch
git commit -am "Release $(uv version --short)"
git tag v$(uv version --short)
git push && git push --tags                  # GitHub bouwt en publiceert de release
```
