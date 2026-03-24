"""Constants for DE BLE Blood Pressure Monitor integration."""
from datetime import timedelta

DOMAIN = "de_ble_blood_pressure_monitor"

# Device info
DEVICE_MANUFACTURER = "Medisana"
DEVICE_MODEL = "BU 575"

# Service UUIDs
BP_SERVICE_UUID = "00001810-0000-1000-8000-00805f9b34fb"
BP_CHAR_UUID = "00002a35-0000-1000-8000-00805f9b34fb"

# Update intervals
SCAN_INTERVAL = timedelta(seconds=20)
CONNECT_TIMEOUT = 10
