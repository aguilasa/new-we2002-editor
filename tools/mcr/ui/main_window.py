#!/usr/bin/env python3
"""The window: a Players tab, a Formation tab, and no way to write anything.

Rule 3 (section 3.3 of the plan): the UI knows no address. This file imports
`model` and nothing else from the port -- `model.load()` is the one door in,
and the selftest sweeps `tools/mcr/ui/**.py` for `layout`, `card` and `mcrio`
to keep it that way.

NOTHING HERE WRITES. There is no Save action, no editable widget and no call
that reaches `Save.write`; opening a card is safe by construction, not by
carefulness. MCR-TASK-12 is what adds the other half, and it should have to add
it on purpose.

A CARD THAT WILL NOT OPEN IS A MESSAGE, NOT A TRACEBACK. `model.load` refuses a
file that is not 131,072 bytes, has no `MC`, or has no WE2002 save in its
directory, and each refusal already says why -- so the window shows that
sentence and stays up.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model                                             # noqa: E402
from PySide6 import QtGui, QtWidgets                     # noqa: E402
from formation_view import FormationView                 # noqa: E402
from squad_view import SquadView                         # noqa: E402

TITLE = "WE2002 memory card -- read only"


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, path: str | None = None):
        super().__init__()
        self.setWindowTitle(TITLE)
        self.resize(1000, 640)
        self._save = None

        self.squad = SquadView()
        self.formation = FormationView()
        tabs = QtWidgets.QTabWidget()
        tabs.addTab(self.squad, "Players")
        tabs.addTab(self.formation, "Formation")
        self.setCentralWidget(tabs)

        menu = self.menuBar().addMenu("&File")
        open_action = QtGui.QAction("&Open card...", self)
        open_action.setShortcut(QtGui.QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.choose)
        menu.addAction(open_action)
        quit_action = QtGui.QAction("&Quit", self)
        quit_action.setShortcut(QtGui.QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        menu.addAction(quit_action)

        self.statusBar().showMessage("No card open")
        if path:
            self.open(path)

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
            QtWidgets.QMessageBox.warning(self, "This card cannot be opened",
                                          str(e))
            self.statusBar().showMessage(f"Refused: {os.path.basename(path)}")
            return False
        self._save = save
        self.squad.set_save(save)
        self.formation.set_save(save)
        entry, blocks = save.card.find_save()
        disagreeing = len(save.disagreements())
        note = ("" if not disagreeing
                else f"    {disagreeing} shirt number(s) DISAGREE")
        self.statusBar().showMessage(
            f"{path}    {entry.name}    blocks {blocks}    "
            f"{len(save.players)} players{note}")
        self.setWindowTitle(f"{os.path.basename(path)} -- {TITLE}")
        return True
