import sys, os, smbios_interface, json
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer
from display_power_observer import DisplayPowerObserver

class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.kde = self.is_kde()

        # Initialize smbios interface and get the current thermal and battery modes
        self.smbios = smbios_interface.smbiosInterface()
        self.thermal_mode = self.smbios.get_thermal()
        self.battery_mode = self.smbios.get_battery()

        # Initialize settings
        dir = os.path.dirname(os.path.realpath(__file__))
        self.init_settings()

        # Initialize the display and power observer
        self.display_power_observer = DisplayPowerObserver()
        
        self.setToolTip("Dell Power Tray")

        # Create the menu
        self.menu = QMenu()

        # Add the main entries
        self.thermal_entry = self.menu.addMenu(f"Current Thermal Mode:\t{self.format(self.thermal_mode)}")
        self.battery_entry = self.menu.addMenu(f"Current Battery Mode:\t{self.format(self.battery_mode)}")
        if self.kde:
            self.thermal_entry.setIcon(QIcon.fromTheme("temperature-normal"))
            self.battery_entry.setIcon(QIcon.fromTheme("battery-normal"))

        # Add the sub-entries for Thermal
        for i in self.smbios.thermal_modes:
            sub_entry = QAction(self.format(i), self) # Set the text to the mode name
            sub_entry.triggered.connect(lambda _, i=i: self.set_thermal(i, write=True)) # Set the action to set the thermal mode
            sub_entry.setCheckable(True)
            if i == self.thermal_mode: # If the current thermal mode is selected it should be checked
                sub_entry.setChecked(True)
            self.thermal_entry.addAction(sub_entry) # Add the sub-entry to the menu

        # Add the sub-entries for Battery
        for i in self.smbios.battery_modes:
            sub_entry = QAction(self.format(i), self) # Set the text to the mode name
            sub_entry.triggered.connect(lambda _, i=i: self.set_battery(i)) # Set the action to set the battery mode
            sub_entry.setCheckable(True)
            if i == self.battery_mode: # If the current battery mode is selected it should be checked
                sub_entry.setChecked(True)
            self.battery_entry.addAction(sub_entry) # Add the sub-entry to the menu

        self.menu.addSeparator()

        # Add options entry to the menu
        self.options_entry = self.menu.addMenu("Options")
        if self.kde:
            self.options_entry.setIcon(QIcon.fromTheme("preferences-system"))

        # Add button to enable/disable auto-perf-on-dock to the options entry
        auto_perf_on_dock_entry = QAction(f"Automatic performance mode when docked", self)
        auto_perf_on_dock_entry.setCheckable(True)
        auto_perf_on_dock_entry.setChecked(self.settings["auto-perf-on-dock"])
        auto_perf_on_dock_entry.triggered.connect(self.toggle_auto_perf_on_dock)
        self.options_entry.addAction(auto_perf_on_dock_entry)

        # Add option to enable/disable custom-scripts-on-dock to the options entry
        custom_scripts_on_dock_entry = QAction(f"Run custom scripts when docked", self)
        custom_scripts_on_dock_entry.setCheckable(True)
        custom_scripts_on_dock_entry.setChecked(self.settings["custom-scripts-on-dock"])
        custom_scripts_on_dock_entry.triggered.connect(self.toggle_custom_scripts_on_dock)
        self.options_entry.addAction(custom_scripts_on_dock_entry)

        self.menu.addSeparator()

        # Add the exit button
        exit_button = QAction("Exit", self)
        if self.kde:
            exit_button.setIcon(QIcon.fromTheme("application-exit"))
        exit_button.triggered.connect(QApplication.quit)
        self.menu.addAction(exit_button)

        # Set the menu
        self.setContextMenu(self.menu)

        # Check if the last manually set thermal mode file exists if it doesn't create it
        # and if it does read it and set the last thermal mode to the value in the file
        try:
            if not os.path.exists(f"{dir}/last_thermal_mode"):
                with open(f"{dir}/last_thermal_mode", "w") as f:
                    f.write(self.thermal_mode)
                self.last_thermal_mode = self.thermal_mode
            else:
                with open(f"{dir}/last_thermal_mode", "r") as f:
                    self.last_thermal_mode = f.read()
        except Exception as e:
            print(f"Error while initializing last thermal mode file: {e}")

        # Initial dock check and state for dock
        self.last_dock_state = self.display_power_observer.is_docked()

        # Create a QTimer to check for docking status every x seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_docking_status)

        # If settings auto-perf-on-dock or custom-scripts-on-dock
        # is enabled trigger the timer handler
        if self.settings["auto-perf-on-dock"] or self.settings["custom-scripts-on-dock"]:
            self.handle_timer_state_change()

        # Initial run of custom scripts if the setting is enabled
        if self.settings["custom-scripts-on-dock"]:
            self.run_custom_scripts(self.last_dock_state)
        
    # Toggle auto-perf-on-dock'
    def toggle_auto_perf_on_dock(self):
        if self.settings["auto-perf-on-dock"]:
            self.set_thermal(self.last_thermal_mode)
            self.settings["auto-perf-on-dock"] = False
            self.write_settings()
            print("Auto Perf on Dock disabled")
        else:
            if self.display_power_observer.is_docked():
                self.set_thermal("performance")
            self.settings["auto-perf-on-dock"] = True
            self.write_settings()
            print("Auto Perf on Dock enabled")
        self.handle_timer_state_change()

    # Toggle custom-scripts-on-dock
    def toggle_custom_scripts_on_dock(self):
        if self.settings["custom-scripts-on-dock"]:
            self.settings["custom-scripts-on-dock"] = False
            self.write_settings()
            print("Custom scripts on dock disabled")
        else:
            self.settings["custom-scripts-on-dock"] = True
            self.write_settings()
            print("Custom scripts on dock enabled")
        self.handle_timer_state_change()

    # Enable/Disable timer based on the current state of the settings.
    # This should be triggered whenever the settings are changed and when the app starts
    def handle_timer_state_change(self):
        if self.settings["auto-perf-on-dock"] or self.settings["custom-scripts-on-dock"]:
            print("Starting timer")
            self.timer.start(5000)
        else:
            print("Stopping timer")
            self.timer.stop()

    # Handle signal for dock status change
    def check_docking_status(self):
        if self.display_power_observer.is_docked():
            self.handle_dock(True)
        else:
            self.handle_dock(False)

    # Handle actions when dock status changes
    def handle_dock(self, docked):
        if docked:
            # If the system is docked and auto-perf-on-dock is enabled it should set the thermal mode to performance
            if self.settings["auto-perf-on-dock"] and self.thermal_mode != "performance":
                self.set_thermal("performance")
            # If the system is docked and custom-scripts-on-dock is enabled it should run the custom scripts
            if self.settings["custom-scripts-on-dock"] and self.last_dock_state != docked:
                self.run_custom_scripts(docked)
                self.last_dock_state = docked
        elif not docked:
            # If the system is undocked and the last manually set thermal mode is not the current
            # thermal mode it should set the thermal mode to the last manually set thermal mode
            if self.thermal_mode != self.last_thermal_mode:
                self.set_thermal(self.last_thermal_mode)
            # If the system is undocked and custom-scripts-on-dock is enabled
            # it should run the custom scripts
            if self.settings["custom-scripts-on-dock"] and self.last_dock_state != docked:
                self.run_custom_scripts(docked)
                self.last_dock_state = docked

    # Run custom scripts
    def run_custom_scripts(self, docked):
        if docked:
            # Run ./custom_scripts/on_dock.sh
            try:
                os.system(f"{dir}/custom_scripts/on_dock.sh")
            except Exception as e:
                print(f"Error while running on_dock.sh: {e}")
        elif not docked:
            # Run ./custom_scripts/off_dock.sh
            try:
                os.system(f"{dir}/custom_scripts/off_dock.sh")
            except Exception as e:
                print(f"Error while running off_dock.sh: {e}")

    # Write the last manually set thermal mode to state and file
    def write_last_thermal_mode(self, mode):
        try:
            with open(f"{dir}/last_thermal_mode", "w") as f:
                f.write(mode)
            self.last_thermal_mode = mode
        except Exception as e:
            print(f"Error while writing last thermal mode file: {e}")

    # Set the thermal operating mode
    def set_thermal(self, mode, write=False):
        print(f"Set Thermal {mode}")
        self.smbios.set_thermal(mode)
        self.thermal_mode = self.smbios.get_thermal()
        self.menu.actions()[0].setText(f"Current Thermal Mode:\t{self.format(self.thermal_mode)}")
        for action in self.thermal_entry.actions(): # Make sure the correct thermal mode is checked
            if action.text() == self.format(mode):
                action.setChecked(True)
            else:
                action.setChecked(False)
        self.icon_refresh()
        if write:
            self.write_last_thermal_mode(mode)

    # Set the battery operating mode
    def set_battery(self, mode):
        print(f"Set Battery {mode}")
        self.smbios.set_battery(mode)
        self.battery_mode = self.smbios.get_battery()
        self.menu.actions()[1].setText(f"Current Battery Mode:\t{self.format(self.battery_mode)}")
        for action in self.battery_entry.actions(): # Make sure the correct battery mode is checked
            if action.text() == self.format(mode):
                action.setChecked(True)
            else:
                action.setChecked(False)

    # Refresh icons after thermal mode change
    def icon_refresh(self):
        if (self.thermal_mode == "balanced"):
            self.setIcon(QIcon(f"{dir}/icons/breeze/face-smile-grin.svg"))
        elif (self.thermal_mode == "cool-bottom"):
            self.setIcon(QIcon(f"{dir}/icons/breeze/face-cool.svg"))
        elif (self.thermal_mode == "quiet"):
            self.setIcon(QIcon(f"{dir}/icons/breeze/face-ninja.svg"))
        elif (self.thermal_mode == "performance"):
            self.setIcon(QIcon(f"{dir}/icons/breeze/face-devilish.svg"))

    # Helper method to replace mulitple characters in a string
    def replace(self, string, chars, replacement):
        for i in chars:
            string = string.replace(i, replacement)
        return string

    # Helper method to capitalize all words in a string
    def capitalize(self, string):
        return ' '.join([i.capitalize() for i in string.split()])

    # Helper method to format strings for the menu
    def format(self, string):
        # Replace all underscores and dashes with spaces
        string = self.capitalize(self.replace(string, ['_', '-'], ' '))
        # Make all words containing 2 or less characters uppercase
        return ' '.join([i.upper() if len(i) <= 2 else i for i in string.split()])

    # Function to detect if the system is running KDE or not
    def is_kde(self):
        return os.environ.get("XDG_CURRENT_DESKTOP") == "KDE"

    # Function to initialize the settings
    def init_settings(self):
        default_settings = {
            "auto-perf-on-dock": True,
            "custom-scripts-on-dock": False
        }
        try: # Try to load the settings file and make sure all settings are present
            settings = json.load(open(f"{dir}/settings.json", "r"))
            for i in default_settings:
                if i not in settings:
                    settings[i] = default_settings[i]
            # Load the settings into the proper settings variable and write them to the file
            self.settings = settings
            self.write_settings()
        except:
            try: # If the settings file doesn't exist or is corrupt create a new one
                with open(f"{dir}/settings.json", "w") as f:
                    # Create dict containing the default settings
                    json.dump(default_settings, f)
                # Load them into the settings variable
                self.settings = default_settings
            except Exception as e:
                print(f"Error while initializing settings: {e}")

    # Function to read settings
    def read_settings(self):
        try:
            with open(f"{dir}/settings.json", "r") as f:
                settings = json.load(f)
        except Exception as e:
            print(f"Error while reading settings: {e}")
            settings = {}
        return settings

    # Function to write settings
    def write_settings(self):
        try:
            with open(f"{dir}/settings.json", "w") as f:
                json.dump(self.settings, f)
        except Exception as e:
            print(f"Error while writing settings: {e}")

# Main method
if __name__ == "__main__":
    # Check for flags
    for i in sys.argv:
        if (i == "--help" or i == '-h' or i == "-?"):
            print("Dell Power Tray")
            print("Usage: dell-power-tray [OPTION]")
            print("Options:")
            print("  --install\tInstall the application")
            print("  --uninstall\tUninstall the application")
            print("  --help\tDisplay this help message")
            sys.exit(0)
        if (i == "--install" or i == '-i' or i == "--uninstall" or i == '-u'):
            import installer
            if (i == "--install" or i == '-i'):
                installer.install()
            elif (i == "--uninstall" or i == '-u'):
                installer.uninstall()
            sys.exit(0)

    # Create the application
    app = QApplication(sys.argv)

    # Get application directory
    dir = os.path.dirname(os.path.realpath(__file__))

    # Set initial icon
    icon = QIcon.fromTheme(f"{dir}/icons/breeze/face-smile-grin.svg")

    # Create the system tray icon
    tray_icon = SystemTrayIcon()
    tray_icon.setIcon(icon)
    tray_icon.setVisible(True)
    tray_icon.icon_refresh()

    # Run the application
    sys.exit(app.exec_())
