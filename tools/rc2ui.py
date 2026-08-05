#!/usr/bin/env python3
"""Convert the six dialogs of legacy/mfc/ed.rc into Qt .ui files (phase 4).

434 controls placed by hand at absolute coordinates. Retyping them is out of
the question, and so is redesigning the layout: the point of this phase is a
transcription faithful enough that the Qt window can be put next to a
screenshot of ed.exe under Wine and compared.

So the geometry is absolute here too. Qt layouts come later, if ever -- the
original has no resizing behaviour to preserve, and matching it pixel for
pixel is what makes the port reviewable.

Two outputs per run:

  src/app/ui/*.ui            the forms, consumed by uic
  src/app/ui/controls.json   everything the .ui cannot express

The manifest exists because Win32 styles carry information Qt has no property
for -- ES_NUMBER and ES_UPPERCASE are validators, not widget flags. Phase 5
reads it rather than going back to the .rc.

Widget names went through glossary.UI_CONTROLS in phase 5.5. Phase 4 had kept
ed.rc's Italian symbols so the forms stayed diffable against ed.rc while the
handlers were ported; that job is done. Every manifest entry still carries the
original symbol as `id`, so grepping a name across both trees still works.

    python3 tools/rc2ui.py
    python3 tools/rc2ui.py --check    # regenerate into memory and diff
"""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
import glossary  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RC = ROOT / "legacy" / "mfc" / "ed.rc"
OUT = ROOT / "src" / "app" / "ui"

# ed.rc is ISO-8859-1 and stays that way -- see CLAUDE.md. It is decoded here
# and the .ui files are written as UTF-8, which is what Qt expects.
RC_ENCODING = "iso-8859-1"

# Dialog units are not pixels. MapDialogRect scales x by baseX/4 and y by
# baseY/8, where the base units come from the dialog font. All six dialogs are
# FONT 8 "MS Sans Serif", whose average character cell is 6 x 13. That is how
# IDD_ED_DIALOG's 718 x 337 DLU becomes 1077 x 548 px, which matches what Wine
# renders.
BASE_X = 6
BASE_Y = 13


def dlu_x(v: int) -> int:
    return v * BASE_X // 4


def dlu_y(v: int) -> int:
    return v * BASE_Y // 8


# A COMBOBOX's height in the .rc is the height of the *dropped-down list*, not
# of the control. Win32 draws the closed control one text line tall and uses
# the rest only while the list is open. Taken literally, CMB_NSQUADRE's 64 DLU
# becomes a 104 px box that swallows the DEFAULT TACTICS group behind it.
#
# 12 DLU is what the closed control measures in ed.exe under Wine, and it is
# also the height every EDITTEXT in this .rc uses. The .rc value is not lost:
# controls.json keeps it as dropdown_dlu.
COMBO_HEIGHT_DLU = 12


# The .rc identifies dialogs by resource symbol; the generated C++ class takes
# an English name. Controls are renamed too since phase 5.5 -- see
# glossary.UI_CONTROLS.
DIALOG_CLASS = {
    "IDD_ED_DIALOG": "MainDialog",
    "DLG_SELECT_GIOC": "PlayerSelectDialog",
    "DLG_CARATT": "PlayerSkillsDialog",
    "DLG_GRAF": "FlagKitPreviewDialog",
    "DLG_PTATTICHE": "DefaultTacticsDialog",
    "DLG_EDITOPT": "EditOptionsDialog",
}

# Statement keyword -> (Qt class, does the first argument hold a caption?)
SIMPLE = {
    "LTEXT": ("QLabel", True),
    "CTEXT": ("QLabel", True),
    "RTEXT": ("QLabel", True),
    "GROUPBOX": ("QGroupBox", True),
    "PUSHBUTTON": ("QPushButton", True),
    "DEFPUSHBUTTON": ("QPushButton", True),
    "EDITTEXT": ("QLineEdit", False),
    "COMBOBOX": ("QComboBox", False),
    "LISTBOX": ("QListWidget", False),
}

