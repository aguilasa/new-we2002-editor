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

On Linux `make kits` (`make kits-98` for the Xvfb) runs it with `--visible`:
TAG=, KITS_IMAGE=, ARGS=.
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import api  # noqa: E402
from PySide6 import QtCore, QtGui, QtWidgets  # noqa: E402

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
CHECKER = ("#cfcfcf", "#f2f2f2")
BACKDROP = "#8c8c8c"
ZONE_PEN = "#e0157a"
GAP_PEN = "#1e9be0"


def fixed_palette() -> QtGui.QPalette:
    pal = QtGui.QPalette()
    for role, colour in COLOURS.items():
        pal.setColor(getattr(QtGui.QPalette.ColorRole, role), QtGui.QColor(colour))
    for role in ("WindowText", "Text", "ButtonText"):
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
    image the game pairs with a palette (`api.GAME_PAIRS`)."""
    out = [("bitmap de trabalho, 1º conjunto", WORK[0]),
           ("bitmap de trabalho, 2º conjunto", WORK[1])]
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
    return "índice %d · BGR555 0x%04x · RGB %d,%d,%d%s" % (
        entry.index, entry.bgr555, r, g, b, " · transparente" if not a else "")


class Window(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("kits")
        self.source = None
        self.kit = None
        self.picture = None              # the FlatImage on the canvas
        self.grid = ()                   # its palette as PaletteEntry
        self.left = None                 # zone_left() of the image shown

        top = QtWidgets.QHBoxLayout()
        self.open_button = QtWidgets.QPushButton("Abrir…")
        self.open_button.clicked.connect(self.ask_open)
        self.path_label = QtWidgets.QLabel("nada aberto")
        self.path_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        self.tag_box = QtWidgets.QComboBox()
        self.tag_box.setMinimumContentsLength(18)
        self.tag_box.currentIndexChanged.connect(self.load_kit)
        self.tag_box.hide()
        top.addWidget(self.open_button)
        top.addWidget(self.path_label, 1)
        top.addWidget(self.tag_box)

        self.image_box = QtWidgets.QComboBox()
        for label, key in image_choices():
            self.image_box.addItem(label, key)
        self.image_box.currentIndexChanged.connect(self.image_changed)
        self.palette_box = QtWidgets.QComboBox()
        self.palette_box.currentIndexChanged.connect(self.redraw)
        self.zoom_box = QtWidgets.QComboBox()
        for z in ZOOMS:
            self.zoom_box.addItem("%d×" % z, z)
        self.zoom_box.setCurrentIndex(ZOOMS.index(DEFAULT_ZOOM))
        self.zoom_box.currentIndexChanged.connect(self.zoom_changed)
        self.checker_box = QtWidgets.QCheckBox("Xadrez")
        self.checker_box.setChecked(True)
        self.checker_box.toggled.connect(self.checker_changed)
        self.grid_box = QtWidgets.QCheckBox("Grade 16×16")
        self.grid_box.setChecked(True)
        self.zones_box = QtWidgets.QCheckBox("Zonas")
        self.zones_box.toggled.connect(self.zones_changed)
        self.export_button = QtWidgets.QPushButton("Exportar PNG")
        self.export_button.clicked.connect(self.ask_export)

        controls = QtWidgets.QHBoxLayout()
        for text, widget in (("Imagem", self.image_box), ("Paleta", self.palette_box),
                             ("Zoom", self.zoom_box)):
            controls.addWidget(QtWidgets.QLabel(text))
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
        self.tabs.addTab(plan, "Plano")

        self.status = QtWidgets.QLabel(" ")
        self.status.setWordWrap(True)
        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central)
        layout.addLayout(top)
        layout.addWidget(self.tabs, 1)
        layout.addWidget(self.status)
        self.setCentralWidget(central)
        self.image_changed()

    # -- opening ----------------------------------------------------------------

    def ask_open(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Abrir imagem de CD ou TEX", "",
            "Imagem de CD ou TEX (*.bin *.iso *.cue *.BIN);;Todos (*)")
        if path:
            self.open_path(path)

    def open_path(self, path: str) -> bool:
        try:
            source = api.open_source(path)
        except api.KitsError as exc:
            self.status.setText(str(exc))
            return False
        self.source = source
        self.path_label.setText(path)
        blocker = QtCore.QSignalBlocker(self.tag_box)
        self.tag_box.clear()
        if source.kind == api.KIND_ROM:
            names = {}
            for team in source.teams():
                if team.tag is not None:
                    names.setdefault(team.tag, []).append(team.name)
            for tag in source.kit_tags():
                label = "TEX_%s" % tag
                if tag in names:
                    label += " — " + ", ".join(names[tag])
                self.tag_box.addItem(label, tag)
            self.tag_box.show()
        else:
            self.tag_box.hide()
        del blocker
        self.load_kit()
        return True

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
            self.status.setText(str(exc))
            self.redraw()
            return
        if not kit.ok:
            self.status.setText("%s recusado: %s" % (kit.label, "; ".join(kit.problems)))
        else:
            notes = "; ".join(n.text for n in kit.notes)
            self.status.setText("%s, %d bytes%s" % (kit.label, kit.size,
                                                   " — " + notes if notes else ""))
            self.kit = kit
        self.redraw()

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
        parts = ["x %d, y %d" % (x, y)]
        if self.left is not None:
            zone = api.zone_at(x + self.left, y)
            parts.append("zona: %s" % (zone.name if zone is not None else "nenhuma"))
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
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Exportar PNG", "", "PNG (*.png)")
        if path:
            self.export(path)

    def export(self, path: str) -> bool:
        """The image as drawn, at 1x, in RGBA."""
        image = self.canvas.image
        ok = image is not None and image.save(path, "PNG")
        self.status.setText(("exportado: %s" if ok else "não gravou %s") % path)
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
    args = parser.parse_args(argv)

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv[:1])
    apply_style(app)
    window = Window()
    window.resize(980, 640)
    park(window, args.visible)
    if args.path and not window.open_path(args.path):
        print("could not open %s: %s" % (args.path, window.status.text()), file=sys.stderr)
        return 1
    if args.tag and not window.select_tag(args.tag):
        print("no kit %s in %s" % (args.tag, args.path), file=sys.stderr)
        return 2
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
    settle(app)

    if args.walk:
        return walk(app, window, args.plant)
    if args.hover:
        return hover(app, window, args.hover)
    pictures = args.export or args.screenshot
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
        print("  %s · imagem %s · paleta %s · %s"
              % (window.tag_box.currentText() or "TEX avulso", window.image_box.currentText(),
                 window.palette_box.currentText(), window.status.text()))
        print("  window %s, at %d,%d" % ("up" if window.isVisible() else "NOT up",
                                         window.x(), window.y()))
        return 0
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
