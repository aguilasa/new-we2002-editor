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
