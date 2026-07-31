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

#include "MainWindow.hpp"

int main(int argc, char** argv) {
    QApplication app(argc, argv);
    QApplication::setApplicationName(QStringLiteral("we2002"));
    QApplication::setApplicationDisplayName(QStringLiteral("WE2002 Editor"));

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
