# dell-power-tray
Power management for Dell laptops. Only tested with KDE
# Requirements
* libsmbios binary utilities (https://github.com/dell/libsmbios). This one is probably available in your package manager.
```
# On Fedora
sudo dnf install smbios-utils-bin
```
```
# On Ubuntu
sudo apt update && sudo apt install smbios-utils
```
* PyQt5 (Can be installed with pip. See instructions below)
# Installation
* Navigate to where you want your project to reside:
```
# Where ever you want really, this is just an example
cd ~/.local/share/
```
* Clone project:
```
git clone https://github.com/DimseBoms/dell-power-tray
```
* navigate to newly downloaded project:
```
cd dell-power-tray
```
* Install python requirements:
```
pip install -r requirements.txt
```
* Run the application:
```
python3 main.py
```
* If you want it to show up in the app launcher:
```
python3 main.py --install
```
* To be able to run the necessary commands without typing sudo you need to add this to the bottom of /etc/sudoers using visudo:
```
sudo visudo
```
```
# Dell Power Tray
YOUR_USERNAME_HERE ALL = NOPASSWD: /usr/sbin/smbios-sys-info
YOUR_USERNAME_HERE ALL = NOPASSWD: /usr/sbin/smbios-thermal-ctl
YOUR_USERNAME_HERE ALL = NOPASSWD: /usr/sbin/smbios-battery-ctl
```
* Keep in mind that the location of smbios binaries may be different on your distro. To find the location of the binaries you can use *which* or *whereis*
```
which smbios-sys-info
```
or
```
whereis smbios-sys-info
```