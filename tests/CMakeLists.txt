add_executable(we2002_tests
    test_main.cpp
)
target_link_libraries(we2002_tests PRIVATE we2002::core)
add_test(NAME core COMMAND we2002_tests)

# Headless half of the phase 3 golden tests. The other half is ed.exe under
# Wine, driven by tools/golden_run.sh; tools/golden_compare.py diffs the two.
add_executable(we2002_golden_tool
    golden_tool.cpp
)
target_link_libraries(we2002_golden_tool PRIVATE we2002::core)

if(MSVC)
    # std::getenv is one of the functions MSVC reports as C4996 "deprecated".
    # Same answer as in src/core: silence it rather than rewrite around it.
    target_compile_definitions(we2002_tests PRIVATE _CRT_SECURE_NO_WARNINGS)
    target_compile_definitions(we2002_golden_tool PRIVATE _CRT_SECURE_NO_WARNINGS)
endif()

# Both golden tests are driven by bash scripts that need Wine, xdotool and an X
# display. None of that exists on Windows, and ctest does not fail them there
# gracefully -- it cannot execute a .sh at all, so they come out as errors
# rather than as skips. Register them on UNIX only; the Windows equivalent is
# the transitivity check in section 5 of docs/PLAN-WINDOWS.md, which compares
# the SHA-256 of a `we2002_golden_tool roundtrip` against the one produced by
# the GCC build. we2002_golden_tool itself is built everywhere, because that
# check is what uses it.
if(UNIX)
    # The golden test proper. It needs three things the repository cannot carry:
    # a ~474 MB CD image, the prebuilt Debug/ed.exe, and a working Wine plus an X
    # display. Point WE2002_GOLDEN_IMAGE at an image to enable it; without that it
    # reports itself skipped rather than failing.
    add_test(NAME golden
        COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/../tools/golden_check.sh
                "" $<TARGET_FILE:we2002_golden_tool>)
    set_tests_properties(golden PROPERTIES
        SKIP_RETURN_CODE 77
        TIMEOUT 900)

    # The same comparison with the Qt window on the port side instead of the
    # headless tool. `golden` proves the core writes what ed.exe writes; this
    # proves the widget layer between the two does not change the answer. Skips
    # itself when the app was not built (no Qt6).
    if(TARGET newWe2002)
        add_test(NAME golden_gui
            COMMAND ${CMAKE_COMMAND} -E env
                    WE2002_GOLDEN_MODE=gui
                    WE2002_GOLDEN_APP=$<TARGET_FILE:newWe2002>
                    ${CMAKE_CURRENT_SOURCE_DIR}/../tools/golden_check.sh)
        set_tests_properties(golden_gui PROPERTIES
            SKIP_RETURN_CODE 77
            TIMEOUT 1200)
    endif()
endif()

