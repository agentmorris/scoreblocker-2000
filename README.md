# ScoreBlocker 2000

## 🏈 Overview

ScoreBlocker 2000 is advanced technology for sports fans who want to watch games without having scores from other games ruined by on-screen graphics.  This sophisticated, futuristic tool is also known as a "big black rectangle".

## 🏟️ Features

* Always on top
* Frameless design (no distracting graphics, just a big black rectangle)
* Drag to move/resize

## 🏃‍♂️ Mobility & Control

- Click and drag to move ScoreBlocker 2000 anywhere on your screen
- Dual position system
  - Primary position: automatically saves your last position
  - Secondary position: set a custom position in the settings file for quick switching
- Right-click: jump to your secondary position
- Double-click to exit

## 🏁 Getting Started

### Installation

* Ensure you have Python installed on your Windows system
* Clone or download this repository

### Running the Application

**Option 1: Double-click the VBS script (recommended)**

```
run_score_blocker.vbs
```

**Option 2: Command line**

```bash
python score_blocker.py
```

**Option 3: Batch file**

```
run_score_blocker.bat
```

### Creating a Desktop Shortcut

For the cleanest experience, create a desktop shortcut to `run_score_blocker.vbs`.


### Settings File

The settings file (`score_blocker_settings.json`) is created alongside the Python script:

```json
{
  "primary": {
    "x": 100,
    "y": 100,
    "width": 200,
    "height": 100
  },
  "secondary": {
    "x": 300,
    "y": 200,
    "width": 200,
    "height": 100
  },
  "background_color": "#000000",
  "border_color": "#D3D3D3"
}
```

Edit the `secondary` section to set your preferred alternate position and size. Customize `background_color` and `border_color` using hex color codes (e.g., "#FF0000" for red).

## 🏅 Technical Requirements

- **Operating System**: Windows
- **Python**: Any version with tkinter (usually included)

## 🤝 Contributing

Found a bug? Want to add a feature? We welcome contributions! This is open-source software under the MIT license.

## 📜 License

MIT
