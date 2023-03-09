import pyudev

class ExternalMonitorPowerMonitor:
    def __init__(self):
        self.context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(self.context)
        self.observer_callbacks = []
    
    def add_observer_callback(self, callback):
        self.observer_callbacks.append(callback)
        
    def start(self):
        for device in self.context.list_devices(subsystem='drm'):
            if device.get('UDID'):
                self._notify_observer_callbacks(device)
        self.observer_callbacks.append(self._notify_observer_callbacks)
        self.monitor.filter_by(subsystem='usb')
        self.monitor.filter_by(subsystem='drm')
        self.monitor.filter_by(subsystem='hidraw')
        self.monitor.filter_by(subsystem='input')
        self.monitor.filter_by(subsystem='video4linux')
        self.monitor.filter_by('ID_CLASS', 'display')
        self.monitor.filter_by('ID_CLASS', 'misc')
        self.monitor.start()
        for device in iter(self.monitor.poll, None):
            self._notify_observer_callbacks(device)

    def _notify_observer_callbacks(self, device):
        if 'HDMI' in device.get('ID_MODEL_FROM_DATABASE') or \
            'DisplayPort' in device.get('ID_MODEL_FROM_DATABASE') or \
            'USB-C' in device.get('ID_MODEL_FROM_DATABASE') or \
            'DP' in device.get('ID_MODEL_FROM_DATABASE') or \
            'misc' in device.get('ID_CLASS'):
            external_monitor_connected = device.action == 'add'
            for callback in self.observer_callbacks:
                callback('external_monitor_connected', external_monitor_connected)
        elif 'POWER_SUPPLY' in device.get('SUBSYSTEM'):
            laptop_power_connected = device.get('POWER_SUPPLY_STATUS') == 'Charging' or device.get('POWER_SUPPLY_STATUS') == 'Full'
            for callback in self.observer_callbacks:
                callback('laptop_power_connected', laptop_power_connected)