# The .ui forms are generated from legacy/mfc/ed.rc and committed. This checks
# they are still what the converter produces -- editing a .ui by hand, or
# touching ed.rc without regenerating, fails here rather than silently at some
# point in phase 5. Also revalidates the XML, so a malformed emit is caught
# without Qt installed.
find_package(Python3 COMPONENTS Interpreter)
if(Python3_FOUND)
    add_test(NAME ui_forms
        COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/../tools/rc2ui.py --check)

    # Phase 3.5 banned Italian identifiers from the core and phase 5.5 from
    # the application, including the widget names. Both maps live in
    # tools/glossary.py; this fails if one of them stops being applied.
    add_test(NAME glossary
        COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/../tools/apply_glossary.py --check)

    # The prompts under docs/prompts/ are project-agnostic: they read the
    # progress files and each task states its own source of truth in the
    # `fonte_de_verdade` frontmatter field. This enforces the four conventions
    # that make that work -- see .claude/rules/tasks.md.
    add_test(NAME tasks
        COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/../tools/check_tasks.py)

    # PES2 (docs/PLAN-PES2-PSX.md) is a separate project that shares no code
    # with we2002_core, but its tools are Python and belong in the same run.
    #
    # Two tests, because the two things worth guarding have very different
    # costs. The self-test builds a 24-sector disc in a temporary directory
    # and exercises the sector arithmetic, the Form 1 / Form 2 split and the
    # three refusals of iso.py -- it needs nothing and runs everywhere.
    add_test(NAME pes2_selftest
        COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/../tools/pes2/selftest.py)

    # The other needs a ~445 MiB disc image, which the repository cannot
    # carry. Point WE2002_PES2_IMAGE at one and it re-measures the anchors of
    # plan 1.13, the table counts and digests of 1.6, the LZSS containers and
    # the image/CLUT index of 1.14, and docs/PES2-NOMES.md against the disc; WE2002_PES2_IMAGE_B, _CARD and
    # _TMPDIR add the release diff, the memory-card alignment, the
    # negative control and the asset write path of 6.7. Without WE2002_PES2_IMAGE it reports itself skipped,
    # the same way the golden tests do.
    add_test(NAME pes2_image
        COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/../tools/pes2/check_image.py)
    set_tests_properties(pes2_image PROPERTIES
        SKIP_RETURN_CODE 77
        TIMEOUT 600)

    # The .mcr editor port (docs/PLAN-MCR-PY.md) is a fifth project: Python 3
    # for the core, PySide6 in a venv for the UI, and no build shared with
    # anything. Three targets, one per cost bracket -- section 4.4 of the plan.
    #
    # The mandatory one needs nothing. Every module builds the card it needs in
    # memory, and selftest.py unsets WE2002_MCR_CARD before calling any of
    # them, so this runs the same on a machine that has never seen a memory
    # card. It also plants every negative control and demands each one go red
    # -- a guard that has never been red is decoration. How many there are is
    # what controls.py prints, not something spelled out here: CORR-MCR-017
    # measured what a copied number costs.
    add_test(NAME mcr_selftest
        COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/../tools/mcr/selftest.py)
    set_tests_properties(mcr_selftest PROPERTIES TIMEOUT 300)

    # The second needs a real 128 KiB card. Point WE2002_MCR_CARD at one and it
    # re-measures the round-trip in both forms, the two copies of every shirt
    # number, the 17 destinations against wte/re/mcr.md and the upstream's
    # label and weight tables when work/easy-mcr is there. Without the variable
    # it reports itself skipped, the same way the golden tests do. It never
    # writes the card it is given -- the last check re-reads it to prove it.
    add_test(NAME mcr_card
        COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/../tools/mcr/cli.py check)
    set_tests_properties(mcr_card PROPERTIES
        SKIP_RETURN_CODE 77
        TIMEOUT 600)

    # The container gate (MCR-TASK-16), and it is the ONLY one of this cycle
    # that needs no WE2002_MCR_CARD: its input is the eight DexDrive .gme
    # committed under mcr/, so any clone can run it. It takes each one apart
    # and puts it back together and demands the same bytes -- which is what
    # proves the 3,904-byte header is PRESERVED and not regenerated, three of
    # the eight carrying a header of zeros that no synthesis makes. It skips
    # with 77 if the directory is not there, the same convention as the rest.
    add_test(NAME mcr_container
        COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/../tools/mcr/gme.py --check)
    set_tests_properties(mcr_container PROPERTIES
        SKIP_RETURN_CODE 77
        TIMEOUT 120)
endif()

# The third mcr bracket needs the venv with PySide6 and an X display, which is
# the same class of dependency as the golden tests -- so it is UNIX-only and
# skips itself when the venv, the UI or the display is missing. Since
# MCR-TASK-11 it passes; since MCR-TASK-12 it also drives the widgets, writes
# two cards and checks their round-trip -- but only when WE2002_MCR_CARD names
# a card. Without it the target still passes on the window alone, and says so.
if(UNIX AND Python3_FOUND)
    add_test(NAME mcr_ui
        COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/../tools/mcr/ui_check.py)
    set_tests_properties(mcr_ui PROPERTIES
        SKIP_RETURN_CODE 77
        TIMEOUT 300)
endif()

# Booting the PES2 game is that project's third cost bracket: it needs
# DuckStation, an X display and about ninety seconds of wall clock. Registered
# anyway, on the same terms as the golden tests -- it skips itself unless
# PES2_IMAGE names a working copy, so a machine without the emulator sees a
# skip and not a failure. Never runs in CI, for the same reason golden does not.
if(UNIX)
    add_test(NAME pes2_boot
        COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/../tools/pes2/boot_check.sh)
    set_tests_properties(pes2_boot PROPERTIES
        SKIP_RETURN_CODE 77
        RESOURCE_LOCK duckstation
        TIMEOUT 600)
endif()

