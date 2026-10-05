#!/usr/bin/env python3
"""Every piece of text the kit viewer's window shows, by language.

PLAN-KITS-PY.md section 3.4, "Idioma da interface" (KITS-TASK-36).  The
window speaks US English unless asked otherwise; `pt-BR` is the other
language.  Plain Python and the standard library only -- no `.ts`/`.qm`, no
generated binary -- so `kits_selftest` imports it with no venv.

Who picks, in order: `ui/app.py --lang <code>`, the variable
`WE2002_KITS_LANG`, and `DEFAULT`.  An unknown code is refused, never swapped
for the default in silence.

What is NOT here: the core's and the CLI's messages (`kit.problems`, notes,
record and zone names) stay English, and team names come from the disc or the
English table (section 3.3).  With `pt-BR` chosen those still read in English;
that is the assumed limit, not a defect.

A key added here goes in EVERY language with the same `{fields}`: the
selftest refuses a catalog that differs.

Usage:
    python tools/kits/ui/i18n.py          # the self-check
"""

from __future__ import annotations

import os
import string

DEFAULT = "en-US"
ENV = "WE2002_KITS_LANG"

NAMES = {"en-US": "English (US)", "pt-BR": "Português (Brasil)"}
"""Each language by its own name: the selector shows them the same whatever
language is in force."""

CATALOG = {
    "en-US": {
        "window_title": "kits",
        "open": "Open…",
        "nothing_open": "nothing open",
        "language": "Language",
        "image": "Image",
        "palette": "Palette",
        "zoom": "Zoom",
        "zoom_item": "{zoom}×",
        "checker": "Checker",
        "grid": "Grid 16×16",
        "zones": "Zones",
        "export_png": "Export PNG",
        "tab_plan": "Plan",
        "work_set_1": "work bitmap, 1st set",
        "work_set_2": "work bitmap, 2nd set",
        "kit_tag": "TEX_{tag}",
        "kit_team": "{team} — TEX_{tag}",
        "kit_ml_default": "Master League default — TEX_{tag}",
        "open_title": "Open a CD image or a TEX",
        "open_filter": "CD image or TEX (*.bin *.iso *.cue *.BIN);;All files (*)",
        "export_title": "Export PNG",
        "export_filter": "PNG (*.png)",
        "status_refused": "{label} refused: {problems}",
        "status_kit": "{label}, {size} bytes",
        "status_kit_notes": "{label}, {size} bytes — {notes}",
        "status_exported": "exported: {path}",
        "status_not_written": "did not write {path}",
        "readout_xy": "x {x}, y {y}",
        "readout_zone": "zone: {zone}",
        "zone_none": "none",
        "readout_entry": "index {index} · BGR555 0x{bgr555:04x} · RGB {r},{g},{b}",
        "readout_transparent": " · transparent",
        "tab_3d": "3D",
        "kit_set": "Set",
        "set_first": "first",
        "set_second": "second",
        "figure": "Figure",
        "figure_player": "player",
        "figure_keeper": "goalkeeper",
        "figure_hint": "drag to turn",
        "figure_geometry": "3D geometry: {path}",
        "figure_off": "3D off: {reason}",
        "tab_diag": "Diagnosis",
        "diag_refused": "{label}: refused by the guard, {count} problem(s)",
        "diag_notes": "{label}: read, with {count} note(s)",
        "diag_clean": "{label}: read, nothing to report",
        "diag_problem": "Refused: {text}",
        "diag_note": "Note: {text}",
    },
    "pt-BR": {
        "window_title": "kits",
        "open": "Abrir…",
        "nothing_open": "nada aberto",
        "language": "Idioma",
        "image": "Imagem",
        "palette": "Paleta",
        "zoom": "Zoom",
        "zoom_item": "{zoom}×",
        "checker": "Xadrez",
        "grid": "Grade 16×16",
        "zones": "Zonas",
        "export_png": "Exportar PNG",
        "tab_plan": "Plano",
        "work_set_1": "bitmap de trabalho, 1º conjunto",
        "work_set_2": "bitmap de trabalho, 2º conjunto",
        "kit_tag": "TEX_{tag}",
        "kit_team": "{team} — TEX_{tag}",
        "kit_ml_default": "Padrão da Master League — TEX_{tag}",
        "open_title": "Abrir imagem de CD ou TEX",
        "open_filter": "Imagem de CD ou TEX (*.bin *.iso *.cue *.BIN);;Todos (*)",
        "export_title": "Exportar PNG",
        "export_filter": "PNG (*.png)",
        "status_refused": "{label} recusado: {problems}",
        "status_kit": "{label}, {size} bytes",
        "status_kit_notes": "{label}, {size} bytes — {notes}",
        "status_exported": "exportado: {path}",
        "status_not_written": "não gravou {path}",
        "readout_xy": "x {x}, y {y}",
        "readout_zone": "zona: {zone}",
        "zone_none": "nenhuma",
        "readout_entry": "índice {index} · BGR555 0x{bgr555:04x} · RGB {r},{g},{b}",
        "readout_transparent": " · transparente",
        "tab_3d": "3D",
        "kit_set": "Conjunto",
        "set_first": "titular",
        "set_second": "suplente",
        "figure": "Figura",
        "figure_player": "jogador",
        "figure_keeper": "goleiro",
        "figure_hint": "arraste para girar",
        "figure_geometry": "geometria do 3D: {path}",
        "figure_off": "3D desligado: {reason}",
        "tab_diag": "Diagnóstico",
        "diag_refused": "{label}: recusado pela guarda, {count} problema(s)",
        "diag_notes": "{label}: lido, com {count} nota(s)",
        "diag_clean": "{label}: lido, nada a relatar",
        "diag_problem": "Recusado: {text}",
        "diag_note": "Nota: {text}",
    },
}

