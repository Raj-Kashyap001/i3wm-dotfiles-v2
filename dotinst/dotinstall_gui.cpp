#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQmlContext>
#include <QDir>
#include <QFile>
#include <QStandardPaths>
#include <QDebug>
#include <QDateTime>
#include <QProcess>

// DotfilesManager class to handle dotfile installations
class DotfilesManager : public QObject {
    Q_OBJECT

public:
    explicit DotfilesManager(QObject *parent = nullptr) : QObject(parent) {}

    Q_PROPERTY(bool removeExisting READ removeExisting WRITE setRemoveExisting NOTIFY removeExistingChanged)

    bool removeExisting() const { return m_removeExisting; }
    void setRemoveExisting(bool remove) { m_removeExisting = remove; emit removeExistingChanged(); }

    Q_INVOKABLE bool isDunstInstalled() {
        return checkIfInstalled("~/.config/dunst");
    }

    Q_INVOKABLE bool isFishInstalled() {
        return checkIfInstalled("~/.config/fish");
    }

    Q_INVOKABLE bool isI3Installed() {
        return checkIfInstalled("~/.config/i3");
    }

    Q_INVOKABLE bool isKittyInstalled() {
        return checkIfInstalled("~/.config/kitty");
    }

    Q_INVOKABLE bool isPicomInstalled() {
        return checkIfInstalled("~/.config/picom");
    }

    Q_INVOKABLE bool isPolybarInstalled() {
        return checkIfInstalled("~/.config/polybar");
    }

    Q_INVOKABLE void installDunst() {
        emit statusMessage("Installing Dunst...");
        createSymlinks("dunst", "~/.config/dunst");
        emit statusMessage("Dunst installed.");
    }

    Q_INVOKABLE void installFish() {
        emit statusMessage("Installing Fish...");
        createSymlinks("fish", "~/.config/fish");
        emit statusMessage("Fish installed.");
    }

    Q_INVOKABLE void installI3() {
        emit statusMessage("Installing i3...");
        createSymlinks("i3", "~/.config/i3");
        emit statusMessage("i3 installed.");
    }

    Q_INVOKABLE void installKitty() {
        emit statusMessage("Installing Kitty...");
        createSymlinks("kitty", "~/.config/kitty");
        emit statusMessage("Kitty installed.");
    }

    Q_INVOKABLE void installPicom() {
        emit statusMessage("Installing Picom...");
        createSymlinks("picom", "~/.config/picom");
        emit statusMessage("Picom installed.");
    }

    Q_INVOKABLE void installPolybar() {
        emit statusMessage("Installing Polybar...");
        createSymlinks("polybar", "~/.config/polybar");
        emit statusMessage("Polybar installed.");
    }

    Q_INVOKABLE void backupAll() {
        emit statusMessage("Backing up all dotfiles...");
        backupDirectory("~/.config/dunst", "dunst");
        backupDirectory("~/.config/fish", "fish");
        backupDirectory("~/.config/i3", "i3");
        backupDirectory("~/.config/kitty", "kitty");
        backupDirectory("~/.config/picom", "picom");
        backupDirectory("~/.config/polybar", "polybar");
        emit statusMessage("Backup completed.");
    }

    Q_INVOKABLE void restoreAll() {
        emit statusMessage("Restoring all dotfiles...");
        restoreDirectory("~/.config/dunst", "dunst");
        restoreDirectory("~/.config/fish", "fish");
        restoreDirectory("~/.config/i3", "i3");
        restoreDirectory("~/.config/kitty", "kitty");
        restoreDirectory("~/.config/picom", "picom");
        restoreDirectory("~/.config/polybar", "polybar");
        emit statusMessage("Restore completed.");
    }

    Q_INVOKABLE QString getVersion() {
        QProcess process;
        process.start("git", QStringList() << "describe" << "--tags" << "--abbrev=0");
        process.waitForFinished();
        QString version = process.readAllStandardOutput().trimmed();
        if (version.isEmpty()) {
            return "v1.0.0"; // Default
        }
        return version;
    }

signals:
    void statusMessage(const QString &message);
    void removeExistingChanged();

private:
    bool m_removeExisting = false;

    bool checkIfInstalled(const QString &destDir) {
        QString expandedDest = destDir;
        expandedDest.replace("~", QStandardPaths::writableLocation(QStandardPaths::HomeLocation));
        QDir dest(expandedDest);
        if (!dest.exists()) return false;
        QStringList files = dest.entryList(QDir::Files | QDir::NoDotAndDotDot);
        for (const QString &file : files) {
            QFile f(dest.absoluteFilePath(file));
            if (f.size() > 0) return true; // Ignore empty files
        }
        return false;
    }

