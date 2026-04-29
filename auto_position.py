"""
Auto-position a ScoreBlocker window over the "other games" score ticker for
the NFL game playing in the user's browser.

Public API:

    decide_position() -> Decision

    Decision is a dataclass:
      kind:    'ticker' | 'no_ticker' | 'unreviewed' | 'no_game' | 'unsupported'
      rect:    Optional[(x, y, w, h)] in absolute screen pixels (only for 'ticker')
      detail:  short human-readable message (for logging)

ScoreBlocker calls decide_position() on double-click and uses `kind` to pick
a flash colour and whether to move the overlay.

Windows-only for now (browser-window enumeration uses Win32 APIs). On other
OSes decide_position() returns kind='unsupported'.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass

try:
    from auto_scoreblock_data import SCORE_REGIONS, GAMES, NETWORK_SLUG
except ImportError:
    SCORE_REGIONS = {}
    GAMES = {}
    NETWORK_SLUG = {}


BROWSER_EXES = ('chrome.exe', 'firefox.exe', 'msedge.exe')

# nfl.com Game Center page titles look like:
#   "Los Angeles Chargers at Denver Broncos 2024 REG 6 - Game Center"
# Browsers append their own suffix (" - Google Chrome", " — Mozilla Firefox",
# " - Microsoft​Edge"). The regex matches the embedded page title.
TITLE_RE = re.compile(
    r'(.+?) at (.+?) (\d{4}) (REG|POST) (\d+)',
    re.IGNORECASE,
)

EDGE_SNAP_THRESHOLD = 0.01


@dataclass
class Decision:
    kind: str
    rect: tuple[int, int, int, int] | None = None
    detail: str = ''


# ----- Windows browser/window enumeration -----------------------------------

def _enumerate_browser_windows():
    """Yield (hwnd, title, exe_basename) for visible top-level browser windows.

    Uses ctypes to call Win32 APIs directly so we don't take a pywin32 dep.
    """
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    psapi = ctypes.windll.psapi

    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

    EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    found: list[tuple[int, str, str]] = []

    def _exe_for_pid(pid: int) -> str:
        h = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not h:
            return ''
        try:
            buf = ctypes.create_unicode_buffer(1024)
            size = wintypes.DWORD(len(buf))
            if kernel32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(size)):
                full = buf.value
                # Basename only
                return full.rsplit('\\', 1)[-1].lower()
            return ''
        finally:
            kernel32.CloseHandle(h)

    def _callback(hwnd, _lparam):
        if not user32.IsWindowVisible(hwnd):
            return True
        length = user32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return True
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        title = buf.value
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        exe = _exe_for_pid(pid.value)
        if exe in BROWSER_EXES:
            found.append((hwnd, title, exe))
        return True

    user32.EnumWindows(EnumWindowsProc(_callback), 0)
    return found


def _window_rect(hwnd: int) -> tuple[int, int, int, int] | None:
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    rect = wintypes.RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        return None
    return (rect.left, rect.top, rect.right, rect.bottom)


def _monitor_for_point(x: int, y: int) -> tuple[int, int, int, int] | None:
    """Return (left, top, width, height) of the monitor containing (x, y),
    or None if no monitor was found."""
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    MONITOR_DEFAULTTONEAREST = 2

    class POINT(ctypes.Structure):
        _fields_ = [('x', wintypes.LONG), ('y', wintypes.LONG)]

    class MONITORINFO(ctypes.Structure):
        _fields_ = [
            ('cbSize', wintypes.DWORD),
            ('rcMonitor', wintypes.RECT),
            ('rcWork', wintypes.RECT),
            ('dwFlags', wintypes.DWORD),
        ]

    pt = POINT(x, y)
    hmon = user32.MonitorFromPoint(pt, MONITOR_DEFAULTTONEAREST)
    if not hmon:
        return None
    info = MONITORINFO()
    info.cbSize = ctypes.sizeof(MONITORINFO)
    if not user32.GetMonitorInfoW(hmon, ctypes.byref(info)):
        return None
    r = info.rcMonitor
    return (r.left, r.top, r.right - r.left, r.bottom - r.top)


# ----- Title parsing & game lookup ------------------------------------------

def _title_is_nfl(title: str) -> bool:
    """True if the window title looks like an NFL.com Game Center page."""
    return TITLE_RE.search(title) is not None


def _find_record_for_title(title: str):
    """Parse an NFL.com Game Center title and return (away, home, network, year)
    from the embedded data, or None if we can't disambiguate (e.g. the year /
    week isn't in our games lookup, or the team names don't match)."""
    m = TITLE_RE.search(title)
    if not m:
        return None
    away_full, home_full, year, season_type, week = m.groups()
    try:
        year = int(year)
        week = int(week)
    except ValueError:
        return None
    season_type = season_type.lower()

    candidates = GAMES.get((year, season_type, week))
    if not candidates:
        return None

    away_lower = away_full.lower()
    home_lower = home_full.lower()
    for away, home, network in candidates:
        if away.lower() in away_lower and home.lower() in home_lower:
            return (away, home, network, year)
    return None


# ----- Coordinate math ------------------------------------------------------

def _snap_to_edge(v: float) -> float:
    if v < EDGE_SNAP_THRESHOLD:
        return 0.0
    if v > 1.0 - EDGE_SNAP_THRESHOLD:
        return 1.0
    return v


def latest_ticker_rect_for(network_slug: str):
    """Return the most-recent ticker rect for a network slug, or None.

    Searches SCORE_REGIONS for keys "<slug>_<year>" with status='ticker' and
    returns the rect for the highest year. Used by the c/f keyboard
    shortcuts to "snap to the most-recent CBS/FOX ticker position".
    """
    best_year = -1
    best_rect = None
    prefix = f'{network_slug}_'
    for key, val in SCORE_REGIONS.items():
        if not key.startswith(prefix):
            continue
        if val.get('status') != 'ticker':
            continue
        try:
            year = int(key[len(prefix):])
        except ValueError:
            continue
        if year > best_year:
            best_year = year
            best_rect = val['rect']
    return best_rect


def monitor_for_point(x: int, y: int):
    """Public alias for the internal monitor lookup."""
    return _monitor_for_point(x, y)


def normalized_to_screen(rect_norm, monitor) -> tuple[int, int, int, int]:
    """Convert a normalized [xmin, ymin, xmax, ymax] (relative to the 16:9
    video frame) into absolute screen pixels for the given monitor.

    Assumes fullscreen playback: video occupies the full width of the monitor
    and is vertically centered. If the monitor is narrower than 16:9 (rare),
    falls back to full-height with horizontal centering.
    """
    x_min, y_min, x_max, y_max = (_snap_to_edge(v) for v in rect_norm)
    M_x, M_y, M_w, M_h = monitor

    video_w = M_w
    video_h = video_w * 9 / 16
    if video_h > M_h:
        video_h = M_h
        video_w = video_h * 16 / 9
        video_x = M_x + (M_w - video_w) / 2
        video_y = M_y
    else:
        video_x = M_x
        video_y = M_y + (M_h - video_h) / 2

    sx = round(video_x + x_min * video_w)
    sy = round(video_y + y_min * video_h)
    sw = round((x_max - x_min) * video_w)
    sh = round((y_max - y_min) * video_h)
    return sx, sy, sw, sh


# ----- Public entry point ---------------------------------------------------

def decide_position() -> Decision:
    if sys.platform != 'win32':
        return Decision('unsupported', None,
                        f'Auto-position is Windows-only (running on {sys.platform})')

    if not SCORE_REGIONS or not GAMES:
        return Decision('unsupported', None,
                        'auto_scoreblock_data not loaded')

    try:
        windows = _enumerate_browser_windows()
    except Exception as e:
        return Decision('no_game', None, f'Window enumeration failed: {e}')

    saw_nfl_tab = False

    for hwnd, title, _exe in windows:
        if not _title_is_nfl(title):
            continue
        saw_nfl_tab = True
        match = _find_record_for_title(title)
        if not match:
            # NFL game tab, but year/week not in our lookup or no team-name
            # match. Treat as "haven't annotated this cell yet."
            continue
        away, home, network, year = match
        slug = NETWORK_SLUG.get(network)
        if slug is None:
            continue  # Unknown network → also unreviewed-ish
        cell_key = f'{slug}_{year}'
        cell = SCORE_REGIONS.get(cell_key)

        wrect = _window_rect(hwnd)
        if wrect is None:
            return Decision('no_game', None, 'Could not get window rect')
        wl, wt, wr, wb = wrect
        cx = (wl + wr) // 2
        cy = (wt + wb) // 2
        monitor = _monitor_for_point(cx, cy)
        if monitor is None:
            return Decision('no_game', None, 'No monitor found for window')

        if cell is None:
            return Decision('unreviewed', None,
                            f'{cell_key}: not yet annotated')
        if cell['status'] == 'no_ticker':
            return Decision('no_ticker', None,
                            f'{cell_key}: known no ticker')
        if cell['status'] == 'ticker':
            sx, sy, sw, sh = normalized_to_screen(cell['rect'], monitor)
            return Decision('ticker', (sx, sy, sw, sh),
                            f'{cell_key}: {away} @ {home}')

        return Decision('unreviewed', None, f'{cell_key}: unknown status')

    if saw_nfl_tab:
        return Decision('unreviewed', None,
                        'Found NFL game tab but cell not in data')
    return Decision('no_game', None, 'No NFL game found in any browser window')