# The appearance viewer (docs/PLAN-LOOKS-PY.md) is the sixth project: Python 3
# in tools/looks/, PySide6 in a venv of its own, no build shared with anything.
#
# All four targets sit inside if(Python3_FOUND) like the other eight Python tests
# above. They did not, and the one that suffers is the mandatory gate: with no
# Python found, ${Python3_EXECUTABLE} expands to nothing, the command becomes
# the bare .py path, and looks_selftest reports FAILED -- sending whoever reads
# it into tools/looks/ to find a defect that is really a missing interpreter.
# Its eight siblings simply do not appear, which is the right answer
# (CORR-LOOKS-016).
if(Python3_FOUND)
    # The mandatory gate. It needs NOTHING -- no image, no venv, no display --
    # and it must never skip its way to green: it runs every module's
    # self-check, sweeps the three design rules of section 3.3, and plants
    # every negative control, demanding each one go red. A guard that has never
    # gone red is decoration.
    #
    # It drops WE2002_LOOKS_IMAGE from its own environment on purpose. With the
    # variable set a module could take a path that does not exist on a clean
    # machine, and the gate would be green here and red there.
    add_test(NAME looks_selftest
        COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/../tools/looks/selftest.py --quiet)
    set_tests_properties(looks_selftest PROPERTIES TIMEOUT 300)

    # The image gate, registered in CORR-LOOKS-012 rather than in
    # LOOKS-TASK-19, because the cycle profile promised it from LOOKS-TASK-05
    # and a promised target that does not exist is worse than a missing one:
    # `ctest -R looks` answered "No tests were found!!!" and exited ZERO, which
    # reads exactly like green. The 19 closes the count; it no longer creates
    # all three.
    #
    # It re-derives, against the real disc, what phase 1 measured: MODEL.BIN's
    # 106 sections from 1816 and EDT_MOD.BIN's 20 from 216 -- 216 derived from
    # the pointer lists, not typed -- the two models of eleven with their
    # mirrored pairs, and that neither list is in file order. Its first read is
    # a Japanese-only file through the two-disc guard, because geometry is
    # identical on both discs: without that read, pointing WE2002_LOOKS_IMAGE
    # at the English translation would pass in silence, and that is the error
    # this cycle exists to make impossible. Without the variable it skips with
    # 77 and names it.
    #
    # Since LOOKS-TASK-19 it runs `cli.py check`: modelfile's check and the
    # seven other modules that grew a --check-image of their own (texture,
    # atlas, skin, looks, assembly, pieces, scene), all run to the end, so the
    # order is for reading and not a guard (CORR-LOOKS-052). Until then
    # this target ran one of eight, and green here said nothing about the
    # palette list, the atlas or the assembly table. The list is not trusted to
    # stay whole: cli.py's self-check reads the sources for every module that
    # answers --check-image and fails when one is missing from the run. A
    # module that skips while the others ran fails the target too.
    add_test(NAME looks_image
        COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/../tools/looks/cli.py check)
    set_tests_properties(looks_image PROPERTIES
        SKIP_RETURN_CODE 77
        TIMEOUT 300)

    # The third bracket, and the dearest: it needs the venv with PySide6, the
    # disc AND a place to put a window. It draws three tuples through the real
    # window, decodes the PNGs in the standard library -- not through the code
    # under test -- and demands that two tuples differing in one field come out
    # as different pictures, that the same tuple twice come out identical, and
    # that a tuple the assembly table refuses exit 2 with nothing written.
    #
    # It is NOT if(UNIX). The window runs on this Windows machine with no Xvfb,
    # parked at -32000 the way CLAUDE.md says; on Linux the same file sets
    # DISPLAY=:98 and resolves XAUTHORITY like `make run-98`.
    #
    # Missing any of the four things makes it skip with 77 and name what is
    # gone. What it must never do is pass with a `note:` about what it could
    # not measure -- that is the shape `mcr_ui` had, green with the window
    # alone whenever the fixture was missing (section 4.4 of the plan).
    add_test(NAME looks_ui
        COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/../tools/looks/ui_check.py)
    set_tests_properties(looks_ui PROPERTIES
        SKIP_RETURN_CODE 77
        TIMEOUT 600)

    # The fourth bracket, added by LOOKS-TASK-19: the game itself. It boots the
    # DuckStation fork with the MCP server, restores the cycle's two save
    # states, proves by the picture which one loaded and that the wrong one is
    # refused, compares both model files in RAM with the disc, and presses one
    # key. It existed since LOOKS-TASK-07 as `oracle.py --check-live` and was in
    # no target -- a gate only whoever remembered it ran, which is the shape
    # CORR-LOOKS-012 was opened for. Its time is in the LOOKS-TASK-19 log.
    #
    # Every prerequisite is checked BEFORE a process starts (oracle.PREREQUISITES):
    # WE2002_LOOKS_DRIVE_IMAGE (the English .cue), WE2002_LOOKS_IMAGE (the
    # Japanese .bin), the two states under work/looks-states/, and then the
    # fork at launch. Missing any is a skip with 77 that names it. The window
    # goes off the desktop at once (-32000 on Windows), and the emulator is
    # killed on the way out.
    #
    # It writes one thing outside this tree, and it is worth knowing: when the
    # emulator's own slot 1 or 2 differs from the project copy, the copy is put
    # back there, loudly.
    add_test(NAME looks_live
        COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/../tools/looks/oracle.py --check-live)
    # DuckStation keeps ONE data directory, so one instance at a time across
    # the whole repository -- the same lock sits on pes2_boot.
    set_tests_properties(looks_live PROPERTIES
        SKIP_RETURN_CODE 77
        RESOURCE_LOCK duckstation
        TIMEOUT 600)
endif()
