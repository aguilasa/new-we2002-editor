"""The pad buttons `press_button` accepts, and the one place that spells them.

The fork's server declares the button as an enum in the input schema of
`press_button` (and of `release_button`), sixteen DualShock names in this
exact spelling. Read on 2026-10-22 out of the tool schema compiled into the
fork's `duckstation-qt` (`strings -a bin/duckstation-qt | grep
'"name":"press_button"'`), and the same list the callers already sent.

`canonical(name)` takes any capitalisation and answers the server's own
spelling, or refuses with the list. It replaces the three copies of the old
rule, `button.capitalize()`, which agreed with the schema for every valid
name and passed a typo straight to the server, where it came back as a
`ToolError` naming nothing useful.
"""

# lineage: tools/pes2/pad.py BUTTONS (lower case) and the capitalize() rule
# of tools/pes2/mcp_drive.py, tools/pes2/pad.py and tools/pes2/who_writes.py.

BUTTONS = ("Cross", "Circle", "Square", "Triangle", "Up", "Down", "Left",
           "Right", "L1", "L2", "R1", "R2", "Start", "Select", "L3", "R3")
"""The sixteen names of the `press_button` enum, in the schema's order."""

_BY_FOLDED = {name.casefold(): name for name in BUTTONS}


class UnknownButton(ValueError):
    """A name that is none of `BUTTONS`, in any capitalisation."""


def canonical(name):
    """The server's spelling of `name`, matched without regard to case.

    `canonical("down")`, `canonical("DOWN")` and `canonical("Down")` are all
    `"Down"`. Anything else -- a typo, a padded string, a non-string --
    raises `UnknownButton` with the sixteen names, before any call is made.
    """
    if isinstance(name, str):
        found = _BY_FOLDED.get(name.casefold())
        if found is not None:
            return found
    raise UnknownButton("%r is not a pad button; press_button takes one of: "
                        "%s (any capitalisation)" % (name, ", ".join(BUTTONS)))


def self_check() -> list:
    """Round trips in three capitalisations, refusals, and agreement with
    the `capitalize()` rule this module replaces.

    Returns one `(name, passed, detail)` per assertion.
    """
    results = [("there are sixteen distinct buttons",
                len(BUTTONS) == 16 and len(set(BUTTONS)) == 16, BUTTONS)]
    wrong = [n for n in BUTTONS
             if (canonical(n), canonical(n.lower()), canonical(n.upper()))
             != (n, n, n)]
    results.append(("canonical() round-trips every name in any "
                    "capitalisation", not wrong, wrong))
    differs = [n for n in BUTTONS if canonical(n.lower()) != n.lower()
               .capitalize()]
    results.append(("canonical() agrees with the old capitalize() rule on "
                    "every valid name", not differs, differs))
    let_through = []
    for junk in ("", "X", "cross ", " Cross", "Triangel", "Start2", "L4",
                 None, 3, b"Cross"):
        try:
            got = canonical(junk)
        except UnknownButton as exc:
            if "Cross" not in str(exc):
                let_through.append((junk, "message lacks the list"))
        else:
            let_through.append((junk, got))
    results.append(("canonical() rejects junk with the list of names",
                    not let_through, let_through))
    results.append(("UnknownButton is a ValueError",
                    issubclass(UnknownButton, ValueError), ""))
    return results
