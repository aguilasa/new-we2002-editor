cmake_minimum_required(VERSION 3.21)
# The project name is the name of the *product*: the installed executable, the
# data directory, share/doc/. It is deliberately not the same as the C++
# namespace, the core library or the WE2002_* variables, which are all named
# after the game and its image format rather than after this editor.
project(newWe2002
    VERSION 0.1.0
    DESCRIPTION "Cross-platform editor for Winning Eleven 2002 PSX CD images"
    LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
    set(CMAKE_BUILD_TYPE Debug CACHE STRING "" FORCE)
endif()

# The inherited code assumes char is SIGNED, which is the default for MSVC and
# for GCC/Clang on x86 but NOT on ARM. Pin it.
# MSVC needs no flag (/J would invert it and break everything) but does need
# /utf-8, since the sources were converted to UTF-8 in phase 1.
if(MSVC)
    add_compile_options(/utf-8)

    # we2002::Database is 1.21 MB -- players[1911] alone is 1.17 MB, since the
    # 2002 code held the whole database in file-scope arrays and the port kept
    # the layout. Every one of them is declared as a local: golden_tool does,
    # the unit tests do, and MainWindow holds one by value.
    #
    # Linux reserves 8 MB of stack per thread and never noticed. MSVC reserves
    # 1 MB, so the very first `Database db;` overflows before main() gets
    # anywhere -- STATUS_STACK_OVERFLOW, exit code 0xC00000FD, and not one byte
    # of output. Reserve the same 8 MB the code was written against rather than
    # move the object to the heap in a dozen places: this changes no semantics
    # and keeps the two platforms running identical source.
    add_link_options(/STACK:8388608)
else()
    add_compile_options(-fsigned-char)
endif()

option(WE2002_SANITIZE "Build with sanitizers" OFF)
set(WE2002_SANITIZERS "address,undefined" CACHE STRING
    "Comma-separated -fsanitize list used when WE2002_SANITIZE=ON")

# NOTE for this development machine: AddressSanitizer does not run here.
# Citrix installs /usr/local/lib/AppProtection/libAppProtection.so into
# /etc/ld.so.preload, which loads before anything else and makes ASan die on
# startup -- even a hello-world segfaults, with or without -static-libasan.
# UBSan is unaffected. Until the preload is dealt with, use:
#     cmake -B build-ubsan -DWE2002_SANITIZE=ON -DWE2002_SANITIZERS=undefined
# CI runners have no such preload and should run the full address,undefined.
if(WE2002_SANITIZE AND NOT MSVC)
    add_compile_options(-fsanitize=${WE2002_SANITIZERS} -fno-omit-frame-pointer -g)
    add_link_options(-fsanitize=${WE2002_SANITIZERS})
endif()

include(GNUInstallDirs)

# The runtime data files. The application resolves this at run time relative to
# its own executable, not from an absolute path baked in here -- see
# src/app/DataFiles.cpp.
set(WE2002_APPDATADIR "${CMAKE_INSTALL_DATADIR}/newWe2002"
    CACHE STRING "Where the runtime .txt data files are installed")

add_subdirectory(src/core)

# The build must not require Qt: the core and its tests stay buildable on a
# machine with nothing but a compiler and libcurl, which is what lets the phase
# 3 golden tests run headless.
find_package(Qt6 QUIET COMPONENTS Widgets)
if(Qt6_FOUND)
    qt_standard_project_setup()
    add_subdirectory(src/app)
else()
    message(STATUS "newWe2002: Qt6 GUI not built -- install qt6-base-dev")
endif()

include(CTest)
if(BUILD_TESTING)
    add_subdirectory(tests)
endif()

# ---------------------------------------------------------------------------
# Install
# ---------------------------------------------------------------------------
#
# The GUI target installs itself (src/app/CMakeLists.txt); everything here is
# data. All of it is installed even without Qt6, so that packaging can be
# checked on a machine that only builds the core.

# Read at run time. naz.txt is NOT here on purpose: it is not a data file at
# all but a C array the author pasted into the tree, and nothing reads it. It
# stays in the repository as history.
install(FILES
    "${CMAKE_CURRENT_SOURCE_DIR}/data/defaultlook.txt"
    "${CMAKE_CURRENT_SOURCE_DIR}/data/SOFIFA attributes.txt"
    "${CMAKE_CURRENT_SOURCE_DIR}/data/WE attributes conversion rules.txt"
    DESTINATION "${WE2002_APPDATADIR}")

install(FILES "${CMAKE_CURRENT_SOURCE_DIR}/packaging/io.github.aguilasa.newWe2002.desktop"
    DESTINATION "${CMAKE_INSTALL_DATADIR}/applications")
install(FILES "${CMAKE_CURRENT_SOURCE_DIR}/packaging/io.github.aguilasa.newWe2002.metainfo.xml"
    DESTINATION "${CMAKE_INSTALL_DATADIR}/metainfo")

# Drawn by tools/make_icon.py. Each size is drawn at that size rather than
# scaled from one master: 16 and 24 lose the shirt's stripes, which at that size
# are a third of a pixel wide and come out as grey mush.
foreach(size 16 24 32 48 64 128 256)
    install(FILES "${CMAKE_CURRENT_SOURCE_DIR}/src/app/resources/newWe2002-${size}.png"
        DESTINATION "${CMAKE_INSTALL_DATADIR}/icons/hicolor/${size}x${size}/apps"
        RENAME newWe2002.png)
endforeach()

# The documents that say what may and may not be done with this code. Shipping
# a build without them would be worse than shipping no build.
install(FILES
    "${CMAKE_CURRENT_SOURCE_DIR}/NOTICE.md"
    "${CMAKE_CURRENT_SOURCE_DIR}/README.md"
    DESTINATION "${CMAKE_INSTALL_DOCDIR}")
