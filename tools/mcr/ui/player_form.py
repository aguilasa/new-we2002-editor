#!/usr/bin/env python3
"""One player's record, editable: identity, appearance, physique, ratings.

Rule 3 (section 3.3 of the plan): this file imports `model`, `attributes` and
`domains` and nothing else from the port. No address, no container, no I/O.

MCR-TASK-11 MADE THIS FORM READ ONLY BY CONSTRUCTION -- every value was a
`QLabel`, so no signal could reach a write path. MCR-TASK-12 spends that
guarantee, and it has to be replaced by one that is measured rather than
promised. Three things stand in for it, and each has a planted control:

  the range is the FIELD's. Every editor is built from `attributes.Field`, so
  a spin box cannot offer a value the record cannot hold and a combo cannot
  offer an index outside the domain. Out of range is unreachable here, not
  merely refused downstream;
  editing changes the MODEL, never the card. Nothing on this form opens a
  file: the values land in the `Player` dataclass, and the bytes move only
  when the window calls `model.store()`. Closing without saving is therefore
  safe by construction, which is the property MCR-TASK-11 had for reading;
  the one write door. `selftest.py` sweeps `tools/mcr/ui/**.py` and demands
  that every `model.store(` in it live in `main_window.py` -- the control
  `ui-writes-from-two-places` plants a second call here and goes red.

THE SHIRT NUMBER IS SHOWN TWICE because the card stores it twice, and the two
disagreeing is the cheapest evidence that an encoder is wrong (section 1.5 of
the plan). Editing it goes through `Player.set_number`, which moves both; a
form that wrote one copy would be the defect this display exists to catch.

THE NAME REFUSES, IT DOES NOT TRUNCATE. Ten bytes of cp932, so five katakana
fill the field and a two-byte character straddling the tenth byte cannot be
cut in half. `Player.set_name` is what says so, and the form puts the sentence
on screen and restores what was there.

AN UNNAMED INDEX IS NOT AN ERROR. Three fields hold more values than the
upstream ever named -- `beard_style` and `beard_colour` name 7 of 8, `foot`
names 3 of 4 -- so `domains.label()` gives `"?"` for a legal value nobody
labelled, and raises only when the value is out of the field's range.
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


def _item_text(field: str, value: int) -> str:
    """`12  fast` -- the number first, and the label only when it adds to it.

    `height` and `age` have a label table whose entries ARE the numbers, so
    appending it prints "191   191".
    """
    try:
        label = domains.label(field, value)
    except domains.DomainError:
        return str(value)
    return str(value) if label == str(value) else f"{value}   {label}"


class PlayerForm(QtWidgets.QWidget):
    """The record of one squad slot, in four groups, all of them editable."""

    changed = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._player = None
        self._loading = False
        self._editors: dict[str, QtWidgets.QWidget] = {}

        outer = QtWidgets.QVBoxLayout(self)
        self._heading = QtWidgets.QLabel("No player selected")
        font = self._heading.font()
        font.setBold(True)
        font.setPointSize(font.pointSize() + 3)
        self._heading.setFont(font)
        outer.addWidget(self._heading)

        outer.addWidget(self._identity())

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
        self.setEnabled(False)

    # -- building ---------------------------------------------------------

    def _identity(self) -> QtWidgets.QGroupBox:
        box = QtWidgets.QGroupBox("Identity")
        grid = QtWidgets.QGridLayout(box)

        self.name = QtWidgets.QLineEdit()
        self.name.setMaxLength(10)          # ten BYTES is the real limit, and
        # cp932 makes them differ: this only stops the obvious case, and
        # `Player.set_name` is what actually refuses.
        self.name.editingFinished.connect(self._commit_name)
        grid.addWidget(QtWidgets.QLabel("Name"), 0, 0)
        grid.addWidget(self.name, 0, 1)

        f = attributes.BY_NAME["number"]
        self.number = QtWidgets.QSpinBox()
        self.number.setRange(f.low, f.high)
        self.number.valueChanged.connect(self._commit_number)
        grid.addWidget(QtWidgets.QLabel("Shirt number"), 1, 0)
        grid.addWidget(self.number, 1, 1)

        self._numbers = QtWidgets.QLabel("")
        grid.addWidget(self._numbers, 1, 2)
        grid.setColumnStretch(2, 1)
        return box

    def _group(self, title: str, fields) -> QtWidgets.QGroupBox:
        box = QtWidgets.QGroupBox(title)
        grid = QtWidgets.QGridLayout(box)
        for row, field in enumerate(fields):
            grid.addWidget(QtWidgets.QLabel(_title(field)), row, 0)
            editor = self._editor(field)
            grid.addWidget(editor, row, 1)
            self._editors[field] = editor
        return box

    def _editor(self, field: str) -> QtWidgets.QWidget:
        """A combo when the upstream named the values, a spin box otherwise.

        THE RANGE COMES FROM THE FIELD, always: `Field.low`..`Field.high` is
        what the bits hold, so neither widget can offer a value the record
        cannot store. That is the substitute for MCR-TASK-11's read-only form
        -- a guarantee by construction, not a check somebody remembers.
        """
        f = attributes.BY_NAME[field]
        if field in domains.FOR_FIELD and field not in ("height", "age"):
            combo = QtWidgets.QComboBox()
            for value in range(f.low, f.high + 1):
                combo.addItem(_item_text(field, value), value)
            combo.currentIndexChanged.connect(
                lambda _, name=field: self._commit(name))
            return combo
        spin = QtWidgets.QSpinBox()
        spin.setRange(f.low, f.high)
        spin.valueChanged.connect(lambda _, name=field: self._commit(name))
        return spin

    def editor(self, field: str) -> QtWidgets.QWidget:
        """The widget that edits `field`. The gate's way in, and it is the
        real widget -- setting its value fires the same signal a person
        would."""
        return self._editors[field]

    # -- showing ----------------------------------------------------------

    def clear(self) -> None:
        self._player = None
        self.setEnabled(False)
        self._heading.setText("No player selected")
        self._numbers.setText("")
        self._loading = True
        self.name.setText("")
        self._loading = False

    def show_player(self, player) -> None:
        self._player = player
        self._loading = True
        try:
            self.setEnabled(True)
            self.name.setText(player.name)
            self.number.setValue(player.shirt_number)
            for field, editor in self._editors.items():
                value = player.attributes[field]
                if isinstance(editor, QtWidgets.QComboBox):
                    editor.setCurrentIndex(
                        max(0, editor.findData(value)))
                else:
                    editor.setValue(value)
        finally:
            self._loading = False
        self._refresh_heading()

    def _refresh_heading(self) -> None:
        p = self._player
        if p is None:
            return
        try:
            position = p.label("position").upper()
        except domains.DomainError:
            position = "??"
        self._heading.setText(f"[{position}] {p.name}")
        agree = "" if p.number_agrees else "   <- THE TWO COPIES DISAGREE"
        self._numbers.setText(
            f"Slot {p.index}    {p.shirt_number} (table), "
            f"{p.attributes['number']} (record){agree}")

    # -- editing ----------------------------------------------------------

    def _commit(self, field: str) -> None:
        if self._loading or self._player is None:
            return
        editor = self._editors[field]
        value = (editor.currentData() if isinstance(editor,
                                                    QtWidgets.QComboBox)
                 else editor.value())
        if value is None or self._player.attributes[field] == value:
            return
        self._player.attributes[field] = value
        self._refresh_heading()
        self.changed.emit()

    def _commit_number(self, value: int) -> None:
        if self._loading or self._player is None:
            return
        if self._player.shirt_number == value \
                and self._player.attributes["number"] == value:
            return
        # BOTH copies, by name. Section 1.5 of the plan.
        self._player.set_number(value)
        self._refresh_heading()
        self.changed.emit()

    def _commit_name(self) -> None:
        if self._loading or self._player is None:
            return
        wanted = self.name.text()
        if wanted == self._player.name:
            return
        try:
            self._player.set_name(wanted)
        except Exception as e:                            # noqa: BLE001
            # `text.encode_name` already explains itself -- ten bytes of cp932,
            # and why cutting a two-byte character in half is not an option.
            QtWidgets.QMessageBox.warning(self, "This name does not fit",
                                          str(e))
            self._loading = True
            self.name.setText(self._player.name)
            self._loading = False
            return
        self._refresh_heading()
        self.changed.emit()
