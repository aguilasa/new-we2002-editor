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
    # plan 1.13, the table counts and digests of 1.6, the LZSS containers of
    # 1.14, and the appendix docs/PES2-NOMES.md against the disc; WE2002_PES2_IMAGE_B, _CARD and
    # _TMPDIR add the release diff, the memory-card alignment and the
    # negative control. Without WE2002_PES2_IMAGE it reports itself skipped,
    # the same way the golden tests do.
    add_test(NAME pes2_image
        COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/../tools/pes2/check_image.py)
    set_tests_properties(pes2_image PROPERTIES
        SKIP_RETURN_CODE 77
        TIMEOUT 600)
endif()

# Booting the game is a third cost bracket: it needs DuckStation, an X
# display and about ninety seconds of wall clock. Registered anyway, on the
# same terms as the golden tests -- it skips itself unless PES2_IMAGE names
# a working copy, so a machine without the emulator sees a skip and not a
# failure. Never runs in CI, for the same reason golden does not.
if(UNIX)
    add_test(NAME pes2_boot
        COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/../tools/pes2/boot_check.sh)
    set_tests_properties(pes2_boot PROPERTIES
        SKIP_RETURN_CODE 77
        TIMEOUT 600)
endif()