# Every statement keyword that can open a control in a dialog body. Anything
# not listed here is treated as a continuation of the statement above.
STATEMENT_KEYWORDS = set(SIMPLE) | {"CONTROL", "SCROLLBAR", "ICON", "STATE3",
                                    "AUTO3STATE", "CHECKBOX", "RADIOBUTTON"}

TEXT_ALIGN = {
    "LTEXT": "Qt::AlignLeft|Qt::AlignVCenter",
    "CTEXT": "Qt::AlignHCenter|Qt::AlignVCenter",
    "RTEXT": "Qt::AlignRight|Qt::AlignVCenter",
}

# Win32 button styles inside a CONTROL statement -> Qt class.
BUTTON_STYLE = {
    "BS_AUTOCHECKBOX": "QCheckBox",
    "BS_CHECKBOX": "QCheckBox",
    "BS_AUTORADIOBUTTON": "QRadioButton",
    "BS_RADIOBUTTON": "QRadioButton",
    "BS_PUSHBUTTON": "QPushButton",
    "BS_GROUPBOX": "QGroupBox",
}


class Control:
    def __init__(self, kind, text, ident, cls, style, rect):
        self.kind = kind          # the .rc keyword
        self.text = text          # caption, or None
        self.ident = ident        # resource symbol
        self.cls = cls            # Qt class
        self.style = style        # raw style string from the .rc
        self.x, self.y, self.w, self.h = rect

    def has(self, flag: str) -> bool:
        return re.search(rf"\b{flag}\b", self.style) is not None

    def negates(self, flag: str) -> bool:
        return re.search(rf"\bNOT\s+{flag}\b", self.style) is not None


def split_args(s: str) -> list[str]:
    """Split on commas that are not inside a quoted string."""
    out, buf, in_str = [], [], False
    i = 0
    while i < len(s):
        c = s[i]
        if c == '"':
            # "" inside a string is an escaped quote in .rc.
            if in_str and i + 1 < len(s) and s[i + 1] == '"':
                buf.append('""')
                i += 2
                continue
            in_str = not in_str
            buf.append(c)
        elif c == "," and not in_str:
            out.append("".join(buf).strip())
            buf = []
        else:
            buf.append(c)
        i += 1
    out.append("".join(buf).strip())
    return out


def unquote(s: str) -> str:
    s = s.strip()
    if s.startswith('"') and s.endswith('"'):
        s = s[1:-1].replace('""', '"')
    return s


def strip_comment(line: str) -> str:
    """Drop a trailing // comment, ignoring // inside a quoted string.

    The author commented out whole controls in place, so this has to run
    before the continuation lines are folded together -- otherwise a disabled
    PUSHBUTTON ends up glued onto the coordinates of the live one above it.
    """
    in_str = False
    for i, c in enumerate(line):
        if c == '"':
            in_str = not in_str
        elif c == "/" and not in_str and line[i:i + 2] == "//":
            return line[:i].rstrip()
    return line


def join_statements(body: list[str]) -> list[str]:
    """Fold continuation lines back into one statement each.

    A statement runs from a line starting with a keyword until the next such
    line. 192 of the 393 controls wrap, sometimes mid-style -- one of them
    splits "NOT WS_VISIBLE" across the break -- so this has to happen before
    anything is parsed.
    """
    statements: list[str] = []
    for raw in body:
        line = strip_comment(raw).strip()
        if not line:
            continue
        # Indentation cannot be the signal -- one PUSHBUTTON is indented with
        # a tab and the rest with four spaces. A statement is recognised by
        # its keyword instead; a wrapped line always resumes inside a style
        # expression and so starts with WS_/BS_/ES_/CBS_/LBS_/NOT.
        head = line.split(None, 1)[0]
        if head in STATEMENT_KEYWORDS or not statements:
            statements.append(line)
        else:
            statements[-1] += " " + line
    return [s for s in statements if s]


