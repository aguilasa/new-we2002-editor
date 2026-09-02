#!/usr/bin/env python3
"""Send one pad action to an already-running DuckStation, and look at it.

`drive.py` runs a whole route and shuts the emulator down after it. This is
for the other way of working: the emulator stays up -- on the user's own
display, where they can see it -- and one action is sent at a time, with a
person deciding the next one. It is what the routes get written *from*.

    tools/pes2/run_duckstation.sh            # PES2_DISPLAY=:1, leaves it up
    python3 tools/pes2/pad.py press cross
    python3 tools/pes2/pad.py press down down cross
    python3 tools/pes2/pad.py shot /tmp/a.png
    python3 tools/pes2/pad.py stats            # mean/sd, and the top band
    python3 tools/pes2/pad.py watch 20         # is anything moving?
    python3 tools/pes2/pad.py run 600          # fast forward, and
                                               # give every kickoff

Buttons are pad names -- cross, circle, square, triangle, start, select,
up, down, left, right, l1, r1 -- plus the hotkeys fast-forward, save-state,
load-state and pause. The keys they map to are read from the emulator's own
configuration, and the press is held for as long as that kind of button
needs; both are drive.py's doing and neither is guessable.

    PES2_DISPLAY   which display to talk to, default :98
    PES2_WINDOW    window id, if the search finds the wrong one
"""

import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import drive                                                  # noqa: E402


def env_for(display):
    env = dict(os.environ, DISPLAY=display)
    # Same split as the launcher: the headless server has no cookie, the
    # user's own display does and needs it.
    if display == ":98":
        env["XAUTHORITY"] = ""
    return env


def client_of(window, env):
    """The window the game actually draws into.

    On a display with a window manager the search finds the *frame*, and
    capturing that includes the title bar: 894x785 instead of 800x655, which
    silently invalidates every crop measured on the headless display -- the
    clock and the top band both land on the wrong pixels. The client is a
    child with the same name.
    """
    out = subprocess.run(["xwininfo", "-id", window, "-children"],
                         env=env, capture_output=True, text=True).stdout
    for line in out.splitlines():
        line = line.strip()
        if not line.startswith("0x") or "Pro Evolution Soccer 2" not in line:
            continue
        child = line.split()[0]
        if child != window:
            return child
    return window


def find_window(display):
    if os.environ.get("PES2_WINDOW"):
        return os.environ["PES2_WINDOW"]
    env = env_for(display)
    out = subprocess.run(
        ["xdotool", "search", "--name", "^Pro Evolution Soccer 2$"],
        env=env, capture_output=True, text=True)
    for w in out.stdout.split():
        pid = subprocess.run(["xprop", "-id", w, "_NET_WM_PID"], env=env,
                             capture_output=True, text=True).stdout.split()
        if pid and pid[-1].isdigit() and os.path.exists(f"/proc/{pid[-1]}"):
            return client_of(w, env)
    raise SystemExit(f"no live game window on {display} -- is it running?")


class Live:
    """A session that attaches instead of booting, so nothing is lost
    between commands."""

    def __init__(self, display, window):
        self.display = display
        self.window = window
        self.verbose = True
        self._tmp = "/tmp"

    say = drive.Session.say
    press = drive.Session.press
    _aim = drive.Session._aim

    def _xdotool(self, *args):
        return subprocess.run(["xdotool", *args], env=env_for(self.display),
                              capture_output=True, text=True)

    def capture(self, path=None):
        path = path or os.path.join(
            "/tmp", f"pes2-live-{time.time():.3f}.png")
        r = subprocess.run(["import", "-window", self.window, path],
                           env=env_for(self.display), capture_output=True,
                           text=True)
        if r.returncode != 0 or not os.path.exists(path):
            raise SystemExit(f"capture failed: {r.stderr.strip()}")
        return drive.Frame(path)


BAND = (0, 60, 800, 200)          # the strip that tells kickoff apart
CLOCK = (560, 90, 760, 130)       # the match clock


def describe(frame):
    if frame.size != (800, 655):
        print(f"  aviso: janela {frame.size[0]}x{frame.size[1]}, nao 800x655"
              f" -- os recortes do relogio e da faixa nao valem",
              file=sys.stderr)
    m, sd = frame.stats()
    bm, bsd = frame.stats(BAND)
    return (f"mean={m:.4f} sd={sd:.4f}   band mean={bm:.4f} sd={bsd:.4f}"
            f"   {'preto' if frame.is_black() else ''}")


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    display = os.environ.get("PES2_DISPLAY", ":98")
    window = find_window(display)
    live = Live(display, window)
    cmd, rest = argv[0], argv[1:]

    if cmd == "press":
        if not rest:
            raise SystemExit("press what? see --help for the button names")
        for button in rest:
            if button not in drive.PAD and button not in drive.HOTKEY:
                raise SystemExit(f"unknown button {button!r}")
        for button in rest:
            live.press(button)
            time.sleep(0.8)
        print(describe(live.capture()))

    elif cmd == "shot":
        path = rest[0] if rest else "/tmp/pes2.png"
        frame = live.capture(path)
        print(f"{path}\n{describe(frame)}")

    elif cmd == "stats":
        print(describe(live.capture()))

    elif cmd == "watch":
        seconds = float(rest[0]) if rest else 10
        a = live.capture()
        time.sleep(seconds)
        b = live.capture()
        print(f"em {seconds:g}s:  tela {b.difference(a):.5f}   "
              f"relogio {b.difference(a, CLOCK):.5f}   "
              f"(relogio 0 = partida parada)")
        print(describe(b))

    elif cmd == "run":
        # Acelerar e esperar nao termina uma partida: **todo gol devolve um
        # saque que espera Cross**, e uma corrida que so segura o Tab para
        # no primeiro gol parecendo que a partida nao acaba -- foi assim que
        # um "onze minutos de fast-forward nao terminaram a partida" entrou
        # num documento. Medido em 2026-09-02 com o usuario olhando a tela.
        budget = float(rest[0]) if rest else 600
        key = drive.HOTKEY["fast-forward"]
        live._aim()
        live._xdotool("keydown", key)
        held = True
        t0 = time.time()
        passes = 0
        try:
            previous = live.capture()
            while time.time() - t0 < budget:
                time.sleep(6)
                current = live.capture()
                m, sd = current.stats()
                elapsed = int(time.time() - t0)
                if not (0.20 < m < 0.36):
                    print(f"  {elapsed}s: saiu do gramado  mean={m:.4f} "
                          f"sd={sd:.4f}", flush=True)
                    break
                if current.difference(previous, CLOCK) < 0.001:
                    live._xdotool("keyup", key)
                    held = False
                    live.press("cross")
                    passes += 1
                    print(f"  {elapsed}s: congelado -> Cross ({passes})",
                          flush=True)
                    time.sleep(2)
                    live._aim()
                    live._xdotool("keydown", key)
                    held = True
                    current = live.capture()
                previous = current
            else:
                print(f"  ainda no gramado apos {int(budget)}s", flush=True)
        finally:
            if held:
                live._xdotool("keyup", key)
        print(f"  {passes} saque(s) dado(s)")
        print(describe(live.capture()))

    else:
        raise SystemExit(f"unknown command {cmd!r}; see --help")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
