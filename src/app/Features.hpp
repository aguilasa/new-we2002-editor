// Feature switches for parts of the editor that are parked rather than gone.
//
// Nothing here is a build option: the code they gate is still compiled, still
// linked and still covered by whatever tests it had. The switch only decides
// whether the user can reach it from the window.

#pragma once

namespace app {

/// The SoFIFA import -- the fork's own addition, not part of the 2002 editor.
///
/// Parked on 2026-08-05 while the port's parity with ed.exe is being checked
/// screen by screen (docs/PARIDADE-FUNCIONAL.md): it is the least verified area
/// of the project, it depends on a website whose 2015 layout the scraper was
/// written against, and none of it is covered by the golden tests.
///
/// Turning this back to `true` is the whole of re-enabling it. What it gates:
///
///   * the three SoFIFA buttons and the edit-options button on the main dialog
///   * the 23 URL boxes
///   * "read from URL" in the player-skills dialog
///   * reading the two rule files at startup, and their missing-file warning
///
/// What it deliberately does NOT gate: reading the <image>_url.txt sidecar.
/// Database::Save() writes that file on every write, exactly as the original's
/// OnWriteCD did, so the load has to keep running or the write would blank it.
inline constexpr bool SOFIFA_ENABLED = false;

}  // namespace app
