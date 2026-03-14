"""Constants for DE BLE Blood Pressure Monitor integration."""
from datetime import timedelta

DOMAIN = "de_ble_blood_pressure_monitor"

# Device info
DEVICE_MANUFACTURER = "Medisana"
DEVICE_MODEL = "BU 575"

# Service UUIDs (из вашего ESPHome конфига)
BP_SERVICE_UUID = "00001810-0000-1000-8000-00805f9b34fb"
BP_CHAR_UUID = "00002a35-0000-1000-8000-00805f9b34fb"

# Update intervals - УМЕНЬШАЕМ для более быстрого обнаружения!
SCAN_INTERVAL = timedelta(seconds=2)  # Было 3, стало 2
CONNECT_TIMEOUT = 5  # Было 10, стало 5
