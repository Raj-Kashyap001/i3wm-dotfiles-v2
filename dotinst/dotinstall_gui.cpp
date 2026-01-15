#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQmlContext>
#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QStandardPaths>
#include <QDebug>
#include <QDateTime>
#include <QProcess>

// DotfilesManager class to handle dotfile installations
class DotfilesManager : public QObject {
    Q_OBJECT

public:
    explicit DotfilesManager(QObject *parent = nullptr) : QObject(parent) {
        // Get the absolute path to the dotfiles directory
        m_dotfilesPath = QDir::currentPath();
        qDebug() << "Dotfiles path:" << m_dotfilesPath;
    }

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

    Q_INVOKABLE bool isFastfetchInstalled() {
        return checkIfInstalled("~/.config/fastfetch");
    }

    Q_INVOKABLE bool isRofiInstalled() {
        return checkIfInstalled("~/.config/rofi");
    }

    Q_INVOKABLE void installDunst() {
        emit statusMessage("Installing Dunst...");
        if (createSymlink("dunst", "~/.config/dunst")) {
            emit statusMessage("✓ Dunst installed successfully.");
        } else {
            emit statusMessage("✗ Dunst installation failed.");
        }
    }

    Q_INVOKABLE void installFish() {
        emit statusMessage("Installing Fish...");
        if (createSymlink("fish", "~/.config/fish")) {
            emit statusMessage("✓ Fish installed successfully.");
        } else {
            emit statusMessage("✗ Fish installation failed.");
        }
    }

    Q_INVOKABLE void installI3() {
        emit statusMessage("Installing i3...");
        if (createSymlink("i3", "~/.config/i3")) {
            emit statusMessage("✓ i3 installed successfully.");
        } else {
            emit statusMessage("✗ i3 installation failed.");
        }
    }

    Q_INVOKABLE void installKitty() {
        emit statusMessage("Installing Kitty...");
        if (createSymlink("kitty", "~/.config/kitty")) {
            emit statusMessage("✓ Kitty installed successfully.");
        } else {
            emit statusMessage("✗ Kitty installation failed.");
        }
    }

    Q_INVOKABLE void installPicom() {
        emit statusMessage("Installing Picom...");
        if (createSymlink("picom", "~/.config/picom")) {
            emit statusMessage("✓ Picom installed successfully.");
        } else {
            emit statusMessage("✗ Picom installation failed.");
        }
    }

    Q_INVOKABLE void installPolybar() {
        emit statusMessage("Installing Polybar...");
        if (createSymlink("polybar", "~/.config/polybar")) {
            emit statusMessage("✓ Polybar installed successfully.");
        } else {
            emit statusMessage("✗ Polybar installation failed.");
        }
    }

    Q_INVOKABLE void installFastfetch() {
        emit statusMessage("Installing Fastfetch...");
        if (createSymlink("fastfetch", "~/.config/fastfetch")) {
            emit statusMessage("✓ Fastfetch installed successfully.");
        } else {
            emit statusMessage("✗ Fastfetch installation failed.");
        }
    }

    Q_INVOKABLE void installRofi() {
        emit statusMessage("Installing Rofi...");
        if (createSymlink("rofi", "~/.config/rofi")) {
            emit statusMessage("✓ Rofi installed successfully.");
        } else {
            emit statusMessage("✗ Rofi installation failed.");
        }
    }
  
    Q_INVOKABLE void backupAll() {
        emit statusMessage("Backing up all dotfiles...");
        int count = 0;
        count += backupDirectory("~/.config/dunst", "dunst") ? 1 : 0;
        count += backupDirectory("~/.config/fish", "fish") ? 1 : 0;
        count += backupDirectory("~/.config/i3", "i3") ? 1 : 0;
        count += backupDirectory("~/.config/kitty", "kitty") ? 1 : 0;
        count += backupDirectory("~/.config/picom", "picom") ? 1 : 0;
        count += backupDirectory("~/.config/polybar", "polybar") ? 1 : 0;
        count += backupDirectory("~/.config/fastfetch", "fastfetch") ? 1 : 0;
        count += backupDirectory("~/.config/rofi", "rofi") ? 1 : 0;
        emit statusMessage(QString("✓ Backup completed. %1 config(s) backed up.").arg(count));
    }