    void createSymlinks(const QString &sourceDir, const QString &destDir) {
        QDir source(sourceDir);
        QString expandedDest = destDir;
        expandedDest.replace("~", QStandardPaths::writableLocation(QStandardPaths::HomeLocation));

        QDir dest(expandedDest);
        if (!dest.exists()) {
            dest.mkpath(".");
        }

        QStringList files = source.entryList(QDir::Files);
        for (const QString &file : files) {
            QString srcFile = source.absoluteFilePath(file);
            QString dstFile = dest.absoluteFilePath(file);
            if (QFile::exists(dstFile) || QFile::symLinkTarget(dstFile) == srcFile) {
                if (m_removeExisting) {
                    QFile::remove(dstFile);
                } else {
                    continue; // Skip if exists
                }
            }
            if (!QFile::link(srcFile, dstFile)) {
                qDebug() << "Failed to create symlink" << srcFile << "to" << dstFile;
            } else {
                qDebug() << "Created symlink" << srcFile << "to" << dstFile;
            }
        }
    }

    void copyDirectory(const QString &sourceDir, const QString &destDir) {
        QDir source(sourceDir);
        QString expandedDest = destDir;
        expandedDest.replace("~", QStandardPaths::writableLocation(QStandardPaths::HomeLocation));

        QDir dest(expandedDest);
        if (!dest.exists()) {
            dest.mkpath(".");
        }

        QStringList files = source.entryList(QDir::Files);
        for (const QString &file : files) {
            QString srcFile = source.absoluteFilePath(file);
            QString dstFile = dest.absoluteFilePath(file);
            if (QFile::exists(dstFile)) {
                QFile::remove(dstFile); // Overwrite if exists
            }
            if (!QFile::copy(srcFile, dstFile)) {
                qDebug() << "Failed to copy" << srcFile << "to" << dstFile;
            } else {
                qDebug() << "Copied" << srcFile << "to" << dstFile;
            }
        }
    }

    void backupDirectory(const QString &destDir, const QString &name) {
        QString expandedDest = destDir;
        expandedDest.replace("~", QStandardPaths::writableLocation(QStandardPaths::HomeLocation));
        QDir dest(expandedDest);
        if (!dest.exists()) return;

        QString backupDir = QStandardPaths::writableLocation(QStandardPaths::HomeLocation) + "/.dotfiles_backup/" + name + "_" + QDateTime::currentDateTime().toString("yyyy-MM-dd_hh-mm-ss");
        QDir backup(backupDir);
        backup.mkpath(".");

        QStringList files = dest.entryList(QDir::Files);
        for (const QString &file : files) {
            QString srcFile = dest.absoluteFilePath(file);
            QString dstFile = backup.absoluteFilePath(file);
            QFile::copy(srcFile, dstFile);
        }
        qDebug() << "Backed up" << name << "to" << backupDir;
    }

    void restoreDirectory(const QString &destDir, const QString &name) {
        QString backupBase = QStandardPaths::writableLocation(QStandardPaths::HomeLocation) + "/.dotfiles_backup";
        QDir backupDir(backupBase);
        if (!backupDir.exists()) return;

        QStringList subdirs = backupDir.entryList(QDir::Dirs | QDir::NoDotAndDotDot);
        QString latestBackup;
        for (const QString &subdir : subdirs) {
            if (subdir.startsWith(name + "_")) {
                if (latestBackup.isEmpty() || subdir > latestBackup) {
                    latestBackup = subdir;
                }
            }
        }
        if (latestBackup.isEmpty()) return;

        QString fullBackupPath = backupBase + "/" + latestBackup;
        QDir backup(fullBackupPath);
        QString expandedDest = destDir;
        expandedDest.replace("~", QStandardPaths::writableLocation(QStandardPaths::HomeLocation));
        QDir dest(expandedDest);
        if (!dest.exists()) dest.mkpath(".");

        QStringList files = backup.entryList(QDir::Files);
        for (const QString &file : files) {
            QString srcFile = backup.absoluteFilePath(file);
            QString dstFile = dest.absoluteFilePath(file);
            QFile::copy(srcFile, dstFile);
        }
        qDebug() << "Restored" << name << "from" << fullBackupPath;
    }
};

int main(int argc, char *argv[]) {
    QGuiApplication app(argc, argv);

    DotfilesManager manager;

    QQmlApplicationEngine engine;
    engine.rootContext()->setContextProperty("dotfilesManager", &manager);
    engine.load(QUrl(QStringLiteral("qrc:/main.qml")));

    if (engine.rootObjects().isEmpty()) {
        return -1;
    }

    return app.exec();
}

#include "dotinstall_gui.moc"