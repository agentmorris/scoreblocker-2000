# ScoreBlocker 2000

## 🏈 Overview

ScoreBlocker 2000 is advanced technology for sports fans who want to watch games without having scores from other games ruined by on-screen graphics.  This sophisticated, futuristic tool is also known as a "big black rectangle".

## 🏟️ Features

* Always on top
* Frameless design (no distracting graphics, just a big black rectangle)
* Drag to move/resize
* Multi-monitor support with preset configurations
* Launch multiple instances simultaneously
* **Auto-position over an NFL game's other-games score ticker with a double-click**
  (Windows only — see "Auto-positioning for NFL games" below)

## 🏃‍♂️ Mobility & Control

- **Left-click and drag**: Move ScoreBlocker 2000 anywhere on your screen
- **Drag from edges or corners**: Resize the window
- **Double-click**: Auto-position over the other-games score ticker for the NFL
  game playing in any open Chrome / Firefox / Edge window (Windows only — see
  "Auto-positioning for NFL games" below).
- **`c` key** (with the window focused): snap to the most-recent known CBS
  ticker position on whichever monitor the window is currently on. Handy when
  the new season's data hasn't been added yet but you know the game's on CBS.
- **`f` key**: same, for FOX.
- **Middle-click**: Show current coordinates and copy to clipboard (helpful for creating config files!)
- **Right-click**: Exit the application

## 🤖 Auto-positioning for NFL games

Double-clicking ScoreBlocker 2000 will look at any open Chrome, Firefox, or Edge
windows for an NFL game. If it finds one, it figures out which broadcast network
the game is on, looks up where that network shows its other-games score ticker
in the broadcast frame, and snaps the window over the ticker on whichever
monitor the game is on.

The window border briefly flashes:
- **green** if it found a game and snapped (or if the network is one that's
  known not to show an other-games ticker, in which case it leaves the window
  where it is)
- **yellow** if it found an NFL game but doesn't have ticker data for that
  (network, season) yet — typical for new seasons before the data is refreshed
- **red** if it can't find an NFL game in any open browser window

Press **`c`** with the window focused to snap to the most-recent known CBS
ticker position on the monitor the window is on; **`f`** does the same for FOX.

There's no AI here — auto-positioning is just a lookup against a database of
known ticker positions that was built once for the 2009-2025 seasons and gets
updated annually. The (game URL → broadcast network) data comes from the
[506sports](https://archive.506sports.com/) wiki archive; the per-network
ticker positions were measured by hand-annotating broadcast frames captured
from NFL+ Full Game Replays. See
[github.com/agentmorris/auto-scoreblock](https://github.com/agentmorris/auto-scoreblock)
for how the database is built and how to update it for a new season.

## 🏁 Getting Started

### Installation

* Ensure you have Python installed on your Windows system
* Clone or download this repository

### Running Single Instance

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

### Multi-Monitor Setup (Recommended for Multiple Windows)

For launching two ScoreBlocker windows simultaneously on specific monitors:

**Step 1: Create your configuration files**

Create JSON configuration files with your desired window positions. Sample configs are provided in `configs/monitor1.json` and `configs/monitor2.json`:

```json
{
  "primary": {
    "x": 100,
    "y": 50,
    "width": 300,
    "height": 150
  },
  "secondary": {
    "x": 1500,
    "y": 50,
    "width": 300,
    "height": 150
  },
  "background_color": "#000000",
  "border_color": "#D3D3D3"
}
```

You can store config files anywhere (even outside the repo) and reference them by path.

**Step 2: Launch your monitor setup**

Use the provided VBS launcher scripts:
- `scoreblocker_launch_monitor1.vbs` - Launches two windows using `configs/monitor1.json`
- `scoreblocker_launch_monitor2.vbs` - Launches two windows using `configs/monitor2.json`
- `scoreblocker_close_all.vbs` - Closes all running ScoreBlocker instances

Or use the command line:
```bash
python launch_monitor.py configs/monitor1.json
```

**Step 3: Create desktop shortcuts**

Create desktop shortcuts to `launch_monitor1.vbs` and `launch_monitor2.vbs` for quick access to your different monitor setups.

### Configuration File Format

Configuration files specify two window positions (primary and secondary) plus color settings:

```json
{
  "primary": {
    "x": 100,
    "y": 50,
    "width": 300,
    "height": 150
  },
  "secondary": {
    "x": 1500,
    "y": 50,
    "width": 300,
    "height": 150
  },
  "background_color": "#000000",
  "border_color": "#D3D3D3"
}
```

Customize `background_color` and `border_color` using hex color codes (e.g., "#FF0000" for red).

## 🏅 Technical Requirements

- **Operating System**: Windows
- **Python**: Any version with tkinter (usually included)

## ⚙️ Advanced Usage

### Command Line Options

```bash
python score_blocker.py --help
```

Available options:
- `--config_file PATH` - Use a specific configuration file
- `--position primary|secondary` - Launch at specific position from config
- `--close_all` - Close all running ScoreBlocker instances

### Custom Launchers

You can create your own launcher scripts to set up multiple windows with different configurations. See `launch_monitor.py` for an example.

## 🤝 Contributing

Found a bug? Want to add a feature? We welcome contributions! This is open-source software under the MIT license.

## 📜 License

MIT
