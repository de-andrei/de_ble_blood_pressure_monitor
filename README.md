# DE BLE Blood Pressure Monitor

Интеграция для Home Assistant, добавляющая поддержку тонометра Medisana BU 575 через Bluetooth.

![Medisana BU 575](custom_components/de_ble_blood_pressure_monitor/brand/icon.png)

## Поддерживаемые устройства

- **Модель:** BU 575 (тонометр)
- **Производитель:** Medisana
- **Bluetooth-сервис:** `00001810-0000-1000-8000-00805f9b34fb`

## Возможности

- Автоматическое обнаружение тонометра через Bluetooth
- Отображение систолического давления (mmHg)
- Отображение диастолического давления (mmHg)
- Отображение среднего артериального давления (mmHg)
- Отображение частоты пульса (bpm)
- Отображение ID пользователя (для тонометров с поддержкой нескольких пользователей)
- Отображение времени последнего измерения
- Сенсор статуса подключения
- Автоматическое подключение при появлении устройства
- Сохранение последних показаний при отключении

## Установка

### Через HACS (рекомендуется)

1. Убедитесь, что у вас установлен [HACS](https://hacs.xyz/)
2. Откройте HACS в Home Assistant
3. Нажмите на три точки в правом верхнем углу
4. Выберите "Пользовательские репозитории"
5. Добавьте:
   - **URL:** `https://github.com/de-andrei/de_ble_blood_pressure_monitor`
   - **Категория:** `Integration`
6. Нажмите "Добавить"
7. Найдите "DE BLE Blood Pressure Monitor" в списке интеграций HACS
8. Нажмите "Скачать"
9. Перезапустите Home Assistant

### Ручная установка

1. Скачайте последний релиз из [репозитория](https://github.com/de-andrei/de_ble_blood_pressure_monitor/releases)
2. Распакуйте папку `custom_components/de_ble_blood_pressure_monitor` в директорию `config/custom_components/` вашего Home Assistant
3. Перезапустите Home Assistant

## Настройка

1. Перейдите в **Настройки** → **Устройства и службы**
2. Нажмите **"Добавить интеграцию"**
3. Найдите **"DE BLE Blood Pressure Monitor"** в списке
4. Выберите ваш тонометр Medisana BU 575 из списка обнаруженных устройств
5. Нажмите "Отправить"

## Сенсоры

После настройки будут созданы следующие сенсоры:

| Сущность | Имя | Описание |
|----------|-----|----------|
| `sensor.blood_pressure_systolic` | Systolic Pressure | Систолическое давление (mmHg) |
| `sensor.blood_pressure_diastolic` | Diastolic Pressure | Диастолическое давление (mmHg) |
| `sensor.blood_pressure_mean_arterial` | Mean Arterial Pressure | Среднее артериальное давление (mmHg) |
| `sensor.blood_pressure_heart_rate` | Heart Rate | Частота пульса (уд/мин) |
| `sensor.blood_pressure_user_id` | User ID | Идентификатор пользователя |
| `sensor.blood_pressure_last_measurement_time` | Last Measurement Time | Время последнего измерения |
| `sensor.blood_pressure_connection_status` | Connection Status | Статус подключения к устройству |