import sys, os

class smbiosInterface:
    def __init__(self):
        # List of all thermal modes and battery modes
        self.thermal_modes = ["balanced", "cool-bottom", "quiet", "performance"]
        self.battery_modes = ["primarily_ac", "adaptive", "standard", "express"]
        self.cmd = "sudo smbios"
        if (self.get_availability()):
            print("SMBIOS is available")
        else:
            print("SMBIOS is not available")
            sys.exit(1)

    # Checks if the smbios binary is available
    def get_availability(self):
        result = os.popen(f"{self.cmd}-sys-info").read().lower().split()
        # Checks if the result contains the words libsmbios or version
        for i in range(len(result)):
            if (result[i] == "libsmbios" or result[i] == "version:"):
                return True
        return False

    # Returns the thermal profile
    def get_thermal(self):
        result = os.popen(f"{self.cmd}-thermal-ctl --get-thermal-info").read().lower().split()
        # Checks if any of the containing words is in the thermal_modes list
        for i in range(len(result)):
            if (result[i] in self.thermal_modes):
                print(f"Current Thermal Mode: {result[i]}")
                return result[i]
            # Extra check for "cool_bottom" because the smbios binary returns "cool bottom" with a space
            if (result[i] == "cool"):
                print(f"Current Battery Mode: cool-bottom")
                return "cool-bottom"
        print(f"Current Thermal Mode: Unknown")
        return "unknown"

    # Returns the battery profile
    def get_battery(self):
        result = os.popen(f"{self.cmd}-battery-ctl --get-charging-cfg").read().lower().split()
        # Checks if any of the containing words is in the battery_modes list
        for i in range(len(result)):
            if (result[i] in self.battery_modes):
                print(f"Current Battery Mode: {result[i]}")
                return result[i]
        print(f"Current Battery Mode: Unknown")
        return "unknown"

    # Sets the thermal profile
    def set_thermal(self, profile):
        if (profile in self.thermal_modes):
            print(f"Setting Thermal Mode to {profile}")
            os.system(f"{self.cmd}-thermal-ctl --set-thermal-mode={profile}")
        else:
            print("Invalid Thermal Mode")

    # Sets the battery profile
    def set_battery(self, profile):
        if (profile in self.battery_modes):
            print(f"Setting Battery Mode to {profile}")
            os.system(f"{self.cmd}-battery-ctl --set-charging-mode={profile}")
        else:
            print("Invalid Battery Mode")
