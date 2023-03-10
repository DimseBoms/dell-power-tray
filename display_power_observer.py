import os


# This class is used to determine if the laptop is docked or not
class DisplayPowerObserver:
    def __init__(self):
        self.drm_path = "/sys/class/drm" # The path to the sysfs drm directory
        self.power_path = "/sys/class/power_supply" # The path to the sysfs power supply directory

    # Returns the names of all connected displays as a list
    def get_display_names(self):
        display_names = []
        try:
            # Iterate through all the directories in the sysfs drm directory listing all the displays
            for directory in os.listdir(self.drm_path):
                directory_path = os.path.join(self.drm_path, directory) # Get the path to the display folder
                # Iterate through all the files for each display folder
                if os.path.isdir(directory_path):
                    for file in os.listdir(directory_path):
                        # If the file is the status file, open it and read the content
                        if file == "status":
                            with open(f"{directory_path}/{file}", "r") as f:
                                content = f.read().strip()
                            if content == "connected":
                                display_name = directory
                                display_names.append(display_name)
        except (FileNotFoundError, Exception) as e:
            print(f"An error while traversing the sysfs drm directory to get the display names: {e}")
        return display_names

    # Returns a list of all the power sources that are online
    def get_power_sources(self):
        power_sources = []
        # Iterate through all the directories in the sysfs power supply directory listing all the power sources
        for directory in os.listdir(self.power_path):
            if not ("bat" in directory.lower()): # check if directory name does not contain bat
                directory_path = os.path.join(self.power_path, directory) # Get the path to the power source folder
                if os.path.isdir(directory_path): # Check if the path is a directory
                    for file in os.listdir(directory_path):
                        # Reads the online file to determine if the power source is online or not
                        if file == "online":
                            with open(f"{directory_path}/{file}", "r") as f:
                                content = f.read().strip()
                                if content == "1":
                                    power_sources.append(directory)
        return power_sources

    # Returns True if the laptop is docked, False otherwise
    def is_docked(self):
        self.displays = self.get_display_names()
        self.powers = self.get_power_sources()
        docked = False
        if len(self.displays) > 1 and len(self.powers) > 0:
            docked = True
        return docked
