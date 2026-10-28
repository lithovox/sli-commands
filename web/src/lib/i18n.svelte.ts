// Dutch and English texts, the language is remembered in the browser.

const en = {
  subtitle: "Convert D-Settlement calculations between NEN-Koppejan and NEN-Bjerrum",
  "tab.convert": "Convert",
  "tab.parameters": "Soil parameters",
  "tab.results": "Results",
  "tab.diagnose": "Diagnostics",
  "python.download": "Downloading Python…",
  "python.start": "Starting Python…",
  "python.package": "Loading slicmd…",
  "python.ready": "Ready",
  "python.failed": "Python could not be started",
  "python.failed.help": "Open the diagnostics to see what is blocked.",
  privacy: "Your files never leave your computer, everything runs in this browser.",
  warning: "Versions before v1.0 are not fully tested and may not be reliable. Always check the converted calculation.",
  "drop.browse": "or click to choose",
  "drop.sli": "Drop D-Settlement calculations (.sli) here",
  "drop.sli.one": "Drop a D-Settlement calculation (.sli) here",
  "drop.csv": "Drop the soils file (.csv) here",
  "drop.sld": "Drop D-Settlement results (.sld) here",
  "convert.soils": "Soils file",
  "convert.soils.count": "{n} soils",
  "convert.soils.replace": "Replace",
  "convert.soils.hint": "No soils file yet? Create one from a calculation in the Soil parameters tab.",
  "convert.calculations": "Calculations",
  "convert.run": "Convert",
  "convert.run.all": "Convert {n} calculations",
  "convert.download": "Download",
  "convert.download.all": "Download all (zip)",
  "convert.clear": "Clear",
  "convert.missing": "Not in the soils file",
  "convert.no.model": "This model cannot be converted",
  "convert.done": "Converted to {name}",
  "convert.waiting": "Load a soils file to convert",
  "notice.terzaghi": "The calculation uses Terzaghi, Darcy is preferred.",
  "notice.strain": "Strain type changed from Natural to Linear, NEN-Bjerrum requires this.",
  "model.koppejan": "NEN-Koppejan",
  "model.bjerrum": "NEN-Bjerrum",
  "parameters.intro":
    "The soil parameters of a calculation, in the format of the soils file. Highlighted values are D-Settlement placeholders that still have to be filled in.",
  "parameters.download": "Download as soils.csv",
  "parameters.placeholder": "placeholder",
  "results.intro":
    "The settlement of the top of a vertical in time. Load the results (.sld) of one or more calculations with the same verticals to compare them.",
  "results.time": "Time [days]",
  "results.settlement": "Settlement [m]",
  "results.vertical": "Vertical {n} (x = {x} m)",
  "results.download": "Download (csv)",
  "results.table": "Show table",
  "results.chart": "Show chart",
  "results.remove": "Remove",
  "diagnose.intro":
    "These checks show whether the web application works on this computer and network. If a step fails, share this page with your IT department.",
  "diagnose.run": "Run again",
  "diagnose.copy": "Copy report",
  "diagnose.webassembly": "WebAssembly is available",
  "diagnose.worker": "A Web Worker can be started",
  "diagnose.pyodide": "Python (Pyodide) is downloaded and started",
  "diagnose.package": "The slicmd package is loaded",
  "diagnose.convert": "Example conversion Koppejan → Bjerrum",
  "diagnose.results": "Example results (.sld) are read",
  "diagnose.browser": "Browser",
  "theme.light": "Light theme",
  "theme.dark": "Dark theme",
  "error.read": "The file could not be read",
  remove: "Remove",
  "menu.tools": "Tools",
  "menu.support": "Support",
  "menu.fold": "Fold the menu",
  "menu.unfold": "Unfold the menu",
  "convert.intro":
    "Converts D-Settlement calculations from NEN-Koppejan to NEN-Bjerrum and back. The soil parameters come from the soils file, the model of each calculation is detected automatically.",
  "help.button": "Help",
  "help.title": "slicmd",
  "help.lead": "Converts D-Settlement calculations between NEN-Koppejan and NEN-Bjerrum, and shows their soil parameters and results.",
  "help.convert": "Load a soils file and one or more calculations (.sli). Each calculation is converted to the other model: .bj.sli for Bjerrum, .kj.sli for Koppejan.",
  "help.parameters": "Shows the soil parameters of a calculation in the format of the soils file, a good start for your own soils file.",
  "help.results": "Shows the settlement of each vertical in time from the results (.sld), several files can be compared.",
  "help.close": "Close",
  "language.title": "Language",
  "results.files": "Calculations",
  "results.verticals.count": "{n} vertical(s)",
  "results.vertical.select": "Vertical",
  "results.mismatch.count": "has {found} vertical(s) where {reference} has {expected}, the results cannot be compared.",
  "results.mismatch.position":
    "vertical {n} is at {found} where it is at {expected} in {reference}, the results cannot be compared.",
  "soils.intro": "The soil parameters below are used for the conversion. Changes take effect at once, download the soils file to keep them.",
  "soils.add": "Add soil",
  "soils.add.missing": "Add the {n} missing soil(s)",
  "soils.edited": "edited",
  "soils.download": "Download soils file",
  "soils.problems": "Correct these values before converting:",
};

