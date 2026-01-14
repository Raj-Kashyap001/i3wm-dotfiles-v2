import QtQuick 6.2
import QtQuick.Controls 6.2
import QtQuick.Controls.Material 6.2
import QtQuick.Layouts 1.15

ApplicationWindow {
    id: window
    visible: true
    width: 850
    height: 650
    title: "i3wm Dotfiles Manager"
    flags: Qt.FramelessWindowHint | Qt.Window

    Material.theme: Material.Dark
    Material.accent: Material.Blue

    // Main Background
    Rectangle {
        anchors.fill: parent
        color: Material.backgroundColor
        border.color: "#333" // Subtle border for frameless window
        border.width: 1

        ColumnLayout {
            anchors.fill: parent
            spacing: 0

            // --- Custom Title Bar ---
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 48
                color: Qt.darker(Material.primaryColor, 1.2)

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 16
                    anchors.rightMargin: 8

                    Image {
                        source: "qrc:/icons/appicon.png"
                        Layout.preferredWidth: 22
                        Layout.preferredHeight: 22
                    }

                    Label {
                        text: "i3wm Dotfiles Manager"
                        font.pixelSize: 14
                        font.weight: Font.Medium
                        color: "white"
                        Layout.leftMargin: 8
                    }
                    
                    Label {
                        text: dotfilesManager.getVersion()
                        font.pixelSize: 12
                        color: "#888"
                        Layout.fillWidth: true
                    }

                    // Modern Icon Close Button
                    Button {
                        id: closeBtn
                        flat: true
                        Layout.preferredWidth: 48
                        Layout.preferredHeight: 48
                        
                        contentItem: Image {
                            source: "qrc:/icons/close-white.svg"
                            fillMode: Image.PreserveAspectFit
                            opacity: closeBtn.hovered ? 1.0 : 0.7
                        }
                        
                        background: Rectangle {
                            color: closeBtn.hovered ? '#d44f5a' : "transparent"
                            radius: 4
                        }
                        
                        onClicked: Qt.quit()
                    }
                }
            }

            // --- Main Content Area ---
            Pane {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.margins: 20
                Material.elevation: 2

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 20

                    // Header Section
                    ColumnLayout {
                        spacing: 4
                        Label {
                            text: "System Installation"
                            font.pixelSize: 22
                            font.weight: Font.Bold
                        }
                        Label {
                            text: "Select components to symlink to your home directory."
                            color: Material.secondaryTextColor
                        }
                    }

                    // Options Card
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 140
                        color: Qt.rgba(1, 1, 1, 0.03)
                        radius: 8
                        border.color: "#333"

                        GridLayout {
                            anchors.fill: parent
                            anchors.margins: 16
                            columns: 3
                            rowSpacing: 10
                            columnSpacing: 30

                            CheckBox { id: dunstCheck; text: "Dunst"; checked: dotfilesManager.isDunstInstalled() }
                            CheckBox { id: fishCheck; text: "Fish"; checked: dotfilesManager.isFishInstalled() }
                            CheckBox { id: i3Check; text: "i3 WM"; checked: dotfilesManager.isI3Installed() }
                            CheckBox { id: kittyCheck; text: "Kitty"; checked: dotfilesManager.isKittyInstalled() }
                            CheckBox { id: picomCheck; text: "Picom"; checked: dotfilesManager.isPicomInstalled() }
                            CheckBox { id: polybarCheck; text: "Polybar"; checked: dotfilesManager.isPolybarInstalled() }
                        }
                    }

                    // Actions & Config
                    RowLayout {
                        spacing: 15

                        CheckBox {
                            id: removeExistingCheck
                            text: "Overwrite existing files"
                            checked: dotfilesManager.removeExisting
                            onCheckedChanged: dotfilesManager.removeExisting = checked
                        }

                        Item { Layout.fillWidth: true } // Spacer

                        Button {
                            text: "Backup All"
                            onClicked: dotfilesManager.backupAll()
                        }
                        
                        Button {
                            text: "Install Selected"
                            highlighted: true
                            Material.accent: Material.Blue
                            onClicked: {
                                if (dunstCheck.checked) dotfilesManager.installDunst()
                                if (fishCheck.checked) dotfilesManager.installFish()
                                if (i3Check.checked) dotfilesManager.installI3()
                                if (kittyCheck.checked) dotfilesManager.installKitty()
                                if (picomCheck.checked) dotfilesManager.installPicom()
                                if (polybarCheck.checked) dotfilesManager.installPolybar()
                            }
                        }
                    }

                    // Log Console
                    Label {
                        text: "Activity Logs"
                        font.pixelSize: 12
                        font.capitalization: Font.AllUppercase
                        color: Material.accent
                    }

                    ScrollView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true

                        TextArea {
                            id: statusArea
                            readOnly: true
                            font.family: "Monospace"
                            font.pixelSize: 12
                            background: Rectangle {
                                color: "#121212"
                                radius: 4
                            }
                        }
                    }

                    Label {
                        text: "i3wm Dotfiles Manager • Raj Kashayp 2026"
                        Layout.alignment: Qt.AlignHCenter
                        font.pixelSize: 10
                        opacity: 0.5
                    }
                }
            }
        }
    }

    Connections {
        target: dotfilesManager
        function onStatusMessage(message) {
            statusArea.append(" > " + message)
        }
    }
}