def parse_control(statement: str) -> Control | None:
    m = re.match(r"^([A-Z][A-Z0-9_]*)\s+(.*)$", statement, re.S)
    if not m:
        return None
    kind, rest = m.group(1), m.group(2)
    args = split_args(rest)

    if kind == "CONTROL":
        # CONTROL "text", id, "class", style, x, y, w, h [, exstyle]
        if len(args) < 8:
            raise SystemExit(f"CONTROL malformado: {statement}")
        text, ident, win_class, style = (
            unquote(args[0]), args[1], unquote(args[2]), args[3])
        rect = [int(a) for a in args[4:8]]
        if win_class != "Button":
            raise SystemExit(
                f"CONTROL de classe {win_class!r} nao mapeada: {statement}")
        cls = "QPushButton"
        for flag, qt in BUTTON_STYLE.items():
            if re.search(rf"\b{flag}\b", style):
                cls = qt
                break
        return Control(kind, text, ident, cls, style, rect)

    if kind not in SIMPLE:
        return None

    cls, has_text = SIMPLE[kind]
    if has_text:
        # "text", id, x, y, w, h [, style [, exstyle]]
        text, ident = unquote(args[0]), args[1]
        rect = [int(a) for a in args[2:6]]
        style = " ".join(args[6:])
    else:
        # id, x, y, w, h [, style [, exstyle]]
        text, ident = None, args[0]
        rect = [int(a) for a in args[1:5]]
        style = " ".join(args[5:])
    return Control(kind, text, ident, cls, style, rect)


def parse_dialogs(text: str) -> list[dict]:
    lines = text.split("\n")
    dialogs = []
    i = 0
    while i < len(lines):
        m = re.match(r"^(\w+)\s+(DIALOGEX|DIALOG)\s+(-?\d+),\s*(-?\d+),"
                     r"\s*(\d+),\s*(\d+)\s*$", lines[i])
        if not m:
            i += 1
            continue
        name = m.group(1)
        w, h = int(m.group(5)), int(m.group(6))
        caption, font = "", ("MS Sans Serif", 8)
        j = i + 1
        while lines[j].strip() != "BEGIN":
            line = lines[j].strip()
            if line.startswith("CAPTION"):
                caption = unquote(line[len("CAPTION"):].strip())
            elif line.startswith("FONT"):
                fm = re.match(r'FONT\s+(\d+),\s*"([^"]*)"', line)
                if fm:
                    font = (fm.group(2), int(fm.group(1)))
            j += 1
        body = []
        j += 1
        while lines[j].strip() != "END":
            body.append(lines[j])
            j += 1
        dialogs.append({
            "name": name, "width": w, "height": h,
            "caption": caption, "font": font,
            "statements": join_statements(body),
        })
        i = j
    return dialogs


def drawn_height(c: Control) -> int:
    """Height of the control as drawn, in DLU. See COMBO_HEIGHT_DLU."""
    return COMBO_HEIGHT_DLU if c.kind == "COMBOBOX" else c.h