export type Key = keyof typeof en;

const nl: Record<Key, string> = {
  subtitle: "Zet D-Settlement berekeningen om tussen NEN-Koppejan en NEN-Bjerrum",
  "tab.convert": "Omzetten",
  "tab.parameters": "Grondparameters",
  "tab.results": "Resultaten",
  "tab.diagnose": "Diagnose",
  "python.download": "Python downloaden…",
  "python.start": "Python starten…",
  "python.package": "slicmd laden…",
  "python.ready": "Gereed",
  "python.failed": "Python kon niet gestart worden",
  "python.failed.help": "Open de diagnose om te zien wat er geblokkeerd wordt.",
  privacy: "Je bestanden verlaten je computer niet, alles draait in deze browser.",
  warning:
    "Versies vóór v1.0 zijn niet volledig getest en mogelijk niet betrouwbaar. Controleer de omgezette berekening altijd.",
  "drop.browse": "of klik om te kiezen",
  "drop.sli": "Sleep D-Settlement berekeningen (.sli) hierheen",
  "drop.sli.one": "Sleep een D-Settlement berekening (.sli) hierheen",
  "drop.csv": "Sleep het grondsoortenbestand (.csv) hierheen",
  "drop.sld": "Sleep D-Settlement resultaten (.sld) hierheen",
  "convert.soils": "Grondsoortenbestand",
  "convert.soils.count": "{n} grondsoorten",
  "convert.soils.replace": "Vervangen",
  "convert.soils.hint": "Nog geen grondsoortenbestand? Maak er een van een berekening op het tabblad Grondparameters.",
  "convert.calculations": "Berekeningen",
  "convert.run": "Omzetten",
  "convert.run.all": "{n} berekeningen omzetten",
  "convert.download": "Downloaden",
  "convert.download.all": "Alles downloaden (zip)",
  "convert.clear": "Wissen",
  "convert.missing": "Niet in het grondsoortenbestand",
  "convert.no.model": "Dit model kan niet omgezet worden",
  "convert.done": "Omgezet naar {name}",
  "convert.waiting": "Laad een grondsoortenbestand om om te zetten",
  "notice.terzaghi": "De berekening gebruikt Terzaghi, Darcy heeft de voorkeur.",
  "notice.strain": "Rektype gewijzigd van Natural naar Linear, NEN-Bjerrum vereist dit.",
  "model.koppejan": "NEN-Koppejan",
  "model.bjerrum": "NEN-Bjerrum",
  "parameters.intro":
    "De grondparameters van een berekening, in het formaat van het grondsoortenbestand. Gemarkeerde waarden zijn standaardwaarden van D-Settlement die nog ingevuld moeten worden.",
  "parameters.download": "Downloaden als soils.csv",
  "parameters.placeholder": "standaardwaarde",
  "results.intro":
    "De zetting van de bovenkant van een verticaal in de tijd. Laad de resultaten (.sld) van een of meer berekeningen met dezelfde verticalen om ze te vergelijken.",
  "results.time": "Tijd [dagen]",
  "results.settlement": "Zetting [m]",
  "results.vertical": "Verticaal {n} (x = {x} m)",
  "results.download": "Downloaden (csv)",
  "results.table": "Tabel tonen",
  "results.chart": "Grafiek tonen",
  "results.remove": "Verwijderen",
  "diagnose.intro":
    "Deze controles laten zien of de webapplicatie werkt op deze computer en dit netwerk. Mislukt een stap, deel deze pagina dan met je IT-afdeling.",
  "diagnose.run": "Opnieuw uitvoeren",
  "diagnose.copy": "Rapport kopiëren",
  "diagnose.webassembly": "WebAssembly is beschikbaar",
  "diagnose.worker": "Een Web Worker kan gestart worden",
  "diagnose.pyodide": "Python (Pyodide) is gedownload en gestart",
  "diagnose.package": "Het slicmd-pakket is geladen",
  "diagnose.convert": "Voorbeeldomzetting Koppejan → Bjerrum",
  "diagnose.results": "Voorbeeldresultaten (.sld) zijn gelezen",
  "diagnose.browser": "Browser",
  "theme.light": "Licht thema",
  "theme.dark": "Donker thema",
  "error.read": "Het bestand kon niet gelezen worden",
  remove: "Verwijderen",
  "menu.tools": "Gereedschap",
  "menu.support": "Ondersteuning",
  "menu.fold": "Menu inklappen",
  "menu.unfold": "Menu uitklappen",
  "convert.intro":
    "Zet D-Settlement berekeningen om van NEN-Koppejan naar NEN-Bjerrum en terug. De grondparameters komen uit het grondsoortenbestand, het model van elke berekening wordt automatisch herkend.",
  "help.button": "Help",
  "help.title": "slicmd",
  "help.lead": "Zet D-Settlement berekeningen om tussen NEN-Koppejan en NEN-Bjerrum, en toont hun grondparameters en resultaten.",
  "help.convert": "Laad een grondsoortenbestand en een of meer berekeningen (.sli). Elke berekening wordt omgezet naar het andere model: .bj.sli voor Bjerrum, .kj.sli voor Koppejan.",
  "help.parameters": "Toont de grondparameters van een berekening in het formaat van het grondsoortenbestand, een goed begin voor je eigen grondsoortenbestand.",
  "help.results": "Toont de zetting van elke verticaal in de tijd uit de resultaten (.sld), meerdere bestanden kunnen vergeleken worden.",
  "help.close": "Sluiten",
  "language.title": "Taal",
  "results.files": "Berekeningen",
  "results.verticals.count": "{n} verticaal/verticalen",
  "results.vertical.select": "Verticaal",
  "results.mismatch.count": "heeft {found} verticaal/verticalen waar {reference} er {expected} heeft, de resultaten kunnen niet vergeleken worden.",
  "results.mismatch.position":
    "verticaal {n} ligt op {found} waar die in {reference} op {expected} ligt, de resultaten kunnen niet vergeleken worden.",
  "soils.intro": "De grondparameters hieronder worden gebruikt voor de omzetting. Wijzigingen gelden direct, download het grondsoortenbestand om ze te bewaren.",
  "soils.add": "Grondsoort toevoegen",
  "soils.add.missing": "De {n} ontbrekende grondsoort(en) toevoegen",
  "soils.edited": "gewijzigd",
  "soils.download": "Grondsoortenbestand downloaden",
  "soils.problems": "Verbeter deze waarden voordat je omzet:",
};

export type Language = "nl" | "en";

const TEXTS: Record<Language, Record<Key, string>> = { en, nl };

function stored(): Language {
  try {
    const language = localStorage.getItem("language");
    if (language === "nl" || language === "en") return language;
  } catch {
    // storage can be blocked, fall back to the browser language
  }
  return navigator.language.toLowerCase().startsWith("nl") ? "nl" : "en";
}

export const i18n = $state({ language: stored() });

export function setLanguage(language: Language) {
  i18n.language = language;
  document.documentElement.lang = language;
  try {
    localStorage.setItem("language", language);
  } catch {
    // not remembered, still works for this visit
  }
}

export function t(key: Key, values: Record<string, string | number> = {}): string {
  return TEXTS[i18n.language][key].replace(/\{(\w+)\}/g, (_, name) => String(values[name] ?? `{${name}}`));
}
