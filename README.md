# dell-power-tray
Power management for Dell laptops. Only tested with KDE
# Requirements
* libsmbios binary (https://github.com/dell/libsmbios). This one is probably available in your package manager.
* PyQt5 (Installed with pip. Check requirements.txt)
# Installation
* Clone project:
```git clone https://github.com/DimseBoms/dell-power-tray```
* navigate to project:
```cd dell-power-tray```
* Install python requirements:
```pip install -r requirements.txt```
* Run the application:
```python3 main.py```
* If you want it to show up in the app launcher:
```python3 main.py --install```