def widget_xml(c: Control, name: str, indent: str) -> list[str]:
    out = [f'{indent}<widget class="{c.cls}" name="{name}">']
    out.append(f"{indent} <property name=\"geometry\">")
    out.append(f"{indent}  <rect>")
    out.append(f"{indent}   <x>{dlu_x(c.x)}</x>")
    out.append(f"{indent}   <y>{dlu_y(c.y)}</y>")
    out.append(f"{indent}   <width>{dlu_x(c.w)}</width>")
    out.append(f"{indent}   <height>{dlu_y(drawn_height(c))}</height>")
    out.append(f"{indent}  </rect>")
    out.append(f"{indent} </property>")

    if c.text is not None:
        # A group box's caption is its title, not its text; uic happily emits
        # setText() on a QGroupBox and the compiler is the one that complains.
        prop = "title" if c.cls == "QGroupBox" else "text"
        out.append(f"{indent} <property name=\"{prop}\">")
        out.append(f"{indent}  <string>{escape(c.text)}</string>")
        out.append(f"{indent} </property>")

    if c.kind in TEXT_ALIGN:
        out.append(f"{indent} <property name=\"alignment\">")
        out.append(f"{indent}  <set>{TEXT_ALIGN[c.kind]}</set>")
        out.append(f"{indent} </property>")

    if c.kind == "EDITTEXT" and c.has("ES_RIGHT"):
        out.append(f"{indent} <property name=\"alignment\">")
        out.append(f"{indent}  <set>Qt::AlignRight|Qt::AlignVCenter</set>")
        out.append(f"{indent} </property>")

    if c.kind == "EDITTEXT" and c.has("ES_READONLY"):
        out.append(f"{indent} <property name=\"readOnly\">")
        out.append(f"{indent}  <bool>true</bool>")
        out.append(f"{indent} </property>")

    if c.kind == "DEFPUSHBUTTON":
        out.append(f"{indent} <property name=\"default\">")
        out.append(f"{indent}  <bool>true</bool>")
        out.append(f"{indent} </property>")

    if c.kind == "PUSHBUTTON":
        # Inside a QDialog, Qt makes every push button autoDefault, so Return
        # clicks whichever one happens to come first in the tab order. Four of
        # the six dialogs here -- including the main one, with 86 buttons --
        # declare no DEFPUSHBUTTON at all, so that would be an arbitrary
        # action, and one of the candidates applies a preset formation over the
        # selected team.
        #
        # A plain PUSHBUTTON in a .rc is not a default button. Saying so keeps
        # Return from doing anything, and leaves DEFPUSHBUTTON as the only way
        # to be one -- which is what the resource script means.
        out.append(f"{indent} <property name=\"autoDefault\">")
        out.append(f"{indent}  <bool>false</bool>")
        out.append(f"{indent} </property>")

    if c.cls == "QGroupBox":
        if c.has("BS_CENTER"):
            out.append(f"{indent} <property name=\"alignment\">")
            out.append(f"{indent}  <set>Qt::AlignHCenter|Qt::AlignTop</set>")
            out.append(f"{indent} </property>")

    if c.negates("WS_VISIBLE"):
        out.append(f"{indent} <property name=\"visible\">")
        out.append(f"{indent}  <bool>false</bool>")
        out.append(f"{indent} </property>")

    if c.negates("WS_TABSTOP"):
        out.append(f"{indent} <property name=\"focusPolicy\">")
        out.append(f"{indent}  <enum>Qt::NoFocus</enum>")
        out.append(f"{indent} </property>")

    if c.has("WS_DISABLED"):
        out.append(f"{indent} <property name=\"enabled\">")
        out.append(f"{indent}  <bool>false</bool>")
        out.append(f"{indent} </property>")

    out.append(f"{indent}</widget>")
    return out


def build_ui(dialog: dict) -> tuple[str, list[dict]]:
    name = dialog["name"]
    cls = DIALOG_CLASS.get(name, name)
    family, size = dialog["font"]

    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    # No "--" in here: XML forbids it inside a comment, and uic rejects the
    # file outright rather than skipping the comment.
    xml.append("<!-- GENERATED by tools/rc2ui.py from legacy/mfc/ed.rc"
               f" ({name}). Do not edit by hand. -->")
    xml.append('<ui version="4.0">')
    xml.append(f" <class>{cls}</class>")
    xml.append(f' <widget class="QDialog" name="{cls}">')
    xml.append('  <property name="geometry">')
    xml.append("   <rect>")
    xml.append("    <x>0</x>")
    xml.append("    <y>0</y>")
    xml.append(f"    <width>{dlu_x(dialog['width'])}</width>")
    xml.append(f"    <height>{dlu_y(dialog['height'])}</height>")
    xml.append("   </rect>")
    xml.append("  </property>")
    xml.append('  <property name="windowTitle">')
    xml.append(f"   <string>{escape(dialog['caption'])}</string>")
    xml.append("  </property>")
    xml.append('  <property name="font">')
    xml.append("   <font>")
    xml.append(f"    <family>{escape(family)}</family>")
    xml.append(f"    <pointsize>{size}</pointsize>")
    xml.append("   </font>")
    xml.append("  </property>")

    manifest = []
    anonymous = 0
    used: set[str] = set()
    for statement in dialog["statements"]:
        c = parse_control(statement)
        if c is None:
            raise SystemExit(f"{name}: statement nao reconhecido: {statement}")

        # IDC_STATIC is -1 and repeats; decorative widgets get a serial name.
        if c.ident == "IDC_STATIC":
            anonymous += 1
            obj = f"static_{anonymous}"
        else:
            obj = glossary.UI_CONTROLS.get(c.ident, c.ident)
            if obj in used:
                raise SystemExit(f"{name}: id repetido: {obj} ({c.ident})")
            used.add(obj)

        xml += widget_xml(c, obj, "  ")
        entry = {
            "object": obj,
            "id": c.ident,
            "rc": c.kind,
            "qt": c.cls,
            "text": c.text,
            "style": " ".join(c.style.split()),
            "dlu": [c.x, c.y, c.w, drawn_height(c)],
            "px": [dlu_x(c.x), dlu_y(c.y), dlu_x(c.w), dlu_y(drawn_height(c))],
        }
        if c.kind == "COMBOBOX":
            entry["dropdown_dlu"] = c.h
        manifest.append(entry)

    xml.append(" </widget>")
    xml.append(" <resources/>")
    xml.append(" <connections/>")
    xml.append("</ui>")
    return "\n".join(xml) + "\n", manifest