    Q_INVOKABLE void restoreAll() {
        emit statusMessage("Restoring all dotfiles...");
        int count = 0;
        count += restoreDirectory("~/.config/dunst", "dunst") ? 1 : 0;
        count += restoreDirectory("~/.config/fish", "fish") ? 1 : 0;
        count += restoreDirectory("~/.config/i3", "i3") ? 1 : 0;
        count += restoreDirectory("~/.config/kitty", "kitty") ? 1 : 0;
        count += restoreDirectory("~/.config/picom", "picom") ? 1 : 0;
        count += restoreDirectory("~/.config/polybar", "polybar") ? 1 : 0;
        count += restoreDirectory("~/.config/fastfetch", "fastfetch") ? 1 : 0;
        count += restoreDirectory("~/.config/rofi", "rofi") ? 1 : 0;
        emit statusMessage(QString("✓ Restore completed. %1 config(s) restored.").arg(count));
    }

    Q_INVOKABLE QString getVersion() {
        QProcess process;
        process.start("git", QStringList() << "describe" << "--tags" << "--abbrev=0");
        process.waitForFinished();
        QString version = process.readAllStandardOutput().trimmed();
        if (version.isEmpty()) {
            return "1.0.1";
        }
        // Remove 'v' prefix if present
        if (version.startsWith('v')) {
            version = version.mid(1);
        }
        return version;
    }

signals:
    void statusMessage(const QString &message);
    void removeExistingChanged();

private:
    bool m_removeExisting = false;
    QString m_dotfilesPath;

    QString expandPath(const QString &path) {
        QString expanded = path;
        expanded.replace("~", QStandardPaths::writableLocation(QStandardPaths::HomeLocation));
        return expanded;
    }

    bool checkIfInstalled(const QString &destDir) {
        QString expandedDest = expandPath(destDir);
        QFileInfo destInfo(expandedDest);
        
        // Check if it exists and is a symlink
        if (destInfo.exists() && destInfo.isSymLink()) {
            return true;
        }
        
        // Or if it's a directory with contents
        if (destInfo.isDir()) {
            QDir dest(expandedDest);
            QStringList entries = dest.entryList(QDir::Files | QDir::Dirs | QDir::NoDotAndDotDot);
            return !entries.isEmpty();
        }
        
        return false;
    }

    bool removeRecursively(const QString &dirPath) {
        QDir dir(dirPath);
        if (!dir.exists()) {
            return true;
        }

        bool success = true;
        QFileInfoList entries = dir.entryInfoList(QDir::NoDotAndDotDot | QDir::AllEntries | QDir::Hidden);
        
        for (const QFileInfo &info : entries) {
            if (info.isDir() && !info.isSymLink()) {
                success &= removeRecursively(info.absoluteFilePath());
            } else {
                success &= QFile::remove(info.absoluteFilePath());
            }
        }
        
        success &= dir.rmdir(dirPath);
        return success;
    }

    bool createSymlink(const QString &sourceDir, const QString &destDir) {
        // Get absolute source path
        QDir sourceQDir(m_dotfilesPath + "/" + sourceDir);
        if (!sourceQDir.exists()) {
            emit statusMessage(QString("✗ Source directory not found: %1").arg(sourceQDir.absolutePath()));
            return false;
        }

        QString srcAbsolutePath = sourceQDir.absolutePath();
        QString expandedDest = expandPath(destDir);

        // Check if destination exists
        QFileInfo destInfo(expandedDest);
        
        if (destInfo.exists() || destInfo.isSymLink()) {
            // If it's already a symlink pointing to the correct location, we're done
            if (destInfo.isSymLink() && destInfo.symLinkTarget() == srcAbsolutePath) {
                emit statusMessage(QString("  → %1 already linked correctly").arg(sourceDir));
                return true;
            }

            if (m_removeExisting) {
                emit statusMessage(QString("  ⚠ Removing existing: %1").arg(expandedDest));
                
                // Remove existing directory or symlink
                if (destInfo.isSymLink()) {
                    if (!QFile::remove(expandedDest)) {
                        emit statusMessage(QString("✗ Failed to remove existing symlink: %1").arg(expandedDest));
                        return false;
                    }
                } else if (destInfo.isDir()) {
                    if (!removeRecursively(expandedDest)) {
                        emit statusMessage(QString("✗ Failed to remove existing directory: %1").arg(expandedDest));
                        return false;
                    }
                } else {
                    if (!QFile::remove(expandedDest)) {
                        emit statusMessage(QString("✗ Failed to remove existing file: %1").arg(expandedDest));
                        return false;
                    }
                }
            } else {
                emit statusMessage(QString("  ⊗ Skipped (exists): %1").arg(sourceDir));
                emit statusMessage(QString("    Enable 'Overwrite existing configs' to replace"));
                return false;
            }
        }

        // Ensure parent directory exists
        QDir parentDir = QFileInfo(expandedDest).dir();
        if (!parentDir.exists()) {
            if (!parentDir.mkpath(".")) {
                emit statusMessage(QString("✗ Failed to create parent directory: %1").arg(parentDir.absolutePath()));
                return false;
            }
        }

        // Create the symlink
        if (QFile::link(srcAbsolutePath, expandedDest)) {
            emit statusMessage(QString("  ✓ Created symlink: %1 → %2").arg(expandedDest).arg(srcAbsolutePath));
            return true;
        } else {
            emit statusMessage(QString("✗ Failed to create symlink for: %1").arg(sourceDir));
            return false;
        }
    }

