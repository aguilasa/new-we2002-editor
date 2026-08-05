find_package(CURL REQUIRED)

add_library(we2002_core STATIC
    CdImage.cpp
    Database.cpp
    Player.cpp
    Sofifa.cpp
    Tables.cpp
    Team.cpp
    TextCodec.cpp
)
add_library(we2002::core ALIAS we2002_core)

target_include_directories(we2002_core PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
)

target_link_libraries(we2002_core PRIVATE CURL::libcurl)

# Hard rule from docs/PLAN-LINUX.md section 5: the core links no GUI toolkit
# and no platform API. Only the standard library and libcurl. If a Qt include
# ever appears here, the phase 3 golden tests stop being runnable headless.

if(NOT MSVC)
    target_compile_options(we2002_core PRIVATE -Wall -Wextra)
else()
    # The inherited code has 198 strcpy/strcat calls, every one of which MSVC
    # reports as C4996 "deprecated". They are not being replaced: CLAUDE.md and
    # docs/PLAN-WINDOWS.md section 10 both say so, because the truncation those
    # calls perform can be load-bearing in the image format and swapping them
    # for strcpy_s without a golden test is exactly how the raw_formation
    # overflow was introduced. Silencing the diagnostic is the correct answer;
    # what actually guards that class of defect here is the static_assert in
    # tests/test_main.cpp, since MSVC has no _FORTIFY_SOURCE.
    #
    # NOMINMAX is the other one. The core includes no platform header itself --
    # that rule still holds -- but curl/curl.h pulls in winsock2.h and so
    # windows.h, which defines min and max as macros. They then eat the
    # std::max/std::min calls in Sofifa.cpp, with an error that names neither
    # windows.h nor the macro. Defining it here keeps the fix out of the
    # sources, where a #ifdef _WIN32 has no business being.
    target_compile_definitions(we2002_core PRIVATE
        _CRT_SECURE_NO_WARNINGS
        NOMINMAX)
endif()
