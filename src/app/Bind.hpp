// Look a widget up by objectName, and refuse to carry on if it is not there.
//
// The forms are generated from legacy/mfc/ed.rc by tools/rc2ui.py, and the
// names went through glossary.UI_CONTROLS in phase 5.5. A name that no longer
// matches the form is a build-configuration mistake -- someone edited the
// glossary without re-running the generator -- but findChild reports it as a
// null pointer, so the first symptom would be a crash somewhere else entirely.
//
// `ctest -R glossary` catches the same mistake statically. This is the belt to
// that pair of braces, for the case where the .ui in the build tree is stale.

#pragma once

#include <QObject>
#include <QString>
#include <QWidget>

template <class T>
T* Bind(const QWidget* parent, const QString& name) {
    T* widget = parent->findChild<T*>(name);
    if (widget == nullptr) {
        qFatal("%s has no widget named %s -- re-run tools/rc2ui.py",
               parent->metaObject()->className(), qPrintable(name));
    }
    return widget;
}

/// The indexed families: "TXT_PLAYER%d" and the like.
template <class T>
T* Bind(const QWidget* parent, const char* format, int index) {
    return Bind<T>(parent, QString::asprintf(format, index));
}
