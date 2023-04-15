#!/bin/bash

# Custom bash script that is executed when the dock is disconnected
# and the setting "Execute script on dock" is enabled in the settings

# Set mouse sensitivity to a custom value using gsettings
gsettings set org.gnome.desktop.peripherals.mouse speed -0.45