    bool backupDirectory(const QString &destDir, const QString &name) {
        QString expandedDest = expandPath(destDir);
        QFileInfo destInfo(expandedDest);
        
        // Don't backup if it doesn't exist or is already a symlink
        if (!destInfo.exists() || destInfo.isSymLink()) {
            return false;
        }

        QString timestamp = QDateTime::currentDateTime().toString("yyyy-MM-dd_hh-mm-ss");
        QString backupPath = expandPath("~/.dotfiles_backup/") + name + "_" + timestamp;
        
        QDir backupDir;
        if (!backupDir.mkpath(backupPath)) {
            emit statusMessage(QString("✗ Failed to create backup directory for %1").arg(name));
            return false;
        }

        // Copy the entire directory recursively
        if (!copyRecursively(expandedDest, backupPath)) {
            emit statusMessage(QString("✗ Failed to backup %1").arg(name));
            return false;
        }

        emit statusMessage(QString("  ✓ Backed up %1 to %2").arg(name).arg(backupPath));
        return true;
    }

    bool copyRecursively(const QString &srcPath, const QString &dstPath) {
        QFileInfo srcInfo(srcPath);
        
        if (srcInfo.isDir()) {
            QDir dstDir(dstPath);
            if (!dstDir.exists() && !dstDir.mkpath(".")) {
                return false;
            }

            QDir srcDir(srcPath);
            QFileInfoList entries = srcDir.entryInfoList(QDir::NoDotAndDotDot | QDir::AllEntries | QDir::Hidden);
            
            for (const QFileInfo &info : entries) {
                QString srcItemPath = info.absoluteFilePath();
                QString dstItemPath = dstPath + "/" + info.fileName();
                
                if (info.isSymLink()) {
                    // For symlinks, copy the target content
                    QString target = info.symLinkTarget();
                    if (!QFile::copy(target, dstItemPath)) {
                        return false;
                    }
                } else if (info.isDir()) {
                    if (!copyRecursively(srcItemPath, dstItemPath)) {
                        return false;
                    }
                } else {
                    if (!QFile::copy(srcItemPath, dstItemPath)) {
                        return false;
                    }
                }
            }
            return true;
        } else {
            return QFile::copy(srcPath, dstPath);
        }
    }

    bool restoreDirectory(const QString &destDir, const QString &name) {
        QString backupBase = expandPath("~/.dotfiles_backup");
        QDir backupDir(backupBase);
        
        if (!backupDir.exists()) {
            return false;
        }

        // Find the latest backup for this config
        QStringList subdirs = backupDir.entryList(QDir::Dirs | QDir::NoDotAndDotDot);
        QString latestBackup;
        for (const QString &subdir : subdirs) {
            if (subdir.startsWith(name + "_")) {
                if (latestBackup.isEmpty() || subdir > latestBackup) {
                    latestBackup = subdir;
                }
            }
        }

        if (latestBackup.isEmpty()) {
            emit statusMessage(QString("  ⊗ No backup found for %1").arg(name));
            return false;
        }

        QString fullBackupPath = backupBase + "/" + latestBackup;
        QString expandedDest = expandPath(destDir);
        
        // Remove existing destination
        QFileInfo destInfo(expandedDest);
        if (destInfo.exists()) {
            if (destInfo.isSymLink()) {
                QFile::remove(expandedDest);
            } else if (destInfo.isDir()) {
                removeRecursively(expandedDest);
            } else {
                QFile::remove(expandedDest);
            }
        }

        // Copy backup to destination
        if (!copyRecursively(fullBackupPath, expandedDest)) {
            emit statusMessage(QString("✗ Failed to restore %1").arg(name));
            return false;
        }

        emit statusMessage(QString("  ✓ Restored %1 from %2").arg(name).arg(latestBackup));
        return true;
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