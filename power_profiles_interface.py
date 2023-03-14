import os

class PowerProfilesInterface:
    def __init__(self):
        # List of all available power profiles on the current system
        self.power_profiles_list = []
        self.cmd = "powerprofilesctl"
        self.available = self.get_availability()
        if (self.available):
            print("Power profiles daemon is available")
            print("Will set Linux power profiles along with Dell thermal profiles")
        else:
            print("Power profiles daemon is unavailable")
            print("Will not be able to set power profiles")

    # Checks if the power profiles daemon is installed
    def get_availability(self):
        result = os.popen(f"{self.cmd} version").read()
        # Checks if the command is found and if the version is not empty
        if (result != ""):
            # Gets the list of all available power profiles and stores it in the power_profiles_list variable
            result = os.popen(f"{self.cmd} list").read()
            # Splits the result into lines
            for line in result.split('\n'):
                if line.startswith(' '):
                    # This is a mode name
                    profile = line.strip()
                    self.power_profiles_list.append(profile)
            print(self.power_profiles_list)
            return True
        return False

    # Returns the currenctly selected power profile
    def get_power_profile(self):
        if not self.available: return "unknown"
        return os.popen(f"{self.cmd} get").read().strip()

    # Sets the power profile
    def set_thermal(self, profile):
        if not self.available: return
        if (profile in self.power_profiles_list):
            print(f"Setting power profile to {profile}")
            os.system(f"{self.cmd} set {profile}")
        else:
            print("Invalid power profile")
