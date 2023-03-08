import sys, smbios_interface, os, subprocess, shutil
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize smbios interface and get the current thermal and battery modes
        self.smbios = smbios_interface.smbiosInterface()
        self.thermal_mode = self.smbios.get_thermal()
        self.battery_mode = self.smbios.get_battery()
        
        self.setToolTip("Dell Power Tray")

        # Create the menu
        self.menu = QMenu()

        # Add the main entries
        thermal_entry = self.menu.addMenu(f"Current Thermal Mode: {self.capitalize(self.replace(self.thermal_mode, ['_', '-'], ' '))}")
        battery_entry = self.menu.addMenu(f"Current Battery Mode: {self.capitalize(self.replace(self.battery_mode, ['_', '-'], ' '))}")

        # Add the sub-entries for Thermal
        for i in self.smbios.thermal_modes:
            sub_entry = QAction(self.capitalize(self.replace(i, ['_', '-'], ' ')), self) # Set the text to the mode name
            sub_entry.triggered.connect(lambda _, i=i: self.set_thermal(i)) # Set the action to set the thermal mode
            thermal_entry.addAction(sub_entry) # Add the sub-entry to the menu

        # Add the sub-entries for Battery
        for i in self.smbios.battery_modes:
            sub_entry = QAction(self.capitalize(self.replace(i, ['_', '-'], ' ')), self) # Set the text to the mode name
            sub_entry.triggered.connect(lambda _, i=i: self.set_battery(i)) # Set the action to set the battery mode
            battery_entry.addAction(sub_entry) # Add the sub-entry to the menu

        # Add the exit button
        exit_button = QAction("Exit", self)
        exit_button.triggered.connect(QApplication.quit)
        self.menu.addAction(exit_button)

        # Set the menu
        self.setContextMenu(self.menu)

    def set_thermal(self, mode):
        print(f"Set Thermal {mode}")
        self.smbios.set_thermal(mode)
        self.thermal_mode = self.smbios.get_thermal()
        self.menu.actions()[0].setText(f"Current Thermal Mode: {self.capitalize(self.replace(self.thermal_mode, ['_', '-'], ' '))}")
        self.icon_refresh()

    def set_battery(self, mode):
        print(f"Set Battery {mode}")
        self.smbios.set_battery(mode)
        self.battery_mode = self.smbios.get_battery()
        self.menu.actions()[1].setText(f"Current Battery Mode: {self.capitalize(self.replace(self.battery_mode, ['_', '-'], ' '))}")

    def icon_refresh(self):
        # Update the icon
        print(f"Icon refresh: {self.thermal_mode}")
        if (self.thermal_mode == "balanced"):
            self.setIcon(QIcon.fromTheme("face-smile"))
        elif (self.thermal_mode == "cool-bottom"):
            self.setIcon(QIcon.fromTheme("face-cool"))
        elif (self.thermal_mode == "quiet"):
            self.setIcon(QIcon.fromTheme("face-ninja"))
        elif (self.thermal_mode == "performance"):
            self.setIcon(QIcon.fromTheme("face-devilish"))

    # Helper method to replace mulitple characters in a string
    def replace(self, string, chars, replacement):
        for i in chars:
            string = string.replace(i, replacement)
        return string

    # Helper method to capitalize all words in a string
    def capitalize(self, string):
        return ' '.join([i.capitalize() for i in string.split()])


# Method to install to ~/.local/share/applications
def install():
    # Get the current directory
    current_dir = os.path.dirname(os.path.realpath(__file__))
    # Get python path
    python_path = os.popen("which python3").read().strip()

    # Create the .desktop file
    desktop_file = f"""[Desktop Entry]
    Name=Dell Power Tray
    Comment=Power management for Dell laptops
    Exec={python_path} {current_dir}/main.py
    Icon={current_dir}/icon.png
    Terminal=false
    Type=Application
    Categories=Utility;"""

    # Write the .desktop file to the current users .local/share/applications directory
    home = os.path.expanduser("~")
    with open(f"{home}/.local/share/applications/dell-power-tray.desktop", "w") as f:
        f.write(desktop_file)

# Uninstall from ~/.local/share/applications
def uninstall():
    # remove file
    home = os.path.expanduser("~")
    os.remove(f"{home}/.local/share/applications/dell-power-tray.desktop")


# Main method
if __name__ == "__main__":
    # Check for install/uninstall flags
    for i in sys.argv:
        if (i == "--install"):
            install()
            print("Installed. The application should now appear in your application menu.")
            sys.exit(0)
        elif (i == "--uninstall"):
            uninstall()
            print("Uninstalled. The application should no longer appear in your application menu.")
            sys.exit(0)

    app = QApplication(sys.argv)

    # Set initial icon
    icon = QIcon.fromTheme("face-smile")

    # Create the system tray icon
    tray_icon = SystemTrayIcon()
    tray_icon.setIcon(icon)
    tray_icon.setVisible(True)
    tray_icon.icon_refresh()

    # Run the application
    sys.exit(app.exec_())
