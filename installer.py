import os

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
    Icon={current_dir}/icons/icon.png
    Terminal=false
    Type=Application
    Categories=Utility;"""

    # Write the .desktop file to ~/.local/share/applications
    try:
        home = os.path.expanduser("~")
        with open(f"{home}/.local/share/applications/dell-power-tray.desktop", "w") as f:
            f.write(desktop_file)
        print("Installed. The application should now appear in your application menu.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Failed to install: {e}")


# Remove .desktop file from ~/.local/share/applications
def uninstall():
    try:
        home = os.path.expanduser("~")
        os.remove(f"{home}/.local/share/applications/dell-power-tray.desktop")
        print("Uninstalled. The application should no longer appear in your application menu.")
    except FileNotFoundError:
        print("No changes made. The application was not installed.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Failed to uninstall: {e}")
