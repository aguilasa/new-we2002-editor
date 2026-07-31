cmake_minimum_required(VERSION 3.21)
project(we2002
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
set(WE2002_APPDATADIR "${CMAKE_INSTALL_DATADIR}/we2002"
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
    message(STATUS "we2002: Qt6 GUI not built -- install qt6-base-dev")
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

install(FILES "${CMAKE_CURRENT_SOURCE_DIR}/packaging/io.github.aguilasa.we2002.desktop"
    DESTINATION "${CMAKE_INSTALL_DATADIR}/applications")
install(FILES "${CMAKE_CURRENT_SOURCE_DIR}/packaging/io.github.aguilasa.we2002.metainfo.xml"
    DESTINATION "${CMAKE_INSTALL_DATADIR}/metainfo")

# 16x16 and 32x32 are the only sizes legacy/mfc/res/ed.ico holds. A scaled-up
# 48 or 256 would be invented art, so there is none.
foreach(size 16 32)
    install(FILES "${CMAKE_CURRENT_SOURCE_DIR}/src/app/resources/we2002-${size}.png"
        DESTINATION "${CMAKE_INSTALL_DATADIR}/icons/hicolor/${size}x${size}/apps"
        RENAME we2002.png)
endforeach()

# The documents that say what may and may not be done with this code. Shipping
# a build without them would be worse than shipping no build.
install(FILES
    "${CMAKE_CURRENT_SOURCE_DIR}/NOTICE.md"
    "${CMAKE_CURRENT_SOURCE_DIR}/README.md"
    DESTINATION "${CMAKE_INSTALL_DOCDIR}")
