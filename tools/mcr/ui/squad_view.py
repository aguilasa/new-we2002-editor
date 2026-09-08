#!/usr/bin/env python3
"""The 23 slots on the left, the selected player's record on the right.

Rule 3: `model` and `domains`, nothing else from the port.

THE LIST LABEL IS OURS, NOT THE UPSTREAM'S. Zetaprog's `ListBoxMcR` is filled
with `Player1..Player23` at design time and each row is replaced by the bare
name as the card is read -- no position, no slot number. MCR-TASK-11 asked for
`[GK] Name` and that is what this shows, because a list of twenty-three
katakana names with nothing else on the row is unusable for finding the
goalkeeper. The position comes from `domains`, which is the upstream's own
table; the shape of the row is a decision of this port.

THE ROW FOLLOWS THE EDIT. Renaming a player or changing their position on the
form has to move the list too, or the screen shows two answers to the same
question -- so the form's `changed` is what repaints the current row, and only
that row.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import domains                                           # noqa: E402
from PySide6 import QtCore, QtWidgets                    # noqa: E402
from player_form import PlayerForm                       # noqa: E402


class SquadView(QtWidgets.QWidget):
    """The squad list and the form, side by side."""

    changed = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._save = None

        self.list = QtWidgets.QListWidget()
        self.list.setMinimumWidth(220)
        self.form = PlayerForm()

        splitter = QtWidgets.QSplitter()
        splitter.addWidget(self.list)
        holder = QtWidgets.QScrollArea()
        holder.setWidgetResizable(True)
        holder.setWidget(self.form)
        splitter.addWidget(holder)
        splitter.setStretchFactor(1, 1)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(splitter)

        self.list.currentRowChanged.connect(self._select)
        self.form.changed.connect(self._edited)

    @staticmethod
    def _row(player) -> str:
        try:
            position = player.label("position").upper()
        except domains.DomainError:
            position = "??"
        return f"[{position}] {player.name}"

    def set_save(self, save) -> None:
        self._save = save
        self.list.clear()
        self.form.clear()
        if save is None:
            return
        for player in save.players:
            self.list.addItem(self._row(player))
        self.list.setCurrentRow(0)

    def _select(self, row: int) -> None:
        if self._save is None or not 0 <= row < len(self._save.players):
            self.form.clear()
            return
        self.form.show_player(self._save.players[row])

    def _edited(self) -> None:
        row = self.list.currentRow()
        if self._save is not None and 0 <= row < len(self._save.players):
            self.list.item(row).setText(self._row(self._save.players[row]))
        self.changed.emit()
