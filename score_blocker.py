#!/usr/bin/env python3
"""
Score Blocker 2000 - A simple overlay window to block scores on screen
"""

import json
import os
import argparse
import subprocess
import sys
from typing import Dict, Any

# Enable unbuffered output
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except:
        pass

class ScoreBlocker:
    def __init__(self, config_file=None, position='primary'):
        import tkinter as tk
        self.tk = tk  # Store reference to tk module
        self.root = tk.Tk()
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Use specified config file or default to score_blocker_settings.json
        if config_file:
            self.settings_file = config_file
        else:
            self.settings_file = os.path.join(script_dir, "score_blocker_settings.json")

        self.position = position  # 'primary' or 'secondary'
        self.dragging = False
        self.resizing = False
        self.resize_edge = None
        self.start_x = 0
        self.start_y = 0
        self.start_width = 0
        self.start_height = 0
        self.background_color = '#000000'
        self.border_color = '#D3D3D3'

        self.setup_window()
        self.load_settings()
        self.bind_events()
        
    def setup_window(self):
        """Configure the main window properties"""
        # Remove window decorations and make it frameless
        self.root.overrideredirect(True)
        
        # Set initial size and position
        self.root.geometry("200x100+100+100")
        
        # Make window always on top
        self.root.attributes('-topmost', True)
        
        # Set background color (will be updated when settings load)
        self.root.configure(bg=self.background_color)
        
        # Show border by default
        self.root.configure(highlightbackground=self.border_color, highlightthickness=2)
        
        # Set cursor to hand when hovering
        self.root.configure(cursor='hand2')
        
        # Create label for text display (initially hidden)
        self.text_label = self.tk.Label(
            self.root,
            text="ScoreBlocker 2000",
            fg=self.background_color,  # Start hidden (same color as background)
            bg=self.background_color,
            font=('Arial', 8, 'normal'),
            justify='right'
        )
        # Position it in the lower-right corner
        self.text_label.place(relx=1.0, rely=1.0, anchor='se', x=-5, y=-5)
        
    def load_settings(self):
        """Load position and size from settings file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    # Load specified position (primary or secondary)
                    position_settings = settings.get(self.position, {})
                    x = position_settings.get('x', 100)
                    y = position_settings.get('y', 100)
                    width = position_settings.get('width', 200)
                    height = position_settings.get('height', 100)
                    self.root.geometry(f"{width}x{height}+{x}+{y}")

                    # Load color settings
                    self.background_color = settings.get('background_color', '#000000')
                    self.border_color = settings.get('border_color', '#D3D3D3')

                    # Apply colors to UI
                    self.root.configure(bg=self.background_color, highlightbackground=self.border_color, highlightthickness=2)
                    self.text_label.configure(bg=self.background_color, fg=self.background_color)
            else:
                # Create initial settings file with default positions
                self.create_default_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.create_default_settings()
            
    def create_default_settings(self):
        """Create default settings file"""
        default_settings = {
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
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(default_settings, f, indent=2)
        except Exception as e:
            print(f"Error creating default settings: {e}")
            
            
    def bind_events(self):
        """Bind mouse events for interaction"""
        # Bind events to both root and label to ensure consistent behavior
        for widget in [self.root, self.text_label]:
            widget.bind('<Button-1>', self.on_click)
            widget.bind('<B1-Motion>', self.on_drag)
            widget.bind('<ButtonRelease-1>', self.on_release)
            widget.bind('<Button-2>', self.on_middle_click)  # Middle-click
            widget.bind('<ButtonRelease-3>', self.on_right_release)  # Right-click release (exit)
            widget.bind('<Motion>', self.on_motion)

        # Use a single enter/leave on root only, and check mouse position in motion
        self.root.bind('<Enter>', self.on_enter)
        self.root.bind('<Leave>', self.on_leave)
        
    def on_enter(self, event):
        """Show text when mouse enters window"""
        self.text_label.configure(fg=self.border_color)  # Make text visible
        
    def on_leave(self, event):
        """Hide text when mouse leaves window"""
        self.text_label.configure(fg=self.background_color)  # Hide text by making it same color as background
        
    def on_motion(self, event):
        """Handle mouse motion for cursor changes at edges"""
        # Ensure text remains visible during motion within window
        self.text_label.configure(fg=self.border_color)
        
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        # Check corners first (within 10 pixels of both edges)
        if event.x <= 10 and event.y <= 10:  # Top-left corner
            self.root.configure(cursor='sizing')
        elif width - event.x <= 10 and event.y <= 10:  # Top-right corner
            self.root.configure(cursor='sizing')
        elif event.x <= 10 and height - event.y <= 10:  # Bottom-left corner
            self.root.configure(cursor='sizing')
        elif width - event.x <= 10 and height - event.y <= 10:  # Bottom-right corner
            self.root.configure(cursor='sizing')
        # Check edges (within 10 pixels)
        elif event.x <= 10:  # Left edge
            self.root.configure(cursor='sb_h_double_arrow')
        elif width - event.x <= 10:  # Right edge
            self.root.configure(cursor='sb_h_double_arrow')
        elif event.y <= 10:  # Top edge
            self.root.configure(cursor='sb_v_double_arrow')
        elif height - event.y <= 10:  # Bottom edge
            self.root.configure(cursor='sb_v_double_arrow')
        else:
            self.root.configure(cursor='hand2')
            
    def on_click(self, event):
        """Handle mouse click - start dragging or resizing"""
        self.start_x = event.x_root
        self.start_y = event.y_root
        
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        # Store initial position for resizing operations that need it
        self.start_win_x = self.root.winfo_x()
        self.start_win_y = self.root.winfo_y()
        self.start_width = width
        self.start_height = height
        
        # Check corners first (within 10 pixels of both edges)
        if event.x <= 10 and event.y <= 10:  # Top-left corner
            self.resizing = True
            self.resize_edge = 'top_left'
        elif width - event.x <= 10 and event.y <= 10:  # Top-right corner
            self.resizing = True
            self.resize_edge = 'top_right'
        elif event.x <= 10 and height - event.y <= 10:  # Bottom-left corner
            self.resizing = True
            self.resize_edge = 'bottom_left'
        elif width - event.x <= 10 and height - event.y <= 10:  # Bottom-right corner
            self.resizing = True
            self.resize_edge = 'bottom_right'
        # Check edges (within 10 pixels)
        elif event.x <= 10:  # Left edge
            self.resizing = True
            self.resize_edge = 'left'
        elif width - event.x <= 10:  # Right edge
            self.resizing = True
            self.resize_edge = 'right'
        elif event.y <= 10:  # Top edge
            self.resizing = True
            self.resize_edge = 'top'
        elif height - event.y <= 10:  # Bottom edge
            self.resizing = True
            self.resize_edge = 'bottom'
        else:
            self.dragging = True
            
    def on_drag(self, event):
        """Handle mouse drag - move window or resize"""
        if self.dragging:
            # Move the window
            dx = event.x_root - self.start_x
            dy = event.y_root - self.start_y
            new_x = self.root.winfo_x() + dx
            new_y = self.root.winfo_y() + dy
            self.root.geometry(f"+{new_x}+{new_y}")
            self.start_x = event.x_root
            self.start_y = event.y_root
            
        elif self.resizing:
            dx = event.x_root - self.start_x
            dy = event.y_root - self.start_y
            
            # Calculate new dimensions based on resize edge/corner
            new_x = self.start_win_x
            new_y = self.start_win_y  
            new_width = self.start_width
            new_height = self.start_height
            
            if self.resize_edge == 'right':
                new_width = max(50, self.start_width + dx)
                
            elif self.resize_edge == 'left':
                new_width = max(50, self.start_width - dx)
                new_x = self.start_win_x + dx if new_width > 50 else self.start_win_x + (self.start_width - 50)
                
            elif self.resize_edge == 'bottom':
                new_height = max(30, self.start_height + dy)
                
            elif self.resize_edge == 'top':
                new_height = max(30, self.start_height - dy)
                new_y = self.start_win_y + dy if new_height > 30 else self.start_win_y + (self.start_height - 30)
                
            elif self.resize_edge == 'top_left':
                new_width = max(50, self.start_width - dx)
                new_height = max(30, self.start_height - dy)
                new_x = self.start_win_x + dx if new_width > 50 else self.start_win_x + (self.start_width - 50)
                new_y = self.start_win_y + dy if new_height > 30 else self.start_win_y + (self.start_height - 30)
                
            elif self.resize_edge == 'top_right':
                new_width = max(50, self.start_width + dx)
                new_height = max(30, self.start_height - dy)
                new_y = self.start_win_y + dy if new_height > 30 else self.start_win_y + (self.start_height - 30)
                
            elif self.resize_edge == 'bottom_left':
                new_width = max(50, self.start_width - dx)
                new_height = max(30, self.start_height + dy)
                new_x = self.start_win_x + dx if new_width > 50 else self.start_win_x + (self.start_width - 50)
                
            elif self.resize_edge == 'bottom_right':
                new_width = max(50, self.start_width + dx)
                new_height = max(30, self.start_height + dy)
            
            self.root.geometry(f"{int(new_width)}x{int(new_height)}+{int(new_x)}+{int(new_y)}")
                
    def on_release(self, event):
        """Handle mouse release - stop dragging/resizing"""
        self.dragging = False
        self.resizing = False
        self.resize_edge = None

    def on_right_release(self, event):
        """Handle right-click release - close the application"""
        self.root.quit()
        return "break"  # Prevent event from propagating to windows below

    def on_middle_click(self, event):
        """Handle middle-click - show and copy coordinates to clipboard"""
        try:
            # Get current window position and size
            x = self.root.winfo_x()
            y = self.root.winfo_y()
            width = self.root.winfo_width()
            height = self.root.winfo_height()

            # Format coordinates as JSON
            coord_text = f'{{"x": {x}, "y": {y}, "width": {width}, "height": {height}}}'

            # Copy to clipboard
            self.root.clipboard_clear()
            self.root.clipboard_append(coord_text)

            # Update label to show coordinates
            self.text_label.configure(
                text=f"Copied!\nx={x}, y={y}\nw={width}, h={height}",
                fg=self.border_color
            )

            # Reset text after 2 seconds
            self.root.after(2000, self.reset_label_text)

        except Exception as e:
            print(f"Error getting coordinates: {e}")

    def reset_label_text(self):
        """Reset label text back to default"""
        self.text_label.configure(text="ScoreBlocker 2000")

    def run(self):
        """Start the application"""
        self.root.mainloop()


def close_all_instances():
    """Close all running ScoreBlocker instances"""
    killed_count = 0

    try:
        # Use PowerShell with WMI to find processes by command line
        # Using -EncodedCommand to avoid quoting issues
        ps_script = (
            "$procs = Get-WmiObject Win32_Process -Filter \"Name='python.exe' OR Name='pythonw.exe'\"; "
            "$procs | Where-Object { $_.CommandLine -like '*score_blocker.py*' } | "
            "ForEach-Object { Write-Output $_.ProcessId }"
        )

        result = subprocess.run(
            ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', ps_script],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )

        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            current_pid = str(os.getpid())  # Get current process ID

            for pid in pids:
                pid = pid.strip()

                # Skip the current process to avoid killing ourselves
                if pid == current_pid:
                    continue

                if pid.isdigit():
                    try:
                        kill_result = subprocess.run(
                            ['taskkill', '/F', '/PID', pid],
                            capture_output=True,
                            text=True,
                            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                        )
                        if kill_result.returncode == 0:
                            print(f"Closed ScoreBlocker instance (PID: {pid})")
                            sys.stdout.flush()
                            killed_count += 1
                        else:
                            print(f"Failed to close PID {pid}: {kill_result.stderr}")
                            sys.stdout.flush()
                    except Exception as e:
                        print(f"Error killing process {pid}: {e}")
                        sys.stdout.flush()

        if killed_count > 0:
            print(f"Total instances closed: {killed_count}")
            sys.stdout.flush()
        else:
            print("No running ScoreBlocker instances found")
            sys.stdout.flush()

    except Exception as e:
        print(f"Error closing instances: {e}")
        sys.stdout.flush()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='ScoreBlocker 2000 - Block scores on screen')
    parser.add_argument('--config_file', type=str, help='Path to configuration file')
    parser.add_argument('--position', type=str, choices=['primary', 'secondary'],
                       default='primary', help='Which position to load from config (primary or secondary)')
    parser.add_argument('--close_all', action='store_true',
                       help='Close all running ScoreBlocker instances and exit')

    args = parser.parse_args()

    if args.close_all:
        try:
            close_all_instances()
            sys.exit(0)
        except Exception as e:
            print(f"Error in close_all: {e}")
            sys.stdout.flush()
            import traceback
            traceback.print_exc()
            sys.exit(1)

    try:
        app = ScoreBlocker(config_file=args.config_file, position=args.position)
        app.run()
    except Exception as e:
        print(f"Error running ScoreBlocker: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)