import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

ApplicationWindow {
    id: window
    visible: true
    width: 850
    height: 650
    title: "i3wm Dotfiles Manager"
    flags: Qt.FramelessWindowHint | Qt.Window

    property bool isDarkTheme: true
    Material.theme: isDarkTheme ? Material.Dark : Material.Light
    Material.accent: Material.Blue

    // Main Background
    Rectangle {
        anchors.fill: parent
        color: Material.backgroundColor
        border.color: "#333" 
        border.width: 1

        ColumnLayout {
            anchors.fill: parent
            spacing: 0

            // --- Custom Title Bar ---
            Rectangle {
                id: titleBar
                Layout.fillWidth: true
                Layout.preferredHeight: 48
                color: Qt.darker(Material.primaryColor, 1.2)

                DragHandler {
                    onActiveChanged: if (active) window.startSystemMove()
                }

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

                    Button {
                        id: themeToggleBtn
                        flat: true
                        Layout.preferredWidth: 48
                        Layout.preferredHeight: 48
                        contentItem: Image {
                            source: isDarkTheme ? "qrc:/icons/moon.svg" : "qrc:/icons/sun.svg"
                            fillMode: Image.PreserveAspectFit
                            opacity: themeToggleBtn.hovered ? 1.0 : 0.7
                        }
                        background: Rectangle {
                            color: themeToggleBtn.hovered ? '#444' : "transparent"
                            radius: 4
                        }
                        onClicked: isDarkTheme = !isDarkTheme
                    }

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

                    ColumnLayout {
                        spacing: 4
                        Label { text: "System Installation"; font.pixelSize: 22; font.weight: Font.Bold }
                        Label { text: "Select components to symlink to your home directory."; color: Material.secondaryTextColor }
                    }

                    // Options Card
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 140
                        color: Qt.rgba(1, 1, 1, 0.03)
                        radius: 8
                        border.color: "#333"

                        GridLayout {
                            anchors.fill: parent; anchors.margins: 16
                            columns: 3; rowSpacing: 10; columnSpacing: 30
                            CheckBox { id: dunstCheck; text: "Dunst"; checked: dotfilesManager.isDunstInstalled() }
                            CheckBox { id: fishCheck; text: "Fish"; checked: dotfilesManager.isFishInstalled() }
                            CheckBox { id: i3Check; text: "i3 WM"; checked: dotfilesManager.isI3Installed() }
                            CheckBox { id: kittyCheck; text: "Kitty"; checked: dotfilesManager.isKittyInstalled() }
                            CheckBox { id: picomCheck; text: "Picom"; checked: dotfilesManager.isPicomInstalled() }
                            CheckBox { id: polybarCheck; text: "Polybar"; checked: dotfilesManager.isPolybarInstalled() }
                        }
                    }

                    RowLayout {
                        spacing: 15
                        CheckBox {
                            id: removeExistingCheck
                            text: "Overwrite existing files"
                            checked: dotfilesManager.removeExisting
                            onCheckedChanged: dotfilesManager.removeExisting = checked
                        }
                        Item { Layout.fillWidth: true }
                        Button { text: "Backup All"; onClicked: dotfilesManager.backupAll() }
                        Button {
                            text: "Install Selected"
                            highlighted: true
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
                                color: isDarkTheme ? "#121212" : "#f5f5f5"
                                radius: 4
                            }
                        }
                    }

                    // --- NEW NOTE TEXT ---
                    Label {
                        text: "Note: For icons to work install nerd font or you can just use mine in fonts/ dir"
                        font.pixelSize: 14
                        color: Material.secondaryTextColor
                        Layout.topMargin: -10
                    }

                    RowLayout {
                        Layout.alignment: Qt.AlignHCenter
                        spacing: 20
                        Label { text: "i3wm Dotfiles Manager • Raj Kashayp 2026"; font.pixelSize: 10; opacity: 0.5 }
                        Button { text: "About"; flat: true; font.pixelSize: 10; opacity: 0.7; onClicked: aboutDialog.open() }
                    }
                }
            }
        }
    }

    Dialog {
        id: aboutDialog
        title: "About"
        standardButtons: Dialog.Ok
        modal: true
        anchors.centerIn: parent
        contentItem: ColumnLayout {
            spacing: 10
            Label { text: "i3wm Dotfiles Manager"; font.pixelSize: 16; font.weight: Font.Bold; Layout.alignment: Qt.AlignHCenter }
            Label { text: "Version: " + dotfilesManager.getVersion(); font.pixelSize: 12; Layout.alignment: Qt.AlignHCenter }
            Label { text: "Developed by: Raj Kashayp"; font.pixelSize: 12; Layout.alignment: Qt.AlignHCenter }
            Label {
                text: "source: https://github.com/Raj-Kashyap001/i3wm-dotfiles-v2"
                font.pixelSize: 12; color: Material.accent; Layout.alignment: Qt.AlignHCenter
                MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: Qt.openUrlExternally("https://github.com/Raj-Kashyap001") }
            }
        }
    }

    Connections {
        target: dotfilesManager
        function onStatusMessage(message) { statusArea.append(" > " + message) }
    }
}