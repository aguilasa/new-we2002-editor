#!/usr/bin/env python3
"""The window: a Players tab, a Formation tab, and the one write door.

Rule 3 (section 3.3 of the plan): the UI knows no address. This file imports
`model` and nothing else from the port -- `model.load()` is the way in and
`model.store()` the way out, and the selftest sweeps `tools/mcr/ui/**.py` for
`layout`, `card` and `mcrio` to keep it that way.

EVERY WRITE IN THIS PORT'S UI GOES THROUGH `_store`, AND THE SWEEP SAYS SO.
`selftest.py` demands that every `model.store(` under `tools/mcr/ui/` live in
this file, and the control `ui-writes-from-two-places` plants a second call in
`squad_view.py` and has to go red. MCR-TASK-11 could say "nothing here writes"
and have it be structurally true; once the form is editable that sentence has
to be replaced by something measured, and this is it.

WRITING GOES TO A COPY BY DEFAULT. `Save` (Ctrl+S) writes the file
`model.copy_target()` names -- `x-edited.mcr` beside `x.mcr` -- and never the
card that was opened. Overwriting the original is a separate menu item that
asks first, with No as the default button, and it does NOT pass `force`: the
refusal that protects the cycle's fixture is `mcrio`'s and stays in force even
when the person at the keyboard says yes.

A CARD THAT WILL NOT OPEN IS A MESSAGE, NOT A TRACEBACK. `model.load` refuses a
file that is not 131,072 bytes, has no `MC`, or has no WE2002 save in its
directory, and each refusal already says why -- so the window shows that
sentence and stays up. The same is true of a write that is refused.

`headless` IS FOR THE GATE, and it exists because of what a modal does to one:
`QMessageBox` spins its own event loop, so a refusal during `--smoke` or
`--write-probe` would hang until the gate's timeout and report "did not exit"
instead of the reason. With `headless` set, refusals raise and the process
dies saying what happened.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model                                             # noqa: E402
from PySide6 import QtGui, QtWidgets                     # noqa: E402
from formation_view import FormationView                 # noqa: E402
from squad_view import SquadView                         # noqa: E402

TITLE = "WE2002 memory card"


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, path: str | None = None):
        super().__init__()
        self.setWindowTitle(TITLE)
        self.resize(1000, 720)
        self._save = None
        self._path = None
        self._dirty = False
        self.headless = False

        self.squad = SquadView()
        self.formation = FormationView()
        tabs = QtWidgets.QTabWidget()
        tabs.addTab(self.squad, "Players")
        tabs.addTab(self.formation, "Formation")
        self.setCentralWidget(tabs)
        self.squad.changed.connect(self._touched)
        self.formation.changed.connect(self._touched)

        menu = self.menuBar().addMenu("&File")
        self._add(menu, "&Open card...", self.choose,
                  QtGui.QKeySequence.StandardKey.Open)
        menu.addSeparator()
        self.act_save = self._add(menu, "&Save a copy", self.save_copy,
                                  QtGui.QKeySequence.StandardKey.Save)
        self.act_save_as = self._add(menu, "Save &as...", self.save_as_dialog,
                                     QtGui.QKeySequence.StandardKey.SaveAs)
        self.act_overwrite = self._add(menu, "Overwrite the &original...",
                                       self.overwrite_original)
        menu.addSeparator()
        self._add(menu, "&Quit", self.close,
                  QtGui.QKeySequence.StandardKey.Quit)
        self._writable(False)

        self.statusBar().showMessage("No card open")
        if path:
            self.open(path)

    def _add(self, menu, text, slot, shortcut=None) -> QtGui.QAction:
        action = QtGui.QAction(text, self)
        if shortcut is not None:
            action.setShortcut(shortcut)
        action.triggered.connect(slot)
        menu.addAction(action)
        return action

    def _writable(self, on: bool) -> None:
        for action in (self.act_save, self.act_save_as, self.act_overwrite):
            action.setEnabled(on)

    # -- what the gate reads ----------------------------------------------

    @property
    def save(self):
        """The model this window is showing, or None."""
        return self._save

    @property
    def path(self) -> str | None:
        """The file it came from."""
        return self._path

    @property
    def dirty(self) -> bool:
        """Whether there are edits that are in no file yet."""
        return self._dirty

    # -- reading ----------------------------------------------------------

    def choose(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open memory card", "", "Memory cards (*.mcr);;All files (*)")
        if path:
            self.open(path)

    def open(self, path: str) -> bool:
        try:
            save = model.load(path)
        except Exception as e:                            # noqa: BLE001
            # The refusals of card.py and mcrio.py already explain themselves;
            # repeating them here in other words would only make two versions
            # of the same sentence.
            if self.headless:
                raise
            QtWidgets.QMessageBox.warning(self, "This card cannot be opened",
                                          str(e))
            self.statusBar().showMessage(f"Refused: {os.path.basename(path)}")
            return False
        self._save = save
        self._path = path
        self._dirty = False
        self.squad.set_save(save)
        self.formation.set_save(save)
        self._writable(True)
        self._describe()
        return True

    def _describe(self, note: str = "") -> None:
        if self._save is None:
            self.statusBar().showMessage("No card open")
            return
        entry, blocks = self._save.card.find_save()
        disagreeing = len(self._save.disagreements())
        warn = ("" if not disagreeing
                else f"    {disagreeing} shirt number(s) DISAGREE")
        self.statusBar().showMessage(
            f"{self._path}    {entry.name}    blocks {blocks}    "
            f"{len(self._save.players)} players{warn}"
            + (f"    {note}" if note else ""))
        star = " *" if self._dirty else ""
        self.setWindowTitle(
            f"{os.path.basename(self._path)}{star} -- {TITLE}")

    def _touched(self) -> None:
        self._dirty = True
        self._describe()

    # -- writing ----------------------------------------------------------

    def _store(self, target: str) -> str | None:
        """THE ONE WRITE IN THIS TREE. Everything above funnels here."""
        if self._save is None:
            return None
        try:
            written = model.store(self._save, target)
        except Exception as e:                            # noqa: BLE001
            if self.headless:
                raise
            QtWidgets.QMessageBox.warning(self, "This card was not written",
                                          str(e))
            self._describe("not written")
            return None
        self._dirty = False
        self._describe(f"written to {os.path.basename(written)}")
        return written

    def save_copy(self) -> str | None:
        """Ctrl+S: a copy beside the card, never the card."""
        if self._path is None:
            return None
        return self._store(model.copy_target(self._path))

    def save_as_dialog(self) -> str | None:
        target, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Write the memory card as",
            model.copy_target(self._path) if self._path else "",
            "Memory cards (*.mcr);;All files (*)")
        return self.save_as(target) if target else None

    def save_as(self, target: str) -> str | None:
        """Write to a named path. The dialog and the gate both arrive here."""
        return self._store(target)

    def overwrite_original(self) -> str | None:
        """The one irreversible action, and the only one that asks first."""
        if self._path is None:
            return None
        answer = QtWidgets.QMessageBox.question(
            self, "Overwrite the original?",
            f"This writes over {self._path}, which is the file you opened. "
            f"There is no undo, and a memory card is a save nobody can play "
            f"again.\n\nWrite a copy instead with Ctrl+S.",
            QtWidgets.QMessageBox.StandardButton.Yes
            | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No)
        if answer != QtWidgets.QMessageBox.StandardButton.Yes:
            return None
        # No `force`: the refusal that guards the cycle's fixture is not the
        # window's to lift.
        return self._store(self._path)

    def closeEvent(self, event) -> None:                  # noqa: N802
        if not self._dirty or self.headless:
            event.accept()
            return
        answer = QtWidgets.QMessageBox.question(
            self, "Leave without writing?",
            "This card has edits that are not in any file yet.",
            QtWidgets.QMessageBox.StandardButton.Discard
            | QtWidgets.QMessageBox.StandardButton.Cancel,
            QtWidgets.QMessageBox.StandardButton.Cancel)
        if answer == QtWidgets.QMessageBox.StandardButton.Discard:
            event.accept()
        else:
            event.ignore()
