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

    // The original's SetIcon(m_hIcon) pair, which had only 16 and 32 to offer.
    // Every size is compiled in (see resources/app.qrc), so this works wherever
    // the executable is run from and a HiDPI panel has something to pick.
    QIcon icon;
    for (const int size : {16, 24, 32, 48, 64, 128, 256}) {
        icon.addFile(QStringLiteral(":/icons/newWe2002-%1.png").arg(size));
    }
    QApplication::setWindowIcon(icon);

    // An image named on the command line skips the file dialog. The original
    // had no arguments at all; this exists so the window can be driven from a
    // script, which is how the golden tests reach it.
    const QStringList args = QApplication::arguments();
    const QString image = (args.size() > 1) ? args.at(1) : QString();

    MainWindow window;
    // The original asked for the image inside OnInitDialog too, but it did not
    // bail out: `return FALSE` there (legacy/mfc/edDlg.cpp:1331) only tells MFC
    // that the focus was already handled -- it does not end the dialog, and no
    // EndDialog is called. Cancelling leaves ed.exe standing with the whole
    // main dialog empty and `Write into CD image` still clickable.
    //
    // Exiting instead is a deliberate divergence: a save button with no image
    // loaded is worse than no window. See PARIDADE-FUNCIONAL.md section 6 and
    // docs/tasks/CORR-WTE-140.md.
    if (!window.OpenImage(image)) {
        return 1;
    }
    window.show();
    return QApplication::exec();
}