def generate() -> dict[str, str]:
    text = RC.read_text(encoding=RC_ENCODING)
    dialogs = parse_dialogs(text)
    if len(dialogs) != 6:
        raise SystemExit(f"esperados 6 dialogos, achados {len(dialogs)}")

    files: dict[str, str] = {}
    manifest: dict[str, dict] = {}
    for d in dialogs:
        ui, controls = build_ui(d)
        cls = DIALOG_CLASS.get(d["name"], d["name"])
        # uic refuses a malformed file outright, and its error message points
        # at a line number rather than at the generator. Parsing here means a
        # bad emit is caught without Qt installed -- which is how the "--"
        # inside the generated XML comment was found.
        try:
            ET.fromstring(ui)
        except ET.ParseError as exc:
            raise SystemExit(f"{cls}.ui: XML invalido: {exc}") from exc
        files[f"{cls}.ui"] = ui
        # Keyed by the Qt class, not by the .rc symbol: three of the six
        # symbols are Italian, and the manifest is read by the app.
        manifest[cls] = {
            "id": d["name"],
            "caption": d["caption"],
            "dlu": [d["width"], d["height"]],
            "px": [dlu_x(d["width"]), dlu_y(d["height"])],
            "controls": controls,
        }

    files["controls.json"] = json.dumps(
        {
            "source": "legacy/mfc/ed.rc",
            "generator": "tools/rc2ui.py",
            "base_units": {"x": BASE_X, "y": BASE_Y},
            "dialogs": manifest,
        },
        indent=2,
        ensure_ascii=False,
    ) + "\n"
    return files


def main(argv: list[str]) -> int:
    files = generate()

    if argv and argv[0] == "--check":
        stale = []
        for name, content in files.items():
            path = OUT / name
            if not path.exists():
                stale.append(f"{name}: nao existe")
            elif path.read_text(encoding="utf-8") != content:
                stale.append(f"{name}: desatualizado")
        if stale:
            print("src/app/ui nao corresponde a legacy/mfc/ed.rc:",
                  file=sys.stderr)
            for s in stale:
                print("  " + s, file=sys.stderr)
            print("rode: python3 tools/rc2ui.py", file=sys.stderr)
            return 1
        print(f"{len(files)} arquivos em dia com ed.rc")
        return 0

    OUT.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        # newline="\n": these files are committed and compared byte for byte by
        # `ctest -R ui_forms`; Python would write CRLF on Windows.
        (OUT / name).write_text(content, encoding="utf-8", newline="\n")
        widgets = content.count('<widget class="') - 1
        if name.endswith(".ui"):
            print(f"  {name}: {widgets} controles")
    print(f"\n{len(files)} arquivos em {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
