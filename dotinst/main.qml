import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

ApplicationWindow {
    id: window
    visible: true
    width: 850
    height: 700
    title: "i3wm Dotfiles Manager"
    flags: Qt.FramelessWindowHint | Qt.Window

    property bool isDarkTheme: true
    Material.theme: isDarkTheme ? Material.Dark : Material.Light
    Material.accent: Material.Blue

    Rectangle {
        anchors.fill: parent
        color: Material.backgroundColor
        border.color: isDarkTheme ? "#333" : "#ddd"
        border.width: 1

        ColumnLayout {
            anchors.fill: parent
            spacing: 0

            // --- FIXED CUSTOM TITLE BAR ---
            Rectangle {
                id: titleBar
                Layout.fillWidth: true
                Layout.preferredHeight: 48
                color: isDarkTheme ? "#1a1a1a" : Material.primaryColor

                DragHandler {
                    onActiveChanged: if (active) window.startSystemMove()
                }

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 16
                    anchors.rightMargin: 4
                    spacing: 0

                    Image {
                        source: "qrc:/icons/appicon.png"
                        Layout.preferredWidth: 20
                        Layout.preferredHeight: 20
                    }

                    Label {
                        text: "i3wm Dotfiles Manager"
                        font.pixelSize: 13
                        font.weight: Font.Medium
                        color: "white"
                        Layout.leftMargin: 10
                    }
                    
                    Label {
                        text: "v" + dotfilesManager.getVersion()
                        font.pixelSize: 11
                        color: "#888"
                        Layout.leftMargin: 8
                        Layout.fillWidth: true
                    }

                    // Theme Toggle
                    Button {
                        id: themeToggleBtn
                        Layout.preferredWidth: 46
                        Layout.preferredHeight: 46
                        flat: true
                        onClicked: isDarkTheme = !isDarkTheme
                        
                        contentItem: Item {
                            Image {
                                anchors.centerIn: parent
                                source: isDarkTheme ? "qrc:/icons/moon.svg" : "qrc:/icons/sun.svg"
                                sourceSize.width: 18
                                sourceSize.height: 18
                                opacity: themeToggleBtn.hovered ? 1.0 : 0.8
                            }
                        }
                    }

                    // Close Button
                    Button {
                        id: closeBtn
                        Layout.preferredWidth: 46
                        Layout.preferredHeight: 46
                        flat: true
                        onClicked: Qt.quit()
                        
                        background: Rectangle {
                            color: closeBtn.hovered ? "#e81123" : "transparent"
                        }
                        
                        contentItem: Item {
                            Image {
                                anchors.centerIn: parent
                                source: "qrc:/icons/close-white.svg"
                                sourceSize.width: 16
                                sourceSize.height: 16
                            }
                        }
                    }
                }
            }

            // --- Main Content Area ---
            Pane {
                Layout.fillWidth: true
                Layout.fillHeight: true
                padding: 25

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
                            text: "Select components to symlink. Existing files will be handled based on the toggle below."
                            color: Material.secondaryTextColor
                            font.pixelSize: 13
                        }
                    }

                    // Options Card (The Group)
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 150
                        color: isDarkTheme ? Qt.rgba(1, 1, 1, 0.03) : Qt.rgba(0, 0, 0, 0.03)
                        radius: 10
                        border.color: isDarkTheme ? "#333" : "#ddd"

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 15
                            
                            Label {
                                text: "CONFIGURATIONS"
                                font.pixelSize: 11
                                font.weight: Font.Bold
                                color: Material.accent
                                Layout.bottomMargin: 5
                            }

                            GridLayout {
                                Layout.fillWidth: true
                                columns: 4
                                rowSpacing: 10
                                columnSpacing: 10

                                CheckBox { id: dunstCheck; text: "Dunst"; checked: dotfilesManager.isDunstInstalled() }
                                CheckBox { id: fishCheck; text: "Fish"; checked: dotfilesManager.isFishInstalled() }
                                CheckBox { id: i3Check; text: "i3 WM"; checked: dotfilesManager.isI3Installed() }
                                CheckBox { id: kittyCheck; text: "Kitty"; checked: dotfilesManager.isKittyInstalled() }
                                CheckBox { id: picomCheck; text: "Picom"; checked: dotfilesManager.isPicomInstalled() }
                                CheckBox { id: polybarCheck; text: "Polybar"; checked: dotfilesManager.isPolybarInstalled() }
                                CheckBox { id: fastfetchCheck; text: "Fastfetch"; checked: dotfilesManager.isFastfetchInstalled() }
                            }
                            Item { Layout.fillHeight: true }
                        }
                    }

                    // Configuration Controls
                    RowLayout {
                        spacing: 15
                        CheckBox {
                            id: removeExistingCheck
                            text: "Overwrite existing configs"
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
                                if (fastfetchCheck.checked) dotfilesManager.installFastfetch()
                            }
                        }
                    }

                    // Activity Log Section
                    ColumnLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        spacing: 8

                        Label {
                            text: "ACTIVITY LOGS"
                            font.pixelSize: 11
                            font.weight: Font.Bold
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
                                    color: isDarkTheme ? "#111" : "#f5f5f5"
                                    radius: 6
                                    border.color: isDarkTheme ? "#222" : "#eee"
                                }
                            }
                        }

                        Label {
                            text: "Note: For icons to work install nerd font or you can just use mine in fonts/ dir"
                            font.pixelSize: 11
                            font.italic: true
                            color: Material.secondaryTextColor
                            Layout.topMargin: 4
                        }
                    }

                    // Footer
                    RowLayout {
                        Layout.fillWidth: true
                        Label { text: "i3wm Dotfiles Manager • Raj Kashayp 2026"; font.pixelSize: 10; opacity: 0.5 }
                        Item { Layout.fillWidth: true }
                        Button { 
                            text: "About"
                            flat: true
                            font.pixelSize: 10
                            onClicked: aboutDialog.open()
                        }
                    }
                }
            }
        }
    }

    // About Dialog (Simplified)
    Dialog {
        id: aboutDialog
        title: "About"
        standardButtons: Dialog.Ok
        modal: true
        anchors.centerIn: parent
        contentItem: ColumnLayout {
            spacing: 10
            Label { text: "i3wm Dotfiles Manager"; font.pixelSize: 16; font.weight: Font.Bold; Layout.alignment: Qt.AlignHCenter }
            Label { text: "Developed by Raj Kashayp"; font.pixelSize: 12; Layout.alignment: Qt.AlignHCenter }
            Button {
                text: "GitHub Repository"
                flat: true
                Layout.alignment: Qt.AlignHCenter
                onClicked: Qt.openUrlExternally("https://github.com/Raj-Kashyap001/i3wm-dotfiles-v2")
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