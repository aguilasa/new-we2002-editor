#!/usr/bin/env python3
"""The kit viewer's window.  Run it with the venv's python.

PLAN-KITS-PY.md section 3.4.  Presentation only: every number on screen is
what `core.api` returns, and this file imports nothing else of the
repository -- `kits_selftest` holds it to that (section 3.1).

**NOTHING OPENS ON THE USER'S SCREEN.**  The window is parked off the desktop
before it is shown -- the `-32000` of `CLAUDE.md` on Windows -- and on Linux
the display is `:98`, set by whoever runs this.  `--visible` is for the user
asking to look, and it is not what a gate runs.

**One look on both systems.**  The style is Fusion, the palette is fixed here
and inherits no system theme, and the font has its family and its size in
pixels fixed, so Windows at 150 % and Linux lay the window out alike.  The
layouts are Qt's: this window reproduces no screen.

Usage (the venv's python: work/venv-looks/Scripts/python.exe on Windows,
work/venv-looks/bin/python on Linux):

    <venv>/python tools/kits/ui/app.py [<rom or TEX>]
    <venv>/python tools/kits/ui/app.py <rom> --tag A4 --image work1 --palette 3 \\
        --zoom 4 --zones --screenshot out.png
    <venv>/python tools/kits/ui/app.py <rom> --walk
    <venv>/python tools/kits/ui/app.py <rom> --tag 00 --hover 15,10
    <venv>/python tools/kits/ui/app.py <rom> --lang pt-BR

**Every text of the window comes from `i18n.py`**, US English by default:
`--lang`, then `WE2002_KITS_LANG`, then en-US; the selector at the top
switches without reopening, and `--switch-to` does what a click there does.
The core's sentences (status notes, refusals, record and zone names) stay
English (section 3.4, KITS-TASK-36).

On Linux `make kits` (`make kits-98` for the Xvfb) runs it with `--visible`:
TAG=, KITS_IMAGE=, ARGS=.
"""

from __future__ import annotations

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import api  # noqa: E402
import i18n  # noqa: E402
from i18n import tr  # noqa: E402
from PySide6 import QtCore, QtGui, QtWidgets  # noqa: E402
from figure_view import FigureView, composed  # noqa: E402

OFF_THE_DESKTOP = -32000  # not-an-address: the parking spot CLAUDE.md names
FRAMES = 5
"""Paints let through before a picture is taken: show() schedules a paint, it
does not perform one."""

FONT_FAMILIES = ("Arial", "Liberation Sans", "DejaVu Sans")
"""Arial on Windows; Liberation Sans is its metric twin on Linux."""
FONT_PX = 13
ZOOMS = (1, 2, 3, 4, 6, 8)
DEFAULT_ZOOM = 3
CHECKER_PX = 8
CELL_PX = 14
"""One colour of the 16x16 palette grid, on screen."""

TAB_NAMES = ("plan", "3d", "diag")
"""--tab names of the three tabs, in tab order."""
MATCH_FIGURE = 2
"""The 3D figure selector's third item: the match player of section 4.3."""
DEFAULT_NUMBER = 10
"""The number the Number field opens with: the slot 5 captain's (section 4.7)."""
WORK = ("work1", "work2")
"""--image names of the two work bitmaps (first and second set); any other
--image is an image record number."""

COLOURS = {
    "Window": "#ececec", "WindowText": "#1e1e1e", "Base": "#ffffff",
    "AlternateBase": "#f4f4f4", "Text": "#1e1e1e", "Button": "#e0e0e0",
    "ButtonText": "#1e1e1e", "Highlight": "#2f6fb2", "HighlightedText": "#ffffff",
    "ToolTipBase": "#ffffe1", "ToolTipText": "#1e1e1e", "PlaceholderText": "#808080",
    "BrightText": "#ff0000", "Light": "#ffffff", "Midlight": "#f0f0f0",
    "Mid": "#b8b8b8", "Dark": "#a0a0a0", "Shadow": "#606060", "Link": "#2f6fb2",
}
"""The fixed palette, by QPalette role: a light one, set the same everywhere."""
DISABLED_TEXT = "#9a9a9a"
DISABLED_ROLES = ("WindowText", "Text", "ButtonText")
CORE_TEXT = "text"
"""The field of a status line that is the core's own sentence, not a catalog
entry: the core speaks English only (section 3.4)."""
CHECKER = ("#cfcfcf", "#f2f2f2")
BACKDROP = "#8c8c8c"
ZONE_PEN = "#e0157a"
GAP_PEN = "#1e9be0"


def fixed_palette() -> QtGui.QPalette:
    pal = QtGui.QPalette()
    for role, colour in COLOURS.items():
        pal.setColor(getattr(QtGui.QPalette.ColorRole, role), QtGui.QColor(colour))
    for role in DISABLED_ROLES:
        pal.setColor(QtGui.QPalette.ColorGroup.Disabled,
                     getattr(QtGui.QPalette.ColorRole, role), QtGui.QColor(DISABLED_TEXT))
    return pal


def fixed_font() -> QtGui.QFont:
    font = QtGui.QFont()
    font.setFamilies(list(FONT_FAMILIES))
    font.setPixelSize(FONT_PX)
    return font


def apply_style(app: QtWidgets.QApplication) -> None:
    """Fusion, the fixed palette and the fixed font: section 3.4."""
    app.setStyle("Fusion")
    app.setPalette(fixed_palette())
    app.setFont(fixed_font())


# -- what can be shown --------------------------------------------------------

def image_choices() -> list:
    """[(label, key)] of the image selector: the two work bitmaps, then every
    image the game pairs with a palette (`api.GAME_PAIRS`).  The work bitmaps'
    labels are in the language in force; record names are the core's."""
    out = [(tr("work_set_1"), WORK[0]), (tr("work_set_2"), WORK[1])]
    for image, _ in api.GAME_PAIRS:
        if all(key != image for _, key in out):
            out.append((api.RECORD_NAMES[image], image))
    return out


