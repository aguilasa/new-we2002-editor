#!/usr/bin/env python3
"""Port carica_dabin() and OnWriteCD() from the legacy MFC dialog into the core.

Together these two functions are ~1360 lines of dense offset arithmetic. They
are the heart of the format handling and the part where a typo is both easiest
to make and hardest to notice -- a wrong seek shows up as one corrupted team
several megabytes into the image.

So they are not retyped. This script lifts the bodies verbatim and applies a
fixed, auditable list of textual substitutions (MFC types -> core types, MFC
calls -> CdImage calls, table names -> the generated constants). Anything it
does not recognise is left alone and will fail to compile, which is the point:
silence would be worse.

Run once; the generated Database.cpp is committed. Re-run and diff after any
change to the legacy source.

    python3 tools/port_database.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import glossary  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
LEGACY = ROOT / "legacy" / "mfc" / "edDlg.cpp"
OUT = ROOT / "src" / "core" / "Database.cpp"

# (pattern, replacement, human-readable reason) applied in order.
SUBS: list[tuple[str, str, str]] = [
    # --- file handle: CFile -> CdImage -------------------------------------
    (r"\bCFile fil_ctrl;", "CdImage fil_ctrl;", "CFile -> CdImage"),
    (
        r"fil_ctrl\.Open\(fil_nomeCD,\s*CFile::modeRead\s*\|\s*CFile::typeBinary\)\s*==\s*0",
        "!fil_ctrl.OpenRead(image)",
        "Open(read) -> OpenRead",
    ),
    (
        r"fil_ctrl\.Open\(fil_nomeCD,\s*CFile::modeReadWrite\s*\|\s*CFile::typeBinary\)\s*==\s*0",
        "!fil_ctrl.OpenReadWrite(image)",
        "Open(rw) -> OpenReadWrite",
    ),
    # The [^,\n] is load-bearing. With plain [^,] the class also matches a
    # newline, so after the begin-rule had rewritten
    #     fil_ctrl.Seek(OFS_COSTI_NAZ, CFile::begin);
    #         fil_ctrl.Seek(2,CFile::current);
    # the current-rule matched from the FIRST Seek across the line break all
    # the way to the second one's ", CFile::current)", swapping the two: the
    # absolute seek became relative and the relative one absolute. That put
    # every Master League transfer cost at the wrong file position. It still
    # compiled, so only the golden test against ed.exe caught it.
    (
        r"fil_ctrl\.Seek\(([^,\n]+),\s*CFile::begin\)",
        r"fil_ctrl.Seek(\1)",
        "Seek(begin) -> Seek",
    ),
    (
        r"fil_ctrl\.Seek\(([^,\n]+),\s*CFile::current\)",
        r"fil_ctrl.SeekCurrent(\1)",
        "Seek(current) -> SeekCurrent",
    ),
    # The tail of OnWriteCD dumps every player's SoFIFA URL to a sidecar text
    # file next to the image. CString::Replace substitutes *all* occurrences,
    # which UrlSidecarPath reproduces.
    (
        r"CString fil_nomeURL;\s*\n\s*fil_nomeURL = fil_nomeCD;\s*\n\s*"
        r"fil_nomeURL\.Replace\(\s*\"\.bin\",\s*\"_url\.txt\"\s*\);\s*\n\s*"
        r"ofstream fil_url;\s*\n\s*fil_url\.open \(fil_nomeURL, ios::trunc \);",
        "\tstd::ofstream fil_url;\n"
        "\tfil_url.open(UrlSidecarPath(image), std::ios::trunc);",
        "URL sidecar path",
    ),
    # --- reporting ---------------------------------------------------------
    (r'AfxMessageBox\("([^"]*)"\)', r'Report(report, "\1")', "AfxMessageBox -> injected reporter"),
    # --- text codec --------------------------------------------------------
    (r"\bkanjitoascii\(", "KanjiToAscii(", "renamed"),
    (r"\basciitokanji\(", "AsciiToKanji(", "renamed"),
    (r"\btrovaIDml\(", "TrovaIdMl(", "renamed"),
    # --- generated tables --------------------------------------------------
    (r"\blun_nomi_add1\b", "LUN_NOMI_ADD1", "table"),
    (r"\blun_nomi_add2\b", "LUN_NOMI_ADD2", "table"),
    (r"\blun_nomi_min\b", "LUN_NOMI_MIN", "table"),
    (r"\blun_nomik\b", "LUN_NOMIK", "table"),
    (r"\blun_nomi([1-6])\b", r"LUN_NOMI\1", "table"),
    (r"\bstart_link\b", "START_LINK", "table"),
    (r"\bnc_naz_seq\b", "NC_NAZ_SEQ", "table"),
    (r"\bnc_naz_qt\b", "NC_NAZ_QT", "table"),
    (r"\bnomi_squadre\b", "TEAM_NAMES", "table"),
    # Negative lookbehind: `ruoli` is BOTH a file-scope table and a member of
    # tattica. Without this guard `tattpred[i].ruoli` becomes
    # `tattpred[i].ROLE_NAMES` and the build breaks -- which it did.
    (r"(?<!\.)\bruoli\b", "ROLE_NAMES", "table"),
    # --- counts ------------------------------------------------------------
    (r"\bGIOCATORI_NC\b", "PLAYERS_NC", "constant"),
    (r"\bGIOCATORI_NAZALL\b", "PLAYERS_NAZALL", "constant"),
    (r"\bGIOCATORI_TOT\b", "PLAYERS_TOTAL", "constant"),
    (r"\bSQUADRE_NAZ\b", "TEAMS_NATIONAL", "constant"),
    (r"\bSQUADRE_ALLS\b", "TEAMS_ALLSTAR", "constant"),
    (r"\bSQUADRE_ML\b", "TEAMS_ML", "constant"),
    # --- misc --------------------------------------------------------------
    (r"(?<!std::)\bendl\b", "std::endl", "qualify endl"),
    (r"(?<!std::)\bceil\(", "std::ceil(", "qualify ceil"),
    (r"\bnomiallstar\(\)", "NomiAllStar()", "renamed"),
    # Every NULL in these two functions terminates a char buffer -- there is
    # not one pointer among them. `= NULL` on a char is the same value as
    # `= 0`, but it warns under -Wconversion-null.
    (r"=\s*NULL;", "= 0;", "NULL -> 0 for char terminators"),
    # Falling from `case 52:` into `default:` is deliberate: those three
    # entries skip 32 bytes and then take the default read. Mark it so the
    # intent is explicit and -Wimplicit-fallthrough stays quiet.
    (
        r"(fil_ctrl\.(?:Seek|Write|Read)Current\(32\);|fil_ctrl\.SeekCurrent\(32\);)(\s*\n\s*)default\s*:",
        r"\1\2[[fallthrough]];\2default:",
        "explicit [[fallthrough]]",
    ),
]

# Constructs that must NOT survive into the core. If any is still present after
# substitution the script fails rather than emitting code that will not build.
FORBIDDEN = [
    (r"\bCFile\b", "MFC file class"),
    (r"\bCString\b", "MFC string"),
    (r"\bAfxMessageBox\b", "MFC message box"),
    (r"\bfil_nomeCD\b", "global filename"),
    (r"\b_itoa\b", "MSVC-only CRT"),
    (r"\bCEdDlg::", "dialog method qualifier"),
]


def grab(lines: list[str], start_pat: str) -> str:
    """Extract a whole function definition, braces balanced."""
    pat = re.compile(start_pat)
    for i, line in enumerate(lines):
        if pat.match(line):
            j = i
            out = [lines[i]]
            while "{" not in lines[j]:
                j += 1
                out.append(lines[j])
            depth = lines[j].count("{") - lines[j].count("}")
            while depth != 0:
                j += 1
                depth += lines[j].count("{") - lines[j].count("}")
                out.append(lines[j])
            return "\n".join(out)
    raise SystemExit(f"funcao nao encontrada: {start_pat}")


def apply_subs(text: str) -> tuple[str, dict[str, int]]:
    counts: dict[str, int] = {}
    for pattern, repl, reason in SUBS:
        text, n = re.subn(pattern, repl, text)
        if n:
            counts[reason] = counts.get(reason, 0) + n
    return text, counts


def check_forbidden(text: str, where: str) -> list[str]:
    problems = []
    for pattern, what in FORBIDDEN:
        hits = re.findall(pattern, text)
        if hits:
            problems.append(f"{where}: {len(hits)}x {what} ({pattern})")
    return problems


def check_seeks(before: str, after: str, where: str) -> list[str]:
    """Every seek must keep the direction it had in the legacy source.

    FORBIDDEN cannot see this: a rule that turns an absolute seek into a
    relative one and vice versa leaves no MFC token behind, and the result
    compiles. It happened -- see the comment on the Seek rules above -- and
    cost a corrupted cost table that only the ed.exe oracle exposed. So count
    the two directions on each side and insist they match.
    """
    problems = []
    for token, produced, what in (
        ("CFile::begin", r"fil_ctrl\.Seek\(", "absolute"),
        ("CFile::current", r"fil_ctrl\.SeekCurrent\(", "relative"),
    ):
        want = len(re.findall(rf"fil_ctrl\.Seek\([^,\n]+,\s*{re.escape(token)}\)", before))
        got = len(re.findall(produced, after))
        if want != got:
            problems.append(
                f"{where}: {want} {what} seek(s) in the legacy source but "
                f"{got} in the output"
            )
    return problems


HEADER = '''// GENERATED by tools/port_database.py -- do not edit by hand.
//
// Load() is carica_dabin() and Save() is OnWriteCD(), lifted verbatim from
// legacy/mfc/edDlg.cpp and mechanically rewritten off MFC. The seeks, the
// read lengths and the loop bounds are untouched: they encode the CD image
// layout, including the manual jumps over MODE2/2352 sector headers.
//
// Re-generate with:  python3 tools/port_database.py

#include "we2002/Database.hpp"

#include <cmath>
#include <cstring>
#include <fstream>
#include <string>

#include "we2002/CdImage.hpp"
#include "we2002/Offsets.hpp"
#include "we2002/Tables.hpp"
#include "we2002/TextCodec.hpp"

namespace we2002 {
namespace {

void Report(const Reporter& report, const char* message) {
    if (report) {
        report(message);
    }
}

/// Path of the "<image>_url.txt" sidecar holding one SoFIFA URL per player.
///
/// The original built this with CString::Replace(".bin", "_url.txt"), which
/// replaces *every* occurrence rather than just the extension. Reproduced as
/// is: a directory called "foo.bin" would be rewritten too, and changing that
/// would change which file the editor reads back.
std::filesystem::path UrlSidecarPath(const std::filesystem::path& image) {
    std::string s = image.string();
    const std::string from = ".bin";
    const std::string to = "_url.txt";
    for (std::size_t at = s.find(from); at != std::string::npos;
         at = s.find(from, at + to.size())) {
        s.replace(at, from.size(), to);
    }
    return {s};
}

}  // namespace

Database::Database() = default;

int TrovaIdMl(const unsigned char* lk) {
    // From legacy/mfc/edDlg.cpp:3430, minus one dead expression statement that
    // read a player name and threw it away, and plus two bounds checks the
    // original did not have.
    //
    // A link is (team code, position). On a real image the team code is 0..119
    // and the result lands inside players[], so neither check ever fires --
    // which is what the golden tests demonstrate. On anything else, which is to
    // say on whatever file a user opens by mistake, the original read past the
    // end of START_LINK's 120 entries and then indexed players[] with the
    // garbage that came out. The first symptom was a crash before the window
    // even appeared, with nothing on stderr.
    //
    // Out of range resolves to player 0 rather than to nothing, because every
    // caller uses the result as an index immediately and none of them has an
    // error path to take.
    const unsigned int team = lk[0];
    const unsigned int slot = lk[1];
    int r = 0;
    if (slot > 22) {
        if (team >= static_cast<unsigned int>(START_LINK_COUNT)) {
            return 0;
        }
        r = static_cast<int>(slot) + START_LINK[team] - 23;
    } else {
        r = static_cast<int>((team * 23) + slot) + PLAYERS_NC;
    }
    if (r < 0 || r >= PLAYERS_TOTAL) {
        return 0;
    }
    return r;
}

void Database::NomiAllStar() {
    // Verbatim from legacy/mfc/edDlg.cpp:8418.
    for (int i = 0; i < 23; i++) {
        // euro
        std::strcpy(gioc[462 + (54 * 23) + i].nome, gioc[TrovaIdMl(&link_euroas[i * 2])].nome);
        // world
        std::strcpy(gioc[462 + (55 * 23) + i].nome, gioc[TrovaIdMl(&link_worldas[i * 2])].nome);
    }
}

'''


def main() -> int:
    lines = LEGACY.read_text(encoding="utf-8").split("\n")

    load = grab(lines, r"^void CEdDlg::carica_dabin")
    save = grab(lines, r"^void CEdDlg::OnWriteCD")
    cost = grab(lines, r"^int CalcolaCostoGiocatore")
    print(f"extraido: carica_dabin={load.count(chr(10))+1} linhas, "
          f"OnWriteCD={save.count(chr(10))+1} linhas, "
          f"CalcolaCostoGiocatore={cost.count(chr(10))+1} linhas")

    raw_load, raw_save, raw_cost = load, save, cost

    load, c1 = apply_subs(load)
    save, c2 = apply_subs(save)
    cost, c3 = apply_subs(cost)
    # The cost formula reads the player pool, which is now a member rather
    # than a global.
    cost = cost.replace("int CalcolaCostoGiocatore(int i)",
                        "int CalcolaCostoGiocatore(const Database& db, int i)")
    cost = re.sub(r"\bgioc\[", "db.gioc[", cost)

    load = load.replace(
        "void CEdDlg::carica_dabin()",
        "bool Database::Load(const std::filesystem::path& image, const Reporter& report)",
    )
    save = save.replace(
        "void CEdDlg::OnWriteCD()",
        "bool Database::Save(const std::filesystem::path& image, const Reporter& report)",
    )
    # The originals `return;` on failure and fall off the end on success.
    load = load.replace("\t\treturn;", "\t\treturn false;")
    save = save.replace("\t\treturn;", "\t\treturn false;")
    load = load.rstrip()[:-1].rstrip() + "\n\treturn true;\n}"
    save = save.rstrip()[:-1].rstrip() + "\n\treturn true;\n}"

    body = HEADER + load + "\n\n" + save + "\n\n" + cost + "\n\n}  // namespace we2002\n"

    problems = (check_forbidden(load, "Load") + check_forbidden(save, "Save")
                + check_forbidden(cost, "Cost")
                + check_seeks(raw_load, load, "Load")
                + check_seeks(raw_save, save, "Save")
                + check_seeks(raw_cost, cost, "Cost"))
    if problems:
        print("\nSUBSTITUICAO INCORRETA -- corrija SUBS antes de usar:", file=sys.stderr)
        for p in problems:
            print("  " + p, file=sys.stderr)
        return 1

    # Phase 3.5. Deliberately last: the guards above are written against the
    # legacy spellings, and running them on renamed text would mean keeping
    # two versions of every pattern.
    body, renames, comments = glossary.rename(body)
    leftover = sorted(set(glossary.LEFTOVER.findall(body)))
    if leftover:
        print("\nNOME EM ITALIANO SOBROU:", ", ".join(leftover), file=sys.stderr)
        return 1

    OUT.write_text(body, encoding="utf-8")

    merged: dict[str, int] = {}
    for c in (c1, c2, c3):
        for k, v in c.items():
            merged[k] = merged.get(k, 0) + v
    merged["glossario: identificadores"] = renames
    merged["glossario: comentarios"] = comments
    print("substituicoes:")
    for k, v in sorted(merged.items(), key=lambda t: -t[1]):
        print(f"  {v:4d}  {k}")
    print(f"\n{OUT.relative_to(ROOT)}: {body.count(chr(10))+1} linhas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
