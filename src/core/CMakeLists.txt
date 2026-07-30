find_package(CURL REQUIRED)

add_library(we2002_core STATIC
    CdImage.cpp
    Database.cpp
    Player.cpp
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
endif()