def palette_choices(key) -> list:
    """Palette records that go with image *key*, in the game's pairing order."""
    if key in WORK:
        kit_set = WORK.index(key) + 1
        return [api.WORK_PALETTE[(kit_set, f)] for f in api.FIGURES]
    return [p for i, p in api.GAME_PAIRS if i == key]


def zone_left(key):
    """x of the image's left edge in the 256x128 the zone map is drawn on, or
    None when the map does not cover it (the flag)."""
    if key in WORK or key in api.UNIFORM_OF_SET.values():
        return 0
    if key in api.SLEEVES_OF_SET.values():
        return api.WORK_W // 2
    return None


def paint_choice(kit, key, palette):
    """The `FlatImage` of image *key* in palette record *palette*."""
    if key in WORK:
        kit_set = WORK.index(key) + 1
        figure = [api.WORK_PALETTE[(kit_set, f)] for f in api.FIGURES].index(palette)
        return kit.work_bitmap(kit_set, figure)
    return kit.flat(key, palette)


def parse_image(text: str):
    if text in WORK:
        return text
    try:
        return int(text)
    except ValueError:
        raise argparse.ArgumentTypeError("--image is %s or an image record number"
                                         % " or ".join(WORK))


# -- widgets --------------------------------------------------------------------

class Canvas(QtWidgets.QWidget):
    """The image, zoomed by nearest neighbour, over a checkerboard, with the
    zone map on top when asked."""

    hovered = QtCore.Signal(int, int)    # image pixel, or (-1, -1)

    def __init__(self) -> None:
        super().__init__()
        self.setMouseTracking(True)
        self.image = None                # QImage
        self.zoom = DEFAULT_ZOOM
        self.checker = True
        self.zones = ()                  # (QRect in image pixels, is a gap)
        self.show_zones = False

    def set_image(self, image, zones) -> None:
        self.image = image
        self.zones = zones
        self.updateGeometry()
        self.adjustSize()
        self.update()

    def sizeHint(self) -> QtCore.QSize:
        if self.image is None:
            return QtCore.QSize(256, 128)
        return QtCore.QSize(self.image.width() * self.zoom, self.image.height() * self.zoom)

    def paintEvent(self, _event) -> None:
        p = QtGui.QPainter(self)
        p.fillRect(self.rect(), QtGui.QColor(BACKDROP))
        if self.image is None:
            return
        area = QtCore.QRect(0, 0, self.image.width() * self.zoom,
                            self.image.height() * self.zoom)
        if self.checker:
            for y in range(0, area.height(), CHECKER_PX):
                for x in range(0, area.width(), CHECKER_PX):
                    p.fillRect(x, y, CHECKER_PX, CHECKER_PX,
                               QtGui.QColor(CHECKER[(x // CHECKER_PX + y // CHECKER_PX) % 2]))
        else:
            p.fillRect(area, QtGui.QColor(CHECKER[1]))
        p.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform, False)
        p.drawImage(area, self.image)
        if self.show_zones:
            for rect, gap in self.zones:
                pen = QtGui.QPen(QtGui.QColor(GAP_PEN if gap else ZONE_PEN))
                pen.setCosmetic(True)
                p.setPen(pen)
                p.drawRect(rect.x() * self.zoom, rect.y() * self.zoom,
                           rect.width() * self.zoom - 1, rect.height() * self.zoom - 1)

    def mouseMoveEvent(self, event) -> None:
        if self.image is None:
            return
        x = int(event.position().x()) // self.zoom
        y = int(event.position().y()) // self.zoom
        inside = 0 <= x < self.image.width() and 0 <= y < self.image.height()
        self.hovered.emit(x if inside else -1, y if inside else -1)

    def leaveEvent(self, _event) -> None:
        self.hovered.emit(-1, -1)


class PaletteGrid(QtWidgets.QWidget):
    """The 256 colours of the palette in use, 16 to a row."""

    hovered = QtCore.Signal(int)         # index, or -1

    def __init__(self) -> None:
        super().__init__()
        self.setMouseTracking(True)
        self.entries = ()
        self.marked = -1
        self.setFixedSize(16 * CELL_PX + 1, 16 * CELL_PX + 1)

    def set_entries(self, entries) -> None:
        self.entries = entries
        self.update()

    def mark(self, index: int) -> None:
        self.marked = index
        self.update()

    def paintEvent(self, _event) -> None:
        p = QtGui.QPainter(self)
        p.fillRect(self.rect(), QtGui.QColor(BACKDROP))
        for e in self.entries:
            x, y = (e.index % 16) * CELL_PX, (e.index // 16) * CELL_PX
            if e.transparent:
                half = CELL_PX // 2
                for dy in (0, half):
                    for dx in (0, half):
                        p.fillRect(x + dx, y + dy, half, half,
                                   QtGui.QColor(CHECKER[(dx + dy) // half % 2]))
            else:
                r, g, b, _ = e.rgba
                p.fillRect(x, y, CELL_PX, CELL_PX, QtGui.QColor(r, g, b))
        if 0 <= self.marked < 256:
            p.setPen(QtGui.QPen(QtGui.QColor(ZONE_PEN), 2))
            p.drawRect((self.marked % 16) * CELL_PX + 1, (self.marked // 16) * CELL_PX + 1,
                       CELL_PX - 2, CELL_PX - 2)

    def mouseMoveEvent(self, event) -> None:
        x = int(event.position().x()) // CELL_PX
        y = int(event.position().y()) // CELL_PX
        self.hovered.emit(y * 16 + x if 0 <= x < 16 and 0 <= y < 16 else -1)

    def leaveEvent(self, _event) -> None:
        self.hovered.emit(-1)


def describe(entry) -> str:
    r, g, b, a = entry.rgba
    return tr("readout_entry", index=entry.index, bgr555=entry.bgr555, r=r, g=g, b=b) + (
        tr("readout_transparent") if not a else "")


class Window(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.source = None
        self.kit = None
        self.picture = None              # the FlatImage on the canvas
        self.grid = ()                   # its palette as PaletteEntry
        self.left = None                 # zone_left() of the image shown
        self.path = None                 # what is open, or None
        self.said = (None, {})           # the status line: (catalog key or None, fields)

        top = QtWidgets.QHBoxLayout()
        self.open_button = QtWidgets.QPushButton()
        self.open_button.clicked.connect(self.ask_open)
        self.path_label = QtWidgets.QLabel()
        self.path_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        # A long path is cut, not obeyed: the window's width is the layout's,
        # whatever was opened and from where.
        self.path_label.setSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored,
                                      QtWidgets.QSizePolicy.Policy.Preferred)
        self.tag_box = QtWidgets.QComboBox()
        self.tag_box.setMinimumContentsLength(18)
        self.tag_box.currentIndexChanged.connect(self.load_kit)
        self.tag_box.hide()
        top.addWidget(self.open_button)
        top.addWidget(self.path_label, 1)
        top.addWidget(self.tag_box)
        self.language_label = QtWidgets.QLabel()
        self.language_box = QtWidgets.QComboBox()
        for code in i18n.LANGUAGES:
            self.language_box.addItem(i18n.NAMES[code], code)
        self.language_box.setCurrentIndex(i18n.LANGUAGES.index(i18n.language()))
        self.language_box.currentIndexChanged.connect(self.language_changed)
        top.addWidget(self.language_label)
        top.addWidget(self.language_box)

        self.image_box = QtWidgets.QComboBox()
        for label, key in image_choices():
            self.image_box.addItem(label, key)
        self.image_box.currentIndexChanged.connect(self.image_changed)
        self.palette_box = QtWidgets.QComboBox()
        self.palette_box.currentIndexChanged.connect(self.redraw)
        self.zoom_box = QtWidgets.QComboBox()
        for z in ZOOMS:
            self.zoom_box.addItem(tr("zoom_item", zoom=z), z)
        self.zoom_box.setCurrentIndex(ZOOMS.index(DEFAULT_ZOOM))
        self.zoom_box.currentIndexChanged.connect(self.zoom_changed)
        self.checker_box = QtWidgets.QCheckBox()
        self.checker_box.setChecked(True)
        self.checker_box.toggled.connect(self.checker_changed)
        self.grid_box = QtWidgets.QCheckBox()
        self.grid_box.setChecked(True)
        self.zones_box = QtWidgets.QCheckBox()
        self.zones_box.toggled.connect(self.zones_changed)
        self.export_button = QtWidgets.QPushButton()
        self.export_button.clicked.connect(self.ask_export)

        controls = QtWidgets.QHBoxLayout()
        # catalog key -> the QLabel beside its selector
        self.labels = {"image": QtWidgets.QLabel(), "palette": QtWidgets.QLabel(),
                       "zoom": QtWidgets.QLabel()}
        for key, widget in zip(self.labels, (self.image_box, self.palette_box, self.zoom_box)):
            controls.addWidget(self.labels[key])
            controls.addWidget(widget)
        for widget in (self.checker_box, self.grid_box, self.zones_box):
            controls.addWidget(widget)
        controls.addStretch(1)
        controls.addWidget(self.export_button)

        self.canvas = Canvas()
        self.canvas.hovered.connect(self.on_pixel)
        scroll = QtWidgets.QScrollArea()
        scroll.setWidget(self.canvas)
        scroll.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.palette_grid = PaletteGrid()
        self.palette_grid.hovered.connect(self.on_index)
        self.grid_box.toggled.connect(self.palette_grid.setVisible)
        body = QtWidgets.QHBoxLayout()
        body.addWidget(scroll, 1)
        body.addWidget(self.palette_grid, 0, QtCore.Qt.AlignmentFlag.AlignTop)
        self.readout = QtWidgets.QLabel(" ")

        plan = QtWidgets.QWidget()
        plan_layout = QtWidgets.QVBoxLayout(plan)
        plan_layout.addLayout(controls)
        plan_layout.addLayout(body, 1)
        plan_layout.addWidget(self.readout)
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.addTab(plan, "")

        # The 3D tab (KITS-TASK-25): the figure the facade draws, in the set and
        # the figure chosen here.  Off, with the core's sentence, when no disc
        # gives the geometry (section 3.2).
        self.geometries = {}             # disc path -> the files api.read_geometry gave
        self.geometry = None             # the files the figure is drawn from, or None
        self.geometry_path = None
        self.geometry_reason = ""        # the core's sentence when there is none
        self.set_box = QtWidgets.QComboBox()
        self.set_box.addItem("", 1)
        self.set_box.addItem("", 2)
        self.figure_box = QtWidgets.QComboBox()
        self.figure_box.addItem("", 0)
        self.figure_box.addItem("", 1)
        # The match figure (KITS-TASK-47, section 4.3): MODEL.BIN in the pose
        # measured in the game, with the armband when `armband` is on.
        self.figure_box.addItem("", MATCH_FIGURE)
        # The three dressings (KITS-TASK-40), each drawing only what was
        # measured: the number on a LOOKS SET figure's back (section 4.7), the
        # armband and the long sleeves on the match figure (section 4.3).  What
        # was not measured stays off, with the sentence in the box's own text.
        self.number_box = QtWidgets.QCheckBox()
        self.number_spin = QtWidgets.QSpinBox()
        self.number_spin.setRange(*api.SHIRT_NUMBERS)
        self.number_spin.setValue(DEFAULT_NUMBER)
        self.armband_box = QtWidgets.QCheckBox()
        self.long_box = QtWidgets.QCheckBox()
        for widget in (self.number_box, self.armband_box, self.long_box):
            widget.toggled.connect(self.draw_figure)
        self.number_spin.valueChanged.connect(self.draw_figure)
        self.figure_box.currentIndexChanged.connect(self.dressings)
        self.set_box.currentIndexChanged.connect(self.draw_figure)
        self.figure_box.currentIndexChanged.connect(self.draw_figure)
        self.figure_view = FigureView(api.draw_figure)
        self.figure_hint = QtWidgets.QLabel()
        self.figure_hint.setWordWrap(True)
        self.reset_button = QtWidgets.QPushButton()
        self.reset_button.clicked.connect(self.figure_view.reset)
        self.figure_labels = {"kit_set": QtWidgets.QLabel(), "figure": QtWidgets.QLabel()}
        row = QtWidgets.QHBoxLayout()
        for key, widget in zip(self.figure_labels, (self.set_box, self.figure_box)):
            row.addWidget(self.figure_labels[key])
            row.addWidget(widget)
        row.addStretch(1)
        row.addWidget(self.reset_button)
        three = QtWidgets.QWidget()
        three_layout = QtWidgets.QVBoxLayout(three)
        three_layout.addLayout(row)
        dress = QtWidgets.QHBoxLayout()
        for widget in (self.number_box, self.number_spin, self.armband_box, self.long_box):
            dress.addWidget(widget)
        dress.addStretch(1)
        three_layout.addLayout(dress)
        three_layout.addWidget(self.figure_hint)
        three_layout.addWidget(self.figure_view, 1)
        self.tabs.addTab(three, "")
        self.tabs.currentChanged.connect(self.draw_figure)
        # The Diagnosis tab (section 3.4, KITS-TASK-33): the guard's problems
        # and the reading notes of the kit, record by record, in the core's words.
        self.diag_kit = None              # (label, problems, notes) shown
        self.diag_summary = QtWidgets.QLabel(" ")
        self.diag_summary.setWordWrap(True)
        self.diag_list = QtWidgets.QListWidget()
        self.diag_list.setWordWrap(True)
        diag = QtWidgets.QWidget()
        diag_layout = QtWidgets.QVBoxLayout(diag)
        diag_layout.addWidget(self.diag_summary)
        diag_layout.addWidget(self.diag_list, 1)
        self.tabs.addTab(diag, "")
        self.figure_note = QtWidgets.QLabel(" ")
        self.figure_note.setWordWrap(True)

        self.status = QtWidgets.QLabel(" ")
        self.status.setWordWrap(True)
        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central)
        layout.addLayout(top)
        layout.addWidget(self.tabs, 1)
        layout.addWidget(self.status)
        layout.addWidget(self.figure_note)
        self.setCentralWidget(central)
        # Labels change with the language, and the default policy sizes a
        # combo once, on first show: pt-BR picked live kept the en-US width,
        # and cut "Visitante" and "jogador em partida" (G2, K3D-TASK-02).
        for box in self.combos().values():
            box.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.retranslate()
        self.image_changed()

    # -- language ---------------------------------------------------------------

    def combos(self) -> dict:
        """Every combo of the window, by attribute name, found rather than
        listed so that a new one is fitted and judged with the rest (G2)."""
        return {name: widget for name, widget in vars(self).items()
                if isinstance(widget, QtWidgets.QComboBox)}

    def retranslate(self) -> None:
        """Every text of the window again, in the language in force."""
        self.setWindowTitle(tr("window_title"))
        self.open_button.setText(tr("open"))
        if self.path is None:
            self.path_label.setText(tr("nothing_open"))
        self.language_label.setText(tr("language"))
        for key, label in self.labels.items():
            label.setText(tr(key))
        for i, (label, _) in enumerate(image_choices()):
            self.image_box.setItemText(i, label)
        for i, z in enumerate(ZOOMS):
            self.zoom_box.setItemText(i, tr("zoom_item", zoom=z))
        self.checker_box.setText(tr("checker"))
        self.grid_box.setText(tr("grid"))
        self.zones_box.setText(tr("zones"))
        self.export_button.setText(tr("export_png"))
        self.tabs.setTabText(0, tr("tab_plan"))
        self.tabs.setTabText(1, tr("tab_3d"))
        self.tabs.setTabText(2, tr("tab_diag"))
        for key, label in self.figure_labels.items():
            label.setText(tr(key))
        self.set_box.setItemText(0, tr("set_first"))
        self.set_box.setItemText(1, tr("set_second"))
        self.figure_box.setItemText(0, tr("figure_player"))
        self.figure_box.setItemText(1, tr("figure_keeper"))
        self.figure_box.setItemText(2, tr("figure_match"))
        self.dressings()
        self.figure_hint.setText(tr("figure_hint"))
        self.reset_button.setText(tr("reset_view"))
        self.show_geometry()
        self.relabel_tags()
        self.show_diagnosis()
        self.say(*self.said)
        self.readout.setText(" ")

    def language_changed(self) -> None:
        i18n.set_language(self.language_box.currentData())
        self.retranslate()

    def say(self, key, fields) -> None:
        """The status line: a catalog key and its fields, or None and the core's
        own sentence (which stays English)."""
        self.said = (key, fields)
        self.status.setText(tr(key, **fields) if key else fields.get(CORE_TEXT, " "))

    # -- opening ----------------------------------------------------------------

    def ask_open(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, tr("open_title"), "", tr("open_filter"))
        if path:
            self.open_path(path)

    def open_path(self, path: str) -> bool:
        try:
            source = api.open_source(path)
        except api.KitsError as exc:
            self.say(None, {CORE_TEXT: str(exc)})
            return False
        self.source = source
        self.path = path
        self.path_label.setText(path)
        self.find_geometry()
        blocker = QtCore.QSignalBlocker(self.tag_box)
        self.tag_box.clear()
        if source.kind == api.KIND_ROM:
            for tag, _kind, _team in self.kit_order():
                self.tag_box.addItem("", tag)
            self.relabel_tags()
            self.tag_box.show()
        else:
            self.tag_box.hide()
        del blocker
        self.load_kit()
        return True

    # -- the figure's geometry (section 3.2) ----------------------------------------

    def find_geometry(self) -> None:
        """The disc the 3D figure is drawn from: the open disc when the looks
        guard trusts it, else WE2002_LOOKS_IMAGE; with neither, the 3D tab
        goes off and the core's sentence says why."""
        self.geometry, self.geometry_path, self.geometry_reason = None, None, ""
        tries = []
        if self.source is not None and self.source.kind == api.KIND_ROM:
            tries.append(self.path)
        tries.append(None)               # api.read_geometry falls back to the variable
        for path in tries:
            try:
                key = path or os.environ.get(api.GEOMETRY_ENV, "")
                if key not in self.geometries:
                    self.geometries[key] = api.read_geometry(path)
                self.geometry, self.geometry_path = self.geometries[key], key
                break
            except api.FigureError as exc:
                self.geometry_reason = str(exc)
        self.show_geometry()

    def show_geometry(self) -> None:
        self.tabs.setTabEnabled(1, self.geometry is not None)
        if self.geometry is not None:
            self.figure_note.setText(tr("figure_geometry", path=self.geometry_path))
        elif self.geometry_reason:
            self.figure_note.setText(tr("figure_off", reason=self.geometry_reason))
        else:
            self.figure_note.setText(" ")

    def match_drawn(self) -> bool:
        """The match figure is what the tab draws: its own item, or the player
        with the armband or the long sleeves, which only it has."""
        figure = self.figure_box.currentData()
        return figure == MATCH_FIGURE or (
            figure == 0 and (self.armband_box.isChecked() or self.long_box.isChecked()))

    def dressings(self) -> None:
        """Which dressing the chosen figure can take, and the sentence for
        the ones it cannot: the long sleeves only exist for the player, so
        the goalkeeper hides the box; the armband was measured on a player,
        and the number on the LOOKS SET figures' backs."""
        figure = self.figure_box.currentData()
        self.long_box.setVisible(figure != 1)
        self.long_box.setText(tr("long_sleeves"))
        keeper = figure == 1
        self.armband_box.setEnabled(not keeper)
        self.armband_box.setText(tr("armband_off") if keeper else tr("armband"))
        if keeper:
            self.armband_box.setChecked(False)
        match = self.match_drawn()
        self.number_box.setEnabled(not match)
        self.number_spin.setEnabled(not match)
        self.number_box.setText(tr("number_off") if match else tr("number"))
        if match:
            self.number_box.setChecked(False)

    def draw_figure(self) -> None:
        """The figure in the chosen set, drawn only while its tab is shown."""
        if self.tabs.currentIndex() != 1:
            return
        if self.geometry is None or self.kit is None:
            self.figure_view.set_scene(None)
            return
        self.dressings()
        try:
            if self.match_drawn():
                scene = api.match_figure(self.kit, self.set_box.currentData(),
                                         armband=self.armband_box.isChecked(),
                                         sleeves=api.MATCH_SLEEVES[
                                             0 if self.long_box.isChecked() else 1],
                                         geometry=self.geometry)
            else:
                scene = api.figure(self.kit, self.set_box.currentData(),
                                   self.figure_box.currentData(),
                                   frame=api.FIGURE_POSE, geometry=self.geometry)
                if self.number_box.isChecked():
                    scene = api.numbered(scene, self.kit, self.set_box.currentData(),
                                         self.figure_box.currentData(),
                                         self.number_spin.value())
        except api.FigureError as exc:
            self.figure_view.set_scene(None)
            self.say(None, {CORE_TEXT: str(exc)})
            return
        self.figure_view.set_scene(scene)

    def kit_order(self) -> tuple:
        """The disc's kits as the selector lists them (section 4.2): the teams
        in game order, the Master League default kit, the unworn tags."""
        try:
            teams = self.source.teams()
        except api.KitsError as exc:
            self.say(None, {CORE_TEXT: str(exc)})
            teams = ()
        return api.kit_order(teams, self.source.kit_tags())

    def relabel_tags(self) -> None:
        """The kit selector's labels: the team and its tag, the ML default
        kit, or the bare tag."""
        if self.source is None or self.source.kind != api.KIND_ROM:
            return
        labels = {}
        for tag, kind, team in self.kit_order():
            if kind == api.KIND_TEAM:
                labels[tag] = tr("kit_team", team=team.name, tag=tag)
            elif kind == api.KIND_ML_DEFAULT:
                labels[tag] = tr("kit_ml_default", tag=tag)
            else:
                labels[tag] = tr("kit_tag", tag=tag)
        for i in range(self.tag_box.count()):
            tag = self.tag_box.itemData(i)
            self.tag_box.setItemText(i, labels.get(tag, tr("kit_tag", tag=tag)))

    def tags(self) -> list:
        return [self.tag_box.itemData(i) for i in range(self.tag_box.count())]

    def select_tag(self, tag: str) -> bool:
        i = self.tag_box.findData(tag)
        if i < 0:
            return False
        if i == self.tag_box.currentIndex():
            self.load_kit()
        self.tag_box.setCurrentIndex(i)
        return True

    def load_kit(self) -> None:
        self.kit = None
        if self.source is None:
            return
        try:
            if self.source.kind == api.KIND_ROM:
                tag = self.tag_box.currentData()
                if tag is None:
                    return
                kit = self.source.kit(tag)
            else:
                kit = self.source.kit()
        except api.KitsError as exc:
            self.say(None, {CORE_TEXT: str(exc)})
            self.show_diagnosis(("", (str(exc),), ()))
            self.redraw()
            return
        self.show_diagnosis((kit.label, tuple(kit.problems), tuple(n.text for n in kit.notes)))
        if not kit.ok:
            self.say("status_refused", {"label": kit.label, "problems": "; ".join(kit.problems)})
        else:
            notes = "; ".join(n.text for n in kit.notes)
            if notes:
                self.say("status_kit_notes", {"label": kit.label, "size": kit.size,
                                              "notes": notes})
            else:
                self.say("status_kit", {"label": kit.label, "size": kit.size})
            self.kit = kit
        self.redraw()
        self.draw_figure()

    def show_diagnosis(self, diag=None) -> None:
        """The Diagnosis tab for *diag* = (label, problems, notes), or again for
        the last one: one row per problem of the guard and per reading note;
        a sound kit read without notes leaves the list empty."""
        if diag is not None:
            self.diag_kit = diag
        self.diag_list.clear()
        if self.diag_kit is None:
            self.diag_summary.setText(" ")
            return
        label, problems, notes = self.diag_kit
        for text in problems:
            self.diag_list.addItem(tr("diag_problem", text=text))
        for text in notes:
            self.diag_list.addItem(tr("diag_note", text=text))
        if problems:
            self.diag_summary.setText(tr("diag_refused", label=label, count=len(problems)))
        elif notes:
            self.diag_summary.setText(tr("diag_notes", label=label, count=len(notes)))
        else:
            self.diag_summary.setText(tr("diag_clean", label=label))

    # -- drawing ------------------------------------------------------------------

    def image_changed(self) -> None:
        key = self.image_box.currentData()
        blocker = QtCore.QSignalBlocker(self.palette_box)
        self.palette_box.clear()
        for record in palette_choices(key):
            self.palette_box.addItem(api.RECORD_NAMES[record], record)
        del blocker
        self.zones_box.setEnabled(zone_left(key) is not None)
        self.redraw()

    def select(self, image=None, palette=None) -> bool:
        if image is not None:
            i = self.image_box.findData(image)
            if i < 0:
                return False
            self.image_box.setCurrentIndex(i)
        if palette is not None:
            i = self.palette_box.findData(palette)
            if i < 0:
                return False
            self.palette_box.setCurrentIndex(i)
        return True

    def redraw(self) -> None:
        self.picture, self.grid = None, ()
        key, palette = self.image_box.currentData(), self.palette_box.currentData()
        if self.kit is None or palette is None:
            self.canvas.set_image(None, ())
            self.palette_grid.set_entries(())
            return
        self.picture = paint_choice(self.kit, key, palette)
        self.grid = self.kit.palette_grid(palette)
        self.left = zone_left(key)
        image = QtGui.QImage(self.picture.rgba, self.picture.width, self.picture.height,
                             self.picture.width * 4, QtGui.QImage.Format.Format_RGBA8888).copy()
        self.canvas.set_image(image, self.zone_rects())
        self.palette_grid.set_entries(self.grid)

    def zone_rects(self) -> tuple:
        if self.left is None or self.picture is None:
            return ()
        out = []
        right = self.left + self.picture.width
        for items, gap in ((api.ZONES, False), (api.GAPS, True)):
            for z in items:
                if self.left <= z.x < right:
                    out.append((QtCore.QRect(z.x - self.left, z.y, z.w, z.h), gap))
        return tuple(out)

    def zoom_changed(self) -> None:
        self.canvas.zoom = self.zoom_box.currentData()
        self.canvas.set_image(self.canvas.image, self.canvas.zones)

    def checker_changed(self, on: bool) -> None:
        self.canvas.checker = on
        self.canvas.update()

    def zones_changed(self, on: bool) -> None:
        self.canvas.show_zones = on
        self.canvas.update()

    # -- reading under the mouse ------------------------------------------------

    def on_pixel(self, x: int, y: int) -> None:
        if x < 0 or self.picture is None:
            self.readout.setText(" ")
            self.palette_grid.mark(-1)
            return
        index = self.picture.indices[y * self.picture.width + x]
        parts = [tr("readout_xy", x=x, y=y)]
        if self.left is not None:
            zone = api.zone_at(x + self.left, y)
            parts.append(tr("readout_zone",
                            zone=zone.name if zone is not None else tr("zone_none")))
        parts.append(describe(self.grid[index]))
        self.readout.setText(" · ".join(parts))
        self.palette_grid.mark(index)

    def on_index(self, index: int) -> None:
        if index < 0 or index >= len(self.grid):
            self.readout.setText(" ")
            return
        self.readout.setText(describe(self.grid[index]))

    # -- export -------------------------------------------------------------------

    def ask_export(self) -> None:
        if self.picture is None:
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, tr("export_title"), "",
                                                        tr("export_filter"))
        if path:
            self.export(path)

    def export(self, path: str) -> bool:
        """The image as drawn, at 1x, in RGBA."""
        image = self.canvas.image
        ok = image is not None and image.save(path, "PNG")
        self.say("status_exported" if ok else "status_not_written", {"path": path})
        return ok


# -- running --------------------------------------------------------------------

def park(window: QtWidgets.QWidget, visible: bool) -> None:
    """Put the window where the user is not, unless the user asked to see it."""
    if visible:
        window.show()
        return
    window.setAttribute(QtCore.Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
    window.move(OFF_THE_DESKTOP, OFF_THE_DESKTOP)
    window.show()
    window.move(OFF_THE_DESKTOP, OFF_THE_DESKTOP)


def combo_fit(box: QtWidgets.QComboBox) -> tuple:
    """(width of the box's text field, width of its longest item, that item):
    the field is the style's, so the arrow and the frame are not counted in."""
    opt = QtWidgets.QStyleOptionComboBox()
    box.initStyleOption(opt)
    field = box.style().subControlRect(QtWidgets.QStyle.ComplexControl.CC_ComboBox, opt,
                                       QtWidgets.QStyle.SubControl.SC_ComboBoxEditField, box)
    metrics = box.fontMetrics()
    texts = [box.itemText(i) for i in range(box.count())] or [""]
    longest = max(texts, key=metrics.horizontalAdvance)
    return field.width(), metrics.horizontalAdvance(longest), longest


def settle(app: QtWidgets.QApplication, frames: int = FRAMES) -> None:
    for _ in range(frames):
        app.processEvents()


def parse_point(text: str):
    try:
        x, y = (int(v) for v in text.split(","))
    except ValueError:
        raise argparse.ArgumentTypeError("X,Y in image pixels, e.g. 15,10")
    return x, y


def hover(app, window, point) -> int:
    """A real mouse move over image pixel *point*, at the zoom shown, through
    the canvas's own event handler.  Prints the readout and the marked palette
    index; 1 when the readout is blank (the point is off the image)."""
    zoom = window.canvas.zoom
    local = QtCore.QPointF(point[0] * zoom + zoom / 2, point[1] * zoom + zoom / 2)
    event = QtGui.QMouseEvent(QtCore.QEvent.Type.MouseMove, local,
                              QtCore.QPointF(window.canvas.mapToGlobal(local.toPoint())),
                              QtCore.Qt.MouseButton.NoButton, QtCore.Qt.MouseButton.NoButton,
                              QtCore.Qt.KeyboardModifier.NoModifier)
    QtWidgets.QApplication.sendEvent(window.canvas, event)
    settle(app, 1)
    text = window.readout.text().strip()
    print("  readout: %s" % (text or "(blank)"))
    print("  marked: %d" % window.palette_grid.marked)
    return 0 if text else 1


def walk(app, window, plant=None) -> int:
    """Every tag x every image x every palette that goes with it, through the
    window's own selectors.  Prints the count; 1 on any exception.  *plant*
    names a tag whose drawing is made to raise: the count has to see it."""
    tags = window.tags() or [None]
    drawn = refused = 0
    errors = []
    for tag in tags:
        try:
            if tag is not None:
                window.select_tag(tag)
            if window.kit is None:
                refused += 1
                continue
            if tag == plant:
                window.kit = None
                window.select(image=WORK[1])     # draws nothing for a kit it lost
            for _, key in image_choices():
                window.select(image=key)
                for record in palette_choices(key):
                    window.select(palette=record)
                    if window.picture is None:
                        raise RuntimeError("nothing drawn for %r / %r" % (key, record))
                    drawn += 1
            settle(app, 1)
        except Exception as exc:  # the count is the point: report every one
            errors.append("%s: %s: %s" % (tag, type(exc).__name__, exc))
    for e in errors:
        print("  EXCEPTION  %s" % e)
    print("walked %d tag(s): %d picture(s) drawn, %d kit(s) refused, %d exception(s)"
          % (len(tags), drawn, refused, len(errors)))
    return 1 if errors else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="The kit viewer's window.")
    parser.add_argument("path", nargs="?", help="a disc image, a cue sheet or a lone TEX")
    parser.add_argument("--tag", help="the kit to show (disc only), e.g. A4")
    parser.add_argument("--image", type=parse_image,
                        help="%s, or an image record number" % " or ".join(WORK))
    parser.add_argument("--palette", type=int, help="a palette record that goes with the image")
    parser.add_argument("--zoom", type=int, choices=ZOOMS)
    parser.add_argument("--zones", action="store_true", help="draw the zone map")
    parser.add_argument("--no-checker", action="store_true")
    parser.add_argument("--export", metavar="PNG", help="write the image shown, at 1x, and exit")
    parser.add_argument("--screenshot", metavar="PNG", help="write the window and exit")
    parser.add_argument("--walk", action="store_true",
                        help="draw every tag, image and palette, count, and exit")
    parser.add_argument("--plant", metavar="TAG",
                        help="with --walk: lose that tag's kit mid-walk, which has to be counted")
    parser.add_argument("--hover", metavar="X,Y", type=parse_point,
                        help="move the mouse over that image pixel, print the readout, and exit")
    parser.add_argument("--visible", action="store_true",
                        help="show the window on the desktop (not for gates)")
    parser.add_argument("--lang", choices=i18n.LANGUAGES,
                        help="the window's language (default: $%s, else %s)"
                        % (i18n.ENV, i18n.DEFAULT))
    parser.add_argument("--tab", choices=TAB_NAMES, default=TAB_NAMES[0],
                        help="the tab shown")
    parser.add_argument("--kit-set", type=int, choices=(1, 2), default=1,
                        help="3D: the kit, 1 home or 2 away")
    parser.add_argument("--figure", type=int, choices=(0, 1, MATCH_FIGURE), default=0,
                        help="3D: 0 the player, 1 the goalkeeper, %d the match player"
                        % MATCH_FIGURE)
    parser.add_argument("--armband", action="store_true",
                        help="3D: tick Captain armband")
    parser.add_argument("--long-sleeves", action="store_true",
                        help="3D: tick Long sleeves")
    parser.add_argument("--number", type=int, metavar="N",
                        help="3D: tick Number, with N in its field")
    parser.add_argument("--list-3d", action="store_true",
                        help="print the 3D tab's dressing boxes (shown, enabled, ticked, "
                        "text) and exit")
    parser.add_argument("--yaw", type=float, help="3D: turn about the vertical, degrees "
                        "(default: facing the viewer)")
    parser.add_argument("--pitch", type=float, help="3D: tilt, degrees")
    parser.add_argument("--reset", action="store_true",
                        help="3D: after --yaw/--pitch, press Reset view")
    parser.add_argument("--double-click", action="store_true",
                        help="3D: after --yaw/--pitch, double-click the figure's view")
    parser.add_argument("--list-diagnosis", action="store_true",
                        help="print the Diagnosis tab of the kit shown (summary and rows) and exit")
    parser.add_argument("--list-kits", action="store_true",
                        help="print the kit selector's items, one per line, and exit")
    parser.add_argument("--export-3d", metavar="PNG",
                        help="3D: write the core's drawing of the figure at the view's size "
                        "and turn, over the backdrop, and print where the view is and how "
                        "long one frame of it takes")
    parser.add_argument("--list-combos", action="store_true",
                        help="after --switch-to, print each combo's text field width and "
                        "its longest item's, and exit")
    parser.add_argument("--switch-to", choices=i18n.LANGUAGES, metavar="LANG",
                        help="once everything is set, pick LANG in the window's own "
                        "language selector, as a click would")
    args = parser.parse_args(argv)
    try:
        i18n.set_language(i18n.chosen(args.lang))
    except i18n.UnknownLanguage as exc:
        print("%s: %s" % (i18n.ENV, exc), file=sys.stderr)
        return 2

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv[:1])
    apply_style(app)
    window = Window()
    window.resize(980, 640)
    park(window, args.visible)
    if args.path and not window.open_path(args.path):
        print("could not open %s: %s" % (args.path, window.status.text()), file=sys.stderr)
        return 1
    if args.list_kits:
        for i in range(window.tag_box.count()):
            print("  kit %d: %s" % (i, window.tag_box.itemText(i)))
        return 0
    if args.tag and not window.select_tag(args.tag):
        print("no kit %s in %s" % (args.tag, args.path), file=sys.stderr)
        return 2
    if args.list_diagnosis:
        print("  diagnosis: %s" % window.diag_summary.text())
        for i in range(window.diag_list.count()):
            print("  row %d: %s" % (i, window.diag_list.item(i).text()))
        return 0
    if not window.select(image=args.image):
        print("no image %r" % args.image, file=sys.stderr)
        return 2
    if not window.select(palette=args.palette):
        print("palette %r does not go with image %r; it takes %s"
              % (args.palette, window.image_box.currentData(),
                 palette_choices(window.image_box.currentData())), file=sys.stderr)
        return 2
    if args.zoom:
        window.zoom_box.setCurrentIndex(ZOOMS.index(args.zoom))
    window.zones_box.setChecked(args.zones)
    window.checker_box.setChecked(not args.no_checker)
    window.set_box.setCurrentIndex(args.kit_set - 1)
    window.figure_box.setCurrentIndex(args.figure)
    window.armband_box.setChecked(args.armband)
    window.long_box.setChecked(args.long_sleeves)
    if args.number is not None:
        window.number_spin.setValue(args.number)
        window.number_box.setChecked(True)
    window.dressings()
    if args.list_3d:
        boxes = {"number": window.number_box, "armband": window.armband_box,
                 "long sleeves": window.long_box}
        for name, box in boxes.items():
            print("  box %s: shown %s, enabled %s, ticked %s, text %s"
                  % (name, not box.isHidden(), box.isEnabled(), box.isChecked(), box.text()))
        print("  kit selector: %s: %s" % (
            window.figure_labels["kit_set"].text(),
            " | ".join(window.set_box.itemText(i) for i in range(window.set_box.count()))))
        return 0
    window.figure_view.turn_to(window.figure_view.yaw if args.yaw is None else args.yaw,
                               window.figure_view.pitch if args.pitch is None else args.pitch)
    if args.reset:
        window.reset_button.click()
    if args.double_click:
        from PySide6 import QtTest
        QtTest.QTest.mouseDClick(window.figure_view, QtCore.Qt.MouseButton.LeftButton)
    if TAB_NAMES.index(args.tab) == 1:
        if not window.tabs.isTabEnabled(1):
            print("the 3D tab is off: %s" % window.figure_note.text(), file=sys.stderr)
            return 3
        window.tabs.setCurrentIndex(1)
    elif TAB_NAMES.index(args.tab) == 2:
        window.tabs.setCurrentIndex(2)
    if args.switch_to:
        # A click comes after the window has been laid out and shown: without
        # this the combos would first be sized in LANG, and a combo that keeps
        # its first width would pass unseen (K3D-TASK-02).
        settle(app)
        window.language_box.setCurrentIndex(i18n.LANGUAGES.index(args.switch_to))
    settle(app)
    if args.list_combos:
        for name, box in window.combos().items():
            field, longest, text = combo_fit(box)
            print("  combo %s: field %d, longest %d, %r" % (name, field, longest, text))
        return 0

    if args.walk:
        return walk(app, window, args.plant)
    if args.hover:
        return hover(app, window, args.hover)
    if args.export_3d:
        view = window.figure_view
        if view.scene is None:
            print("the 3D tab has no figure to draw", file=sys.stderr)
            return 1
        started = time.perf_counter()
        drawn = api.draw_figure(view.scene, view.yaw, view.pitch, view.width(), view.height())
        frame_ms = (time.perf_counter() - started) * 1000.0
        if not composed(drawn).save(args.export_3d):
            print("could not write %s" % args.export_3d, file=sys.stderr)
            return 1
        at = view.mapTo(window, QtCore.QPoint(0, 0))
        print("  3d view: at %d,%d, %dx%d, yaw %g, pitch %g, frame %.0f ms"
              % (at.x(), at.y(), view.width(), view.height(), view.yaw, view.pitch, frame_ms))
    pictures = args.export or args.screenshot or args.export_3d
    if args.export and not window.export(args.export):
        print("could not write %s" % args.export, file=sys.stderr)
        return 1
    if args.screenshot:
        picture = window.grab()
        if not picture.save(args.screenshot):
            print("could not write %s" % args.screenshot, file=sys.stderr)
            return 1
        print("  wrote %s, %dx%d" % (args.screenshot, picture.width(), picture.height()))
    if pictures:
        print("  %s · image %s · palette %s · %s"
              % (window.tag_box.currentText() or "lone TEX", window.image_box.currentText(),
                 window.palette_box.currentText(), window.status.text()))
        print("  window %s, at %d,%d" % ("up" if window.isVisible() else "NOT up",
                                         window.x(), window.y()))
        return 0
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
