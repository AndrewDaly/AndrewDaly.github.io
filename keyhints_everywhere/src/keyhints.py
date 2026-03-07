"""
KeyHints Everywhere - Vimium-style key hints for any Windows application
Scans UI elements and overlays 2-letter hints for keyboard-only navigation
"""

import time
import pyautogui
import uiautomation as automation
import pygetwindow
import keyboard
import threading
import tkinter as tk
import itertools
import sys
from collections import defaultdict


class KeyHintsOverlay:
    """Manages the transparent overlay with key hints"""
    
    def __init__(self, coordinates):
        self.coordinates = coordinates
        self.root = None
        self.buttons = {}
        self.typed_keys = ""
        
    def create_overlay(self):
        """Create a fullscreen transparent overlay with hint buttons"""
        self.root = tk.Tk()
        self.root.title("KeyHints Overlay")
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-alpha", 0.5)
        self.root.attributes("-topmost", True)
        self.root.configure(bg='black')
        self.root.focus_force()
        
        # Generate unique two-character labels
        letters = "abcdefghiklmnopqrstuvwxyz"
        labels = ["".join(pair) for pair in itertools.product(letters, repeat=2)]
        
        # Create hint buttons for each coordinate
        for (x, y), label in zip(self.coordinates, labels):
            if len(self.buttons) >= len(labels):
                break
                
            button = tk.Button(
                self.root, 
                text=label, 
                width=2, 
                height=1, 
                bg="#ffff00",  # Bright yellow
                fg="#000000",  # Black text
                font=('Consolas', 10, 'bold'),
                relief=tk.FLAT,
                borderwidth=2
            )
            
            self.buttons[label] = {
                'widget': button,
                'x': x,
                'y': y
            }
            
            # Center button at coordinate
            button.place(x=x, y=y-5, width=28, height=22)
        
        # Status label at bottom
        self.status_label = tk.Label(
            self.root,
            text=f"Type hint to click | {len(self.buttons)} hints | ESC to cancel",
            bg='#1e1e1e',
            fg='#00ff00',
            font=('Consolas', 14, 'bold'),
            pady=10
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Typing display
        self.typing_label = tk.Label(
            self.root,
            text="",
            bg='#1e1e1e',
            fg='#ffff00',
            font=('Consolas', 24, 'bold'),
            pady=5
        )
        self.typing_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind keyboard events
        self.root.bind("<Key>", self.on_key)
        self.root.bind("<Escape>", lambda e: self.close())
        
        self.root.mainloop()
    
    def on_key(self, event):
        """Handle key press events"""
        char = event.char.lower()
        
        # Ignore non-letter keys
        if not char.isalpha():
            return
        
        self.typed_keys += char
        self.typing_label.config(text=f"Typed: {self.typed_keys}")
        
        # Check if we have a match
        if self.typed_keys in self.buttons:
            btn_info = self.buttons[self.typed_keys]
            x_coord = btn_info['x'] + 14  # Center of button
            y_coord = btn_info['y'] + 11
            
            print(f"Match found: {self.typed_keys} -> ({x_coord}, {y_coord})")
            
            # Close overlay
            self.root.destroy()
            
            # Small delay to ensure overlay is gone
            time.sleep(0.1)
            
            # Move mouse and click
            try:
                pyautogui.moveTo(x_coord, y_coord, duration=0.1)
                pyautogui.click(x_coord, y_coord)
            except Exception as e:
                print(f"Click error: {e}")
            
            self.typed_keys = ""
            
        elif len(self.typed_keys) >= 2:
            # No match, reset
            self.typed_keys = ""
            self.typing_label.config(text="No match - try again")
            self.root.after(1000, lambda: self.typing_label.config(text=""))
    
    def close(self):
        """Close the overlay"""
        if self.root:
            self.root.destroy()


class UIScanner:
    """Scans Windows UI elements using UI Automation"""
    
    def __init__(self):
        self.coordinates = []
        self.seen_coords = set()
        
        # Control types we're interested in
        self.target_control_types = {
            'ButtonControl',
            'MenuItemControl',
            'TabItemControl',
            'ListItemControl',
            'TreeItemControl',
            'HyperlinkControl',
            'CheckBoxControl',
            'RadioButtonControl',
            'ComboBoxControl',
            'EditControl',
            'TextControl',
        }
    
    def scan_window(self, window_title=None):
        """Scan active window for clickable elements"""
        self.coordinates = []
        self.seen_coords = set()
        
        try:
            desktop = automation.GetRootControl()
            active_window_title = pyautogui.getActiveWindowTitle()
            
            if not active_window_title:
                print("No active window found")
                return []
            
            print(f"Scanning window: {active_window_title}")
            
            # Find the active window
            for window in desktop.GetChildren():
                if window.Name == active_window_title:
                    print(f"Found window: {window.Name} (Class: {window.ClassName})")
                    self.scan_control(window)
                    break
            
            print(f"Found {len(self.coordinates)} unique clickable elements")
            return self.coordinates
            
        except Exception as e:
            print(f"Scan error: {e}")
            return []
    
    def scan_control(self, control, level=0):
        """Recursively scan a control and its children"""
        try:
            # Get bounding rectangle
            rect = control.BoundingRectangle
            if rect and rect.width() > 0 and rect.height() > 0:
                x, y = rect.left + rect.width() // 2, rect.top + rect.height() // 2
                
                # Check if this is a control type we care about
                control_type = control.ControlTypeName
                
                # Avoid duplicate coordinates (within 5px tolerance)
                coord_key = (x // 5, y // 5)
                
                if coord_key not in self.seen_coords:
                    # Add controls that are clickable/interactive
                    if (control_type in self.target_control_types or 
                        control.IsEnabled and control.BoundingRectangle.width() < 500):
                        
                        self.coordinates.append((x, y))
                        self.seen_coords.add(coord_key)
                        
                        print(f"{'  ' * level}{control.Name[:40]} | {control_type} | ({x}, {y})")
            
            # Scan children (limit depth to avoid too much recursion)
            if level < 15:
                children = control.GetChildren()
                for child in children:
                    self.scan_control(child, level + 1)
                    
        except Exception as e:
            # Silently skip controls that error out
            pass


class KeyHintsApp:
    """Main application class"""
    
    def __init__(self):
        self.scanner = UIScanner()
        self.overlay = None
        self.is_active = False
    
    def activate_immediate(self):
        """Scan and show hints immediately (for test mode)"""
        print("\n" + "="*60)
        print("KeyHints Activated!")
        print("="*60)
        
        try:
            # Initialize COM (we're in main thread for test mode)
            desktop = automation.GetRootControl()
            
            # Scan the active window
            coordinates = self.scanner.scan_window()
            
            if not coordinates:
                print("No clickable elements found!")
                return
            
            # Create and show overlay
            self.overlay = KeyHintsOverlay(coordinates)
            self.overlay.create_overlay()
            
        except Exception as e:
            print(f"Activation error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("KeyHints deactivated")
    
    def scan_in_thread(self):
        """Scan UI in background thread, then show overlay in main thread"""
        try:
            # Initialize COM for this thread
            initializer = automation.UIAutomationInitializerInThread()
            
            # Scan the active window
            coordinates = self.scanner.scan_window()
            
            # Clean up COM
            del initializer
            
            if coordinates:
                # Store coordinates for main thread
                self.pending_coordinates = coordinates
            else:
                print("No clickable elements found!")
                self.is_active = False
                
        except Exception as e:
            print(f"Scan error: {e}")
            import traceback
            traceback.print_exc()
            self.is_active = False
    
    def run_with_hotkey(self, hotkey='ctrl+shift+k'):
        """Run the app with a global hotkey"""
        print(f"KeyHints Everywhere - Starting...")
        print(f"Press {hotkey.upper()} to activate hints on any window")
        print(f"Press CTRL+C to exit\n")
        
        self.pending_coordinates = None
        
        def hotkey_handler():
            """Handle hotkey - scan in thread, show overlay when ready"""
            if self.is_active:
                print("Already active, ignoring...")
                return
                
            self.is_active = True
            print("\n" + "="*60)
            print("KeyHints Activated!")
            print("="*60)
            
            # Start scanning in background thread
            threading.Thread(target=self.scan_in_thread, daemon=True).start()
        
        def check_for_overlay():
            """Check if scan is complete and show overlay"""
            if self.pending_coordinates is not None:
                coords = self.pending_coordinates
                self.pending_coordinates = None
                
                # Show overlay in main thread
                self.overlay = KeyHintsOverlay(coords)
                self.overlay.create_overlay()
                
                self.is_active = False
                print("KeyHints deactivated")
        
        # Register the hotkey
        keyboard.add_hotkey(hotkey, hotkey_handler)
        
        # Create a simple tkinter window to keep event loop running
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Periodically check for pending overlays
        def periodic_check():
            check_for_overlay()
            root.after(100, periodic_check)  # Check every 100ms
        
        periodic_check()
        
        try:
            # Keep running
            root.mainloop()
        except KeyboardInterrupt:
            print("\nExiting...")


def main():
    """Entry point"""
    app = KeyHintsApp()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        # Test mode - scan current window immediately
        print("Test mode - scanning active window now...")
        app.activate_immediate()
    else:
        # Normal mode - run with hotkey
        app.run_with_hotkey('ctrl+shift+k')


if __name__ == '__main__':
    main()
