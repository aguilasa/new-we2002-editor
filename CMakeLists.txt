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

add_subdirectory(src/core)

# The Qt application does not exist yet -- it arrives in phases 4 and 5. Until
# then the build must not require Qt, so the core and its tests stay buildable
# on a machine with nothing but a compiler and libcurl.
find_package(Qt6 QUIET COMPONENTS Widgets)
if(Qt6_FOUND AND EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/src/app/CMakeLists.txt")
    qt_standard_project_setup()
    add_subdirectory(src/app)
else()
    message(STATUS "we2002: Qt6 GUI not built (Qt6 found: ${Qt6_FOUND})")
endif()

include(CTest)
if(BUILD_TESTING)
    add_subdirectory(tests)
endif()
