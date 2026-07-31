// Entry point. The original was ed.cpp: a CWinApp whose InitInstance built
// CEdDlg and ran it modally.
//
// Two things from ed.cpp are deliberately not here.
// COleObjectFactory::UpdateRegistryAll() registered the automation object in
// the Windows registry -- there is nothing to register on Linux, and it is the
// reason the golden tests need their own Wine prefix. The /Embedding and
// /Automation command-line handling went with it: the editor was never driven
// that way, and the proxy class it needed died with MFC.

#include <QApplication>
#include <QIcon>

#include "MainWindow.hpp"

int main(int argc, char** argv) {
    QApplication app(argc, argv);
    // This is what ends up in WM_CLASS, which is how a desktop shell matches a
    // window back to its .desktop entry. Keep it equal to the executable name
    // and to StartupWMClass in packaging/io.github.aguilasa.newWe2002.desktop.
    QApplication::setApplicationName(QStringLiteral("newWe2002"));
    QApplication::setApplicationDisplayName(QStringLiteral("WE2002 Editor"));

    // The original's SetIcon(m_hIcon) pair. Both sizes come out of
    // legacy/mfc/res/ed.ico and are compiled in, so this works wherever the
    // executable is run from.
    QIcon icon;
    icon.addFile(QStringLiteral(":/icons/newWe2002-16.png"));
    icon.addFile(QStringLiteral(":/icons/newWe2002-32.png"));
    QApplication::setWindowIcon(icon);

    // An image named on the command line skips the file dialog. The original
    // had no arguments at all; this exists so the window can be driven from a
    // script, which is how the golden tests reach it.
    const QStringList args = QApplication::arguments();
    const QString image = (args.size() > 1) ? args.at(1) : QString();

    MainWindow window;
    // The original asked for the image inside OnInitDialog and bailed out of
    // the dialog if the user cancelled. Same order here: no image, no window.
    if (!window.OpenImage(image)) {
        return 1;
    }
    window.show();
    return QApplication::exec();
}
