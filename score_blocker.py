#!/usr/bin/env python3
"""
Score Blocker 2000 - A simple overlay window to block scores on screen
"""

import tkinter as tk
import json
import os
from typing import Dict, Any

class ScoreBlocker:
    def __init__(self):
        self.root = tk.Tk()
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.settings_file = os.path.join(script_dir, "score_blocker_settings.json")
        self.dragging = False
        self.resizing = False
        self.resize_edge = None
        self.start_x = 0
        self.start_y = 0
        self.start_width = 0
        self.start_height = 0
        
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
        
        # Set black background
        self.root.configure(bg='black')
        
        # Set cursor to hand when hovering
        self.root.configure(cursor='hand2')
        
        # Create label for text display (initially hidden)
        self.text_label = tk.Label(
            self.root,
            text="ScoreBlocker 2000",
            fg='black',  # Start hidden (same color as background)
            bg='black',
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
                    # Load primary position (last known position)
                    primary = settings.get('primary', {})
                    x = primary.get('x', 100)
                    y = primary.get('y', 100)
                    width = primary.get('width', 200)
                    height = primary.get('height', 100)
                    self.root.geometry(f"{width}x{height}+{x}+{y}")
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
            }
        }
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(default_settings, f, indent=2)
        except Exception as e:
            print(f"Error creating default settings: {e}")
            
    def save_settings(self):
        """Save current position and size to primary position in settings file"""
        try:
            x = self.root.winfo_x()
            y = self.root.winfo_y()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            
            # Load existing settings to preserve secondary position
            settings = {
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
                }
            }
            
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
            
            # Update only the primary position
            settings['primary'] = {
                'x': x,
                'y': y,
                'width': width,
                'height': height
            }
            
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
            
    def bind_events(self):
        """Bind mouse events for interaction"""
        # Bind events to both root and label to ensure consistent behavior
        for widget in [self.root, self.text_label]:
            widget.bind('<Button-1>', self.on_click)
            widget.bind('<B1-Motion>', self.on_drag)
            widget.bind('<ButtonRelease-1>', self.on_release)
            widget.bind('<Double-Button-1>', self.on_double_click)
            widget.bind('<Button-3>', self.on_right_click)  # Right-click
            widget.bind('<Motion>', self.on_motion)
        
        # Use a single enter/leave on root only, and check mouse position in motion
        self.root.bind('<Enter>', self.on_enter)
        self.root.bind('<Leave>', self.on_leave)
        
    def on_enter(self, event):
        """Show white border and text when mouse enters window"""
        self.root.configure(highlightbackground='white', highlightthickness=2)
        self.text_label.configure(fg='white')  # Make text visible
        
    def on_leave(self, event):
        """Hide border and text when mouse leaves window"""
        self.root.configure(highlightthickness=0)
        self.text_label.configure(fg='black')  # Hide text by making it same color as background
        
    def on_motion(self, event):
        """Handle mouse motion for cursor changes at edges"""
        # Ensure border and text remain visible during motion within window
        self.root.configure(highlightbackground='white', highlightthickness=2)
        self.text_label.configure(fg='white')
        
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        # Check if near bottom-right corner (within 10 pixels of both edges)
        if width - event.x <= 10 and height - event.y <= 10:
            self.root.configure(cursor='sizing')
        # Check if near right edge (within 10 pixels)
        elif width - event.x <= 10:
            self.root.configure(cursor='sb_h_double_arrow')
        # Check if near bottom edge (within 10 pixels)
        elif height - event.y <= 10:
            self.root.configure(cursor='sb_v_double_arrow')
        else:
            self.root.configure(cursor='hand2')
            
    def on_click(self, event):
        """Handle mouse click - start dragging or resizing"""
        self.start_x = event.x_root
        self.start_y = event.y_root
        
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        # Check if clicking near bottom-right corner for diagonal resizing
        if width - event.x <= 10 and height - event.y <= 10:
            self.resizing = True
            self.resize_edge = 'diagonal'
            self.start_width = width
            self.start_height = height
        # Check if clicking near right edge for horizontal resizing
        elif width - event.x <= 10:
            self.resizing = True
            self.resize_edge = 'right'
            self.start_width = width
        # Check if clicking near bottom edge for vertical resizing
        elif height - event.y <= 10:
            self.resizing = True
            self.resize_edge = 'bottom'
            self.start_height = height
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
            # Resize the window
            if self.resize_edge == 'right':
                dx = event.x_root - self.start_x
                new_width = max(50, self.start_width + dx)  # Minimum width of 50
                height = self.root.winfo_height()
                x = self.root.winfo_x()
                y = self.root.winfo_y()
                self.root.geometry(f"{new_width}x{height}+{x}+{y}")
                
            elif self.resize_edge == 'bottom':
                dy = event.y_root - self.start_y
                new_height = max(30, self.start_height + dy)  # Minimum height of 30
                width = self.root.winfo_width()
                x = self.root.winfo_x()
                y = self.root.winfo_y()
                self.root.geometry(f"{width}x{new_height}+{x}+{y}")
                
            elif self.resize_edge == 'diagonal':
                dx = event.x_root - self.start_x
                dy = event.y_root - self.start_y
                new_width = max(50, self.start_width + dx)  # Minimum width of 50
                new_height = max(30, self.start_height + dy)  # Minimum height of 30
                x = self.root.winfo_x()
                y = self.root.winfo_y()
                self.root.geometry(f"{new_width}x{new_height}+{x}+{y}")
                
    def on_release(self, event):
        """Handle mouse release - stop dragging/resizing and save settings"""
        self.dragging = False
        self.resizing = False
        self.resize_edge = None
        self.save_settings()
        
    def on_double_click(self, event):
        """Handle double-click - close the application"""
        self.save_settings()
        self.root.quit()
        
    def on_right_click(self, event):
        """Handle right-click - switch to secondary position"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    secondary = settings.get('secondary', {})
                    x = secondary.get('x', 300)
                    y = secondary.get('y', 200)
                    width = secondary.get('width', 200)
                    height = secondary.get('height', 100)
                    self.root.geometry(f"{width}x{height}+{x}+{y}")
        except Exception as e:
            print(f"Error loading secondary position: {e}")
        
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = ScoreBlocker()
    app.run()