LANGUAGES = tuple(CATALOG)


class UnknownLanguage(ValueError):
    """A language code the catalog does not have."""


_current = DEFAULT


def check_code(code: str) -> str:
    if code not in CATALOG:
        raise UnknownLanguage("unknown language %r; accepted: %s"
                              % (code, ", ".join(LANGUAGES)))
    return code


def chosen(flag=None, environ=None) -> str:
    """The language a run asked for: the flag, then the variable, then DEFAULT."""
    environ = os.environ if environ is None else environ
    return check_code(flag or environ.get(ENV) or DEFAULT)


def set_language(code: str) -> None:
    global _current
    _current = check_code(code)


def language() -> str:
    return _current


def tr(key: str, **fields) -> str:
    """The text of *key* in the language in force, with *fields* filled in."""
    return CATALOG[_current][key].format(**fields)


def fields_of(text: str) -> set:
    """The `{names}` a catalog entry fills in."""
    return {name for _, name, _, _ in string.Formatter().parse(text) if name is not None}


def problems(catalog=None) -> list:
    """Every way the languages of *catalog* differ: a key one has and another
    lacks, or one entry with other fields than the default's."""
    catalog = CATALOG if catalog is None else catalog
    out = []
    if DEFAULT not in catalog:
        return ["no %s catalog" % DEFAULT]
    base = catalog[DEFAULT]
    for code, entries in catalog.items():
        if code == DEFAULT:
            continue
        for key in sorted(set(base) - set(entries)):
            out.append("%s lacks %r" % (code, key))
        for key in sorted(set(entries) - set(base)):
            out.append("%s has %r, which %s lacks" % (code, key, DEFAULT))
        for key in sorted(set(base) & set(entries)):
            mine, theirs = fields_of(entries[key]), fields_of(base[key])
            if mine != theirs:
                out.append("%s %r fills %s, %s fills %s"
                           % (code, key, sorted(mine), DEFAULT, sorted(theirs)))
    return out


def self_check() -> list:
    """Failures of this module, as sentences; empty when it holds."""
    out = ["catalog: %s" % p for p in problems()]
    if set(NAMES) != set(CATALOG):
        out.append("NAMES covers %s, the catalog %s" % (sorted(NAMES), sorted(CATALOG)))
    if DEFAULT != "en-US":
        out.append("the default is %r, not en-US" % DEFAULT)
    planted = {DEFAULT: {"a": "{x}", "b": "y"}, "pt-BR": {"a": "{z}"}}
    if len(problems(planted)) != 2:
        out.append("a planted catalog with one missing key and one renamed field "
                   "gives %r" % problems(planted))
    try:
        chosen("xx-XX", {})
        out.append("an unknown code was accepted")
    except UnknownLanguage:
        pass
    if chosen(None, {}) != DEFAULT or chosen(None, {ENV: "pt-BR"}) != "pt-BR" \
            or chosen("en-US", {ENV: "pt-BR"}) != "en-US":
        out.append("the order flag, variable, default does not hold")
    return out


if __name__ == "__main__":
    bad = self_check()
    for line in bad:
        print("FAIL  %s" % line)
    print("i18n: %d failure(s)" % len(bad))
    raise SystemExit(1 if bad else 0)
