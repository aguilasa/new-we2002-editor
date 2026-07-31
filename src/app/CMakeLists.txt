# The Qt front end. Everything that knows about widgets lives here; everything
# that knows about the CD image lives in we2002::core. The dependency runs one
# way only -- see docs/PLAN-LINUX.md section 5.

qt_add_executable(newWe2002
    main.cpp
    MainWindow.cpp
    TeamView.cpp
    TacticsView.cpp
    Commands.cpp
    DataFiles.cpp
    SofifaView.cpp
    PlayerSelectDialog.cpp
    PlayerSkillsDialog.cpp
    FlagKitDialog.cpp
    DefaultTacticsDialog.cpp
    EditOptionsDialog.cpp
    resources/app.qrc
)

# The forms are generated from legacy/mfc/ed.rc by tools/rc2ui.py and committed
# under ui/. AUTOUIC turns each into a ui_<Form>.h in the build tree.
set_property(TARGET newWe2002 PROPERTY AUTOUIC_SEARCH_PATHS
    "${CMAKE_CURRENT_SOURCE_DIR}/ui")

# Needed for resources/app.qrc, and easy to miss: qt_standard_project_setup()
# turns on AUTOMOC and AUTOUIC but NOT AUTORCC. Without this the .qrc is treated
# as an ordinary source file that nothing knows how to compile, rcc never runs,
# and the build succeeds with the icon simply absent -- which is what happened
# from phase 6 until the icon was redrawn and someone finally looked for it.
set_property(TARGET newWe2002 PROPERTY AUTORCC ON)
target_sources(newWe2002 PRIVATE
    ui/MainDialog.ui
    ui/PlayerSelectDialog.ui
    ui/PlayerSkillsDialog.ui
    ui/FlagKitPreviewDialog.ui
    ui/DefaultTacticsDialog.ui
    ui/EditOptionsDialog.ui
)

target_link_libraries(newWe2002 PRIVATE we2002::core Qt6::Widgets)

if(NOT MSVC)
    target_compile_options(newWe2002 PRIVATE -Wall -Wextra)
endif()

# ---------------------------------------------------------------------------
# Where the runtime data files are looked up. See DataFiles.cpp for the order.
# ---------------------------------------------------------------------------

# Running straight out of the build tree.
target_compile_definitions(newWe2002 PRIVATE
    WE2002_SOURCE_DATA_DIR="${CMAKE_SOURCE_DIR}/data")

# Installed. Baked in as a path *relative to the executable* rather than as an
# absolute prefix, so the installed tree can be moved or staged -- and so that
# a self-contained bundle would work without a rebuild.
file(RELATIVE_PATH WE2002_DATA_FROM_BIN
    "${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_BINDIR}"
    "${CMAKE_INSTALL_PREFIX}/${WE2002_APPDATADIR}")
target_compile_definitions(newWe2002 PRIVATE
    WE2002_DATA_DIR_FROM_BIN="${WE2002_DATA_FROM_BIN}")

install(TARGETS newWe2002 RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}")
