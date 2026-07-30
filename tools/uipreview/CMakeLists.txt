cmake_minimum_required(VERSION 3.21)
project(we2002_uipreview LANGUAGES CXX)

# Standalone on purpose: this is a phase 4 inspection tool, not part of the
# editor, and it must build on a machine that only has Qt5 -- which is the
# case here until phase 5 brings Qt6 in.
#
#   cmake -B build-uipreview -S tools/uipreview
#   cmake --build build-uipreview -j
#   DISPLAY=:99 ./build-uipreview/preview_MainDialog out.png
#
# One executable per form, because uic output is a header that has to be
# included, and the class name differs per form.

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt6 QUIET COMPONENTS Widgets)
if(Qt6_FOUND)
    set(QT Qt6)
else()
    find_package(Qt5 REQUIRED COMPONENTS Widgets)
    set(QT Qt5)
endif()
message(STATUS "uipreview: usando ${QT}")

set(UI_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../src/app/ui")
file(GLOB UI_FILES "${UI_DIR}/*.ui")
if(NOT UI_FILES)
    message(FATAL_ERROR "nenhum .ui em ${UI_DIR}; rode python3 tools/rc2ui.py")
endif()

find_program(UIC_EXE NAMES uic uic-qt6 uic6 REQUIRED)

foreach(ui IN LISTS UI_FILES)
    get_filename_component(name "${ui}" NAME_WE)
    set(gen "${CMAKE_CURRENT_BINARY_DIR}/ui_${name}.h")

    add_custom_command(
        OUTPUT "${gen}"
        COMMAND ${UIC_EXE} "${ui}" -o "${gen}"
        DEPENDS "${ui}"
        COMMENT "uic ${name}.ui"
        VERBATIM)

    # uic names the class after the form's <class> element, so the driver is
    # configured once per form rather than shared.
    set(FORM_NAME "${name}")
    configure_file(main.cpp.in "${CMAKE_CURRENT_BINARY_DIR}/main_${name}.cpp" @ONLY)

    add_executable(preview_${name}
        "${CMAKE_CURRENT_BINARY_DIR}/main_${name}.cpp" "${gen}")
    target_include_directories(preview_${name} PRIVATE "${CMAKE_CURRENT_BINARY_DIR}")
    target_link_libraries(preview_${name} PRIVATE ${QT}::Widgets)
endforeach()
