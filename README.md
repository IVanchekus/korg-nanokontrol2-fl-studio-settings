# KORG nanoKONTROL2 — MIDI Script для FL Studio

Форк [IVanchekus/korg-nanokontrol2-fl-studio-settings](https://github.com/IVanchekus/korg-nanokontrol2-fl-studio-settings) на базе **NanoMeter** (Robin Calvin / olyrhc).

Python-скрипт расширяет возможности KORG nanoKONTROL2 в FL Studio: микшер, транспорт, плейлист, channel rack, пик-метр на LED-кнопках S/M/R, Fader Pickup и др.

**Требования:** KORG nanoKONTROL2, FL Studio 20.7.3+ (рекомендуется 21+), KORG Kontrol Editor.

> **Перед использованием обязательно прочитайте [Wiki NanoMeter](https://github.com/olyrhc/nanometer/wiki)** — там подробно описаны режимы работы (Mixer / Channel Rack / Playlist), назначение кнопок, транспорт, пик-метр, Controller Link и FAQ. Этот README покрывает установку и настройки `config.py`; управление контроллером — по вики.

Имя скрипта в FL Studio (поле **Controller type**):

`MAIN KORG nanoKONTROL2 (korg-nanokontrol2-fl-studio-settings)`

---

## Русский

### Подготовка (Prerequisites)

Перед установкой скрипта подготовьте контроллер — как описано в [Wiki → Prerequisites](https://github.com/olyrhc/nanometer/wiki):

1. Установите **USB-MIDI драйвер** и **KORG Kontrol Editor**:
  - [Драйвер nanoKONTROL2](https://www.korg.com/us/support/download/product/1/285/)
  - [KORG Kontrol Editor](https://www.korg.com/us/support/download/product/1/133/)
2. Запишите **scene-data** на устройство. В оригинальном пакете NanoMeter есть файл `nanometer.nktrl2_data` — перетащите его в Kontrol Editor и выполните **Communication → Write Scene Data**. Подробно: [Scene data setup](https://github.com/olyrhc/nanometer/wiki/Scene-data-setup).
3. ⚠️ Без корректной scene-data скрипт работать не будет. Запись перезапишет текущие настройки контроллера — при необходимости сделайте резервную копию.

Если вы меняли MIDI-каналы в Kontrol Editor вручную, они должны совпадать с `config.py`:

- **Global MIDI Channel** → `MIDIChannel` (по умолчанию **1**)
- **Transport Button MIDI Channel** → `TransportChan` (по умолчанию **14**)

### Установка скрипта

Скопируйте (или перетащите) папку `**MAIN KORG nanoKONTROL2 (korg-nanokontrol2-fl-studio-settings)`** в каталог Hardware FL Studio:

```
%USERPROFILE%\Documents\Image-Line\FL Studio\Settings\Hardware\
```

macOS:

```
~/Documents/Image-Line/FL Studio/Settings/Hardware/
```

Внутри `Hardware` должна лежать папка с файлом `device_nanoKONTROL2.py`.

При необходимости отредактируйте `config.py` внутри этой папки (см. таблицы ниже). Значения `True` и `False` пишутся с заглавной буквы.

### Назначение скрипта в FL Studio

1. Запустите **FL Studio**
2. Откройте **Options → MIDI settings**
3. В разделе **Output** выберите **nanoKONTROL2** (устройство `CTRL`) и назначьте **уникальный Port** (например, `1`)
4. В разделе **Input** выберите **nanoKONTROL2** (устройство `SLIDER/KNOB`) с **тем же Port**
5. В поле **Controller type** выберите:
  `**MAIN KORG nanoKONTROL2 (korg-nanokontrol2-fl-studio-settings)`**
6. Убедитесь, что устройство **включено** (зелёный индикатор Enable)
7. Нажмите **Refresh device list**
8. Закройте окно

💡 Port должен совпадать у Input и Output и не использоваться другими устройствами.

### Проверка

1. **View → Script output** — в логе должно появиться `nanometer config: imported ok.`
2. Запустите воспроизведение — LED-кнопки S/M/R должны реагировать на сигнал
3. Подвигайте фейдер — громкость треков микшера должна меняться

### Обновление

Замените файлы скрипта новой версией, сохранив свой `config.py`. Перезапустите FL Studio или нажмите **Refresh device list** в MIDI settings.

### Отладка

Добавьте в `config.py`:

```python
Debug = True
```

Сырые MIDI-сообщения появятся в **View → Script output**.

---

### Настройки `config.py`

Файл: `MAIN KORG nanoKONTROL2 (korg-nanokontrol2-fl-studio-settings)/config.py`

Если параметр отсутствует или задан неверно, используется значение по умолчанию из `init_config.py`.

#### Общие


| Параметр         | По умолчанию | Диапазон | Описание                                                                                    |
| ---------------- | ------------ | -------- | ------------------------------------------------------------------------------------------- |
| `MIDIChannel`    | `1`          | 1–16     | MIDI-канал подсветки кнопок. Должен совпадать с **Global MIDI Channel** в Kontrol Editor.   |
| `TransportChan`  | `14`         | 1–16     | MIDI-канал транспортных кнопок. Должен совпадать с **Transport Button MIDI Channel**.       |
| `SleepTimer`     | `5`          | 0–300    | Минут бездействия до режима lightshow. `0` — lightshow отключён.                            |
| `PlayBlinkTempo` | `True`       | bool     | `True` — кнопка Play мигает в темп при воспроизведении. `False` — мигает Record при записи. |
| `BlinkFullTempo` | `False`      | bool     | `True` — мигание на каждый удар. `False` — на каждый второй удар (пол-темпа).               |
| `ModeBlink`      | `True`       | bool     | Быстрое мигание транспортных кнопок при смене режима (Cycle).                               |
| `Debug`          | `False`      | bool     | Вывод отладочных сообщений в Script output. Не обязателен в файле — включается вручную.     |


#### PeakMeter (пик-метр на LED S/M/R)


| Параметр       | По умолчанию | Описание                                                     |
| -------------- | ------------ | ------------------------------------------------------------ |
| `PeakMeter`    | `True`       | Включить визуальный пик-метр на кнопках Solo/Mute/Rec.       |
| `PlayingOnly`  | `False`      | `True` — метр только во время воспроизведения.               |
| `ReversePeak`  | `False`      | `True` — индикатор движется справа налево.                   |
| `BigMeter`     | `False`      | `True` — один большой метр на все LED вместо стерео/моно.    |
| `Clipping`     | `True`       | Показывать клиппинг выше 0 dB.                               |
| `SelectedPeak` | `False`      | `True` — пики выбранного трека. `False` — пики мастер-трека. |


#### Микшер


| Параметр           | По умолчанию | Описание                                                                                                                                      |
| ------------------ | ------------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `MixerMode`        | `True`       | Режим управления микшером.                                                                                                                    |
| `ArmedTracks`      | `False`      | `True` — кнопки R включают запись на трек. `False` — выбор трека.                                                                             |
| `MultiSelect`      | `False`      | `True` — множественный выбор треков кнопками R.                                                                                               |
| `TrackRangeOnly`   | `False`      | `True` — кнопки Track переключают только треки текущего диапазона.                                                                            |
| `StickyMaster`     | `False`      | `True` — мастер всегда в диапазоне фейдеров.                                                                                                  |
| `RangeDisplayRect` | `True`       | Красная рамка вокруг управляемых треков (FL Studio 17+). При `True` автоматически отключает `ColoredRange`.                                   |
| `RangeRectTimer`   | `0`          | 0–10 сек — через сколько скрыть рамку. `0` — рамка всегда видна.                                                                              |
| `ColoredRange`     | `True`       | Подсветка цветом треков текущего диапазона.                                                                                                   |
| `HighlightColor`   | `-11835046`  | Цвет подсветки (RGBA, целое число).                                                                                                           |
| `BracketedRange`   | `False`      | Добавлять скобки к именам треков в диапазоне.                                                                                                 |
| `PreserveMixDiff`  | `False`      | `True` — при групповом подъёме фейдеры останавливаются, когда один достигает +5.6 dB.                                                         |
| `FaderPickup`      | `True`       | После смены диапазона фейдер «подхватывает» громкость FL Studio. Несинхронизированные полоски мигают S/M/R. `False` — фейдеры работают сразу. |


#### Channel Rack


| Параметр          | По умолчанию | Описание                                                   |
| ----------------- | ------------ | ---------------------------------------------------------- |
| `ChannelrackMode` | `True`       | Режим управления Channel Rack.                             |
| `ChannelRectCtrl` | `False`      | `True` — рамка выделения канала включена сразу при старте. |


#### Playlist


| Параметр       | По умолчанию | Диапазон | Описание                                               |
| -------------- | ------------ | -------- | ------------------------------------------------------ |
| `PlaylistMode` | `True`       | —        | Режим управления плейлистом.                           |
| `TempoBase`    | `80`         | 10–397   | Минимальное значение темпа на ручке в режиме Playlist. |


#### Controller Link


| Параметр             | По умолчанию | Описание                                                            |
| -------------------- | ------------ | ------------------------------------------------------------------- |
| `ControllerLinkMode` | `False`      | Режим привязки параметров FL Studio к контроллеру.                  |
| `LinkOverriding`     | `False`      | Привязка без удержания Cycle — **перезаписывает обычные функции**.  |
| `TranspBtnLink`      | `False`      | Разрешить привязку транспортных кнопок (может отключить транспорт). |


#### Несколько nanoKONTROL2 (Unit 2–4)

Добавьте в `config.py` для каждого дополнительного устройства (все три параметра обязательны):


| Параметр                        | Диапазон | Описание                                     |
| ------------------------------- | -------- | -------------------------------------------- |
| `MIDIChannel_Unit2` … `Unit4`   | 1–16     | MIDI-канал подсветки для 2–4-го устройства.  |
| `TransportChan_Unit2` … `Unit4` | 1–16     | MIDI-канал транспорта для 2–4-го устройства. |
| `Port_Unit2` … `Unit4`          | 0–255    | MIDI-порт FL Studio для этого устройства.    |


---

## English

> **Before using the controller, read the [NanoMeter Wiki](https://github.com/olyrhc/nanometer/wiki)** — it documents all control modes, button assignments, transport, peak meter, Controller Link, and FAQ. This README covers installation and `config.py`; day-to-day usage is in the wiki.

Script name in FL Studio (**Controller type**):

`**MAIN KORG nanoKONTROL2 (korg-nanokontrol2-fl-studio-settings)`**

### Prerequisites

Before installing the script, prepare the controller as described in the [Wiki → Prerequisites](https://github.com/olyrhc/nanometer/wiki):

1. Install the **USB-MIDI driver** and **KORG Kontrol Editor**:
  - [nanoKONTROL2 driver](https://www.korg.com/us/support/download/product/1/285/)
  - [KORG Kontrol Editor](https://www.korg.com/us/support/download/product/1/133/)
2. Write **scene-data** to the device. The original NanoMeter package includes `nanometer.nktrl2_data` — drag it into Kontrol Editor and use **Communication → Write Scene Data**. Details: [Scene data setup](https://github.com/olyrhc/nanometer/wiki/Scene-data-setup).
3. ⚠️ Without correct scene-data the script will not work. Writing scene-data overwrites existing controller settings — back up first if needed.

If you changed MIDI channels manually in Kontrol Editor, they must match `config.py`:

- **Global MIDI Channel** → `MIDIChannel` (default **1**)
- **Transport Button MIDI Channel** → `TransportChan` (default **14**)

### Install the script

Copy (or drag & drop) the folder `**MAIN KORG nanoKONTROL2 (korg-nanokontrol2-fl-studio-settings)`** into FL Studio's Hardware directory:

```
%USERPROFILE%\Documents\Image-Line\FL Studio\Settings\Hardware\
```

macOS:

```
~/Documents/Image-Line/FL Studio/Settings/Hardware/
```

Edit `config.py` inside that folder if needed (see tables above). Use `True` and `False` with a capital letter.

### Assigning the script in FL Studio

1. Launch **FL Studio**
2. Go to **Options → MIDI settings**
3. In **Output**, select **nanoKONTROL2** (`CTRL` device) and assign a **unique Port** (e.g. `1`)
4. In **Input**, select **nanoKONTROL2** (`SLIDER/KNOB` device) using the **SAME Port**
5. Under **Controller type**, select:
  `**MAIN KORG nanoKONTROL2 (korg-nanokontrol2-fl-studio-settings)`**
6. Ensure the device is **enabled** (green indicator)
7. Press **Refresh device list**
8. Close the window

💡 The port number must match for Input and Output and must not be shared with other devices.

### Verify

1. **View → Script output** — you should see `nanometer config: imported ok.`
2. Play audio — S/M/R LEDs should respond (if `PeakMeter = True`)
3. Move a fader — mixer track volume should change

### Updating

Replace the script files with the new version, keeping your `config.py`. Restart FL Studio or press **Refresh device list** in MIDI settings.

### Debugging

Add to `config.py`:

```python
Debug = True
```

Raw MIDI messages will appear in **View → Script output**.

---

### `config.py` reference

File: `MAIN KORG nanoKONTROL2 (korg-nanokontrol2-fl-studio-settings)/config.py`

Missing or invalid options fall back to defaults in `init_config.py`.

#### General


| Option           | Default | Range | Description                                                                           |
| ---------------- | ------- | ----- | ------------------------------------------------------------------------------------- |
| `MIDIChannel`    | `1`     | 1–16  | MIDI channel for button LEDs. Must match **Global MIDI Channel** in Kontrol Editor.   |
| `TransportChan`  | `14`    | 1–16  | MIDI channel for transport buttons. Must match **Transport Button MIDI Channel**.     |
| `SleepTimer`     | `5`     | 0–300 | Minutes of inactivity before lightshow mode. `0` disables lightshow.                  |
| `PlayBlinkTempo` | `True`  | bool  | `True` — Play blinks in tempo while playing. `False` — Record blinks while recording. |
| `BlinkFullTempo` | `False` | bool  | `True` — blink every beat. `False` — every other beat (half tempo).                   |
| `ModeBlink`      | `True`  | bool  | Rapid transport blink when switching modes (Cycle).                                   |
| `Debug`          | `False` | bool  | Debug output in Script output. Optional — add manually to enable.                     |


#### PeakMeter (S/M/R LED peak meter)


| Option         | Default | Description                                                  |
| -------------- | ------- | ------------------------------------------------------------ |
| `PeakMeter`    | `True`  | Enable visual peak meter on Solo/Mute/Rec buttons.           |
| `PlayingOnly`  | `False` | `True` — meter only while playing.                           |
| `ReversePeak`  | `False` | `True` — peak moves right to left.                           |
| `BigMeter`     | `False` | `True` — single large meter using all LEDs.                  |
| `Clipping`     | `True`  | Show clipping above 0 dB.                                    |
| `SelectedPeak` | `False` | `True` — selected track peaks. `False` — master track peaks. |


#### Mixer


| Option             | Default     | Description                                                                                                                    |
| ------------------ | ----------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `MixerMode`        | `True`      | Mixer control mode.                                                                                                            |
| `ArmedTracks`      | `False`     | `True` — R buttons arm tracks for recording. `False` — select tracks.                                                          |
| `MultiSelect`      | `False`     | `True` — multi-select tracks with R buttons.                                                                                   |
| `TrackRangeOnly`   | `False`     | `True` — Track buttons only switch tracks in the current range.                                                                |
| `StickyMaster`     | `False`     | `True` — master track always included in the fader range.                                                                      |
| `RangeDisplayRect` | `True`      | Red rectangle around controlled tracks (FL Studio 17+). When `True`, disables `ColoredRange` automatically.                    |
| `RangeRectTimer`   | `0`         | 0–10 sec before hiding the rectangle. `0` — always visible.                                                                    |
| `ColoredRange`     | `True`      | Color-highlight tracks in the current range.                                                                                   |
| `HighlightColor`   | `-11835046` | Highlight color (RGBA integer).                                                                                                |
| `BracketedRange`   | `False`     | Add brackets to track names in the range.                                                                                      |
| `PreserveMixDiff`  | `False`     | `True` — when raising multiple faders, stop when one reaches +5.6 dB.                                                          |
| `FaderPickup`      | `True`      | After changing track range, fader must catch up to FL Studio volume. Unsynced strips blink S/M/R. `False` — immediate control. |


#### Channel Rack


| Option            | Default | Description                                              |
| ----------------- | ------- | -------------------------------------------------------- |
| `ChannelrackMode` | `True`  | Channel Rack control mode.                               |
| `ChannelRectCtrl` | `False` | `True` — channel selection rectangle enabled on startup. |


#### Playlist


| Option         | Default | Range  | Description                                       |
| -------------- | ------- | ------ | ------------------------------------------------- |
| `PlaylistMode` | `True`  | —      | Playlist control mode.                            |
| `TempoBase`    | `80`    | 10–397 | Minimum tempo value on the knob in Playlist mode. |


#### Controller Link


| Option               | Default | Description                                                  |
| -------------------- | ------- | ------------------------------------------------------------ |
| `ControllerLinkMode` | `False` | FL Studio parameter linking mode.                            |
| `LinkOverriding`     | `False` | Link without holding Cycle — **overrides normal functions**. |
| `TranspBtnLink`      | `False` | Allow linking transport buttons (may break transport).       |


#### Multiple nanoKONTROL2 units (Unit 2–4)

Add to `config.py` for each extra device (all three values required):


| Option                          | Range | Description                              |
| ------------------------------- | ----- | ---------------------------------------- |
| `MIDIChannel_Unit2` … `Unit4`   | 1–16  | LED MIDI channel for units 2–4.          |
| `TransportChan_Unit2` … `Unit4` | 1–16  | Transport MIDI channel for units 2–4.    |
| `Port_Unit2` … `Unit4`          | 0–255 | FL Studio MIDI port index for that unit. |


---

## Структура проекта / Project structure

```
korg-nanokontrol2-fl-studio-settings/
└── MAIN KORG nanoKONTROL2 (korg-nanokontrol2-fl-studio-settings)/
    ├── device_nanoKONTROL2.py   ← FL Studio entry point (callbacks)
    ├── config.py                ← user settings
    ├── init_config.py           ← config loader and defaults
    ├── kontrol.py               ← main controller logic
    ├── nanometer.py             ← peak meter
    ├── midi_map.py              ← CC numbers
    ├── volume.py, fader_pickup.py
    └── handlers/                ← event handlers
```

## Документация / Documentation

- **[NanoMeter Wiki](https://github.com/olyrhc/nanometer/wiki)** — режимы, кнопки, FAQ (обязательно к прочтению)
- [Scene data setup](https://github.com/olyrhc/nanometer/wiki/Scene-data-setup)
- [FL Studio MIDI Scripting API](https://il-group.github.io/FL-Studio-API-Stubs/midi_controller_scripting/)
- [Fork repository](https://github.com/IVanchekus/korg-nanokontrol2-fl-studio-settings)

## Лицензия / License

See [LICENSE](LICENSE). Based on NanoMeter by Robin Calvin.