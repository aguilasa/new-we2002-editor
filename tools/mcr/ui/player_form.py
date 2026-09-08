#!/usr/bin/env python3
"""One player's record, read only: identity, appearance, physique, ratings.

Rule 3 (section 3.3 of the plan): this file imports `model` and `domains` and
nothing else from the port. No address, no container, no I/O.

READ ONLY BY CONSTRUCTION, not by discipline. Every value is a `QLabel`. There
is no editable widget on this form and therefore no signal that could reach a
write path -- MCR-TASK-11 opens a card, MCR-TASK-12 is what makes it writable.

THE SHIRT NUMBER IS SHOWN TWICE because the card stores it twice, and the two
disagreeing is the cheapest evidence that an encoder is wrong (section 1.5 of
the plan). A form that showed one number would hide the tripwire.

AN UNNAMED INDEX IS NOT AN ERROR. Three fields hold more values than the
upstream ever named -- `beard_style` and `beard_colour` name 7 of 8, `foot`
names 3 of 4 -- so `domains.label()` gives `"?"` for a legal value nobody
labelled, and raises only when the value is out of the field's range. The form
keeps those apart: `?` is printed, out of range is printed as the reason.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import attributes                                        # noqa: E402
import domains                                           # noqa: E402
from PySide6 import QtCore, QtWidgets                    # noqa: E402

# The sixteen ratings are the fields the card stores as 12..19 -- the same
# three bits plus twelve that the upstream shows as a 1..8 star bar.
RATINGS = tuple(f.name for f in attributes.FIELDS if f.low == 12)

APPEARANCE = ("position", "hair_style", "hair_colour", "beard_style",
              "beard_colour", "skin_colour", "build", "boots", "foot",
              "out_of_position")
PHYSIQUE = ("height", "age")


def _title(field: str) -> str:
    return field.replace("_", " ").title()


class PlayerForm(QtWidgets.QWidget):
    """The record of one squad slot, in three groups."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._values: dict[str, QtWidgets.QLabel] = {}

        outer = QtWidgets.QVBoxLayout(self)
        self._heading = QtWidgets.QLabel("No player selected")
        font = self._heading.font()
        font.setBold(True)
        font.setPointSize(font.pointSize() + 3)
        self._heading.setFont(font)
        outer.addWidget(self._heading)

        self._numbers = QtWidgets.QLabel("")
        outer.addWidget(self._numbers)

        columns = QtWidgets.QHBoxLayout()
        outer.addLayout(columns)
        left = QtWidgets.QVBoxLayout()
        right = QtWidgets.QVBoxLayout()
        columns.addLayout(left)
        columns.addLayout(right)

        left.addWidget(self._group("Appearance", APPEARANCE))
        left.addWidget(self._group("Physique", PHYSIQUE))
        left.addStretch(1)
        right.addWidget(self._group("Ratings", RATINGS))
        right.addStretch(1)
        outer.addStretch(1)

    def _group(self, title: str, fields) -> QtWidgets.QGroupBox:
        box = QtWidgets.QGroupBox(title)
        grid = QtWidgets.QGridLayout(box)
        for row, field in enumerate(fields):
            name = QtWidgets.QLabel(_title(field))
            value = QtWidgets.QLabel("--")
            value.setTextInteractionFlags(
                QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
            grid.addWidget(name, row, 0)
            grid.addWidget(value, row, 1)
            self._values[field] = value
        return box

    def clear(self) -> None:
        self._heading.setText("No player selected")
        self._numbers.setText("")
        for value in self._values.values():
            value.setText("--")

    def show_player(self, player) -> None:
        position = self._label("position", player)
        self._heading.setText(f"[{position.upper()}] {player.name}")

        table, record = player.shirt_number, player.attributes["number"]
        agree = "" if player.number_agrees else "   <- THE TWO COPIES DISAGREE"
        self._numbers.setText(
            f"Slot {player.index}    shirt number {table} (table), "
            f"{record} (record){agree}")

        for field, widget in self._values.items():
            raw = player.attributes[field]
            text = str(raw)
            if field in domains.FOR_FIELD:
                label = self._label(field, player)
                # `height` and `age` have a label table whose entries ARE the
                # numbers, so appending it prints "191   191". Show the label
                # only when it says something the number does not.
                if label != text:
                    text = f"{raw}   {label}"
            widget.setText(text)

    @staticmethod
    def _label(field: str, player) -> str:
        try:
            return player.label(field)
        except domains.DomainError as e:
            # Out of the field's range: a real defect, and it says so on the
            # screen instead of taking the window down.
            return f"<out of range: {e}>"
