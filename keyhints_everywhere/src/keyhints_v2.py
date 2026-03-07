"""
KeyHints Everywhere v2 - Fast Win32 overlay version
Uses Win32 API for instant, non-intrusive hint overlay
"""

import time
import pyautogui
import uiautomation as automation
import keyboard
import threading
import itertools
import sys
import win32gui
import win32con
import win32api
from ctypes import windll, byref, sizeof, c_int


class FastOverlay:
    """Fast Win32-based transparent overlay"""
    
    def __init__(self, coordinates):
        self.coordinates = coordinates
        self.buttons = {}
        self.typed_keys = ""
        self.hwnd = None
        self.is_active = True
        
        # Generate hints
        letters = "abcdefghiklmnopqrstuvwxyz"
        labels = ["".join(pair) for pair in itertools.product(letters, repeat=2)]
        
        # Map coordinates to hints
        for (x, y), label in zip(coordinates, labels):
            if len(self.buttons) >= len(labels):
                break
            self.buttons[label] = {'x': x, 'y': y}
        
        print(f"Created {len(self.buttons)} hints")
    
    def create_overlay(self):
        """Create a transparent layered window using Win32 API"""
        
        # Register window class
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self.wnd_proc
        wc.lpszClassName = "KeyHintsOverlay"
        wc.hInstance = win32api.GetModuleHandle(None)
        wc.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        wc.hbrBackground = win32gui.GetStockObject(win32con.NULL_BRUSH)
        
        try:
            class_atom = win32gui.RegisterClass(wc)
        except Exception as e:
            # Class already registered
            class_atom = win32gui.WNDCLASS()
        
        # Get screen dimensions
        screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        
        # Create layered window (transparent, topmost, no activate)
        self.hwnd = win32gui.CreateWindowEx(
            win32con.WS_EX_LAYERED | win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_NOACTIVATE,
            "KeyHintsOverlay",
            "KeyHints",
            win32con.WS_POPUP,
            0, 0,
            screen_width, screen_height,
            0, 0,
            wc.hInstance,
            None
        )
        
        # Make window 50% transparent with black background
        win32gui.SetLayeredWindowAttributes(
            self.hwnd,
            win32api.RGB(0, 0, 0),
            128,  # 50% opacity
            win32con.LWA_ALPHA
        )
        
        # Show the window
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)
        win32gui.UpdateWindow(self.hwnd)
        
        # Draw hints
        self.draw_hints()
        
        # Message loop
        win32gui.PumpMessages()
    
    def wnd_proc(self, hwnd, msg, wparam, lparam):
        """Window procedure"""
        if msg == win32con.WM_PAINT:
            self.draw_hints()
            return 0
        elif msg == win32con.WM_DESTROY:
            win32gui.PostQuitMessage(0)
            return 0
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)
    
    def draw_hints(self):
        """Draw hint labels on the overlay"""
        if not self.hwnd:
            return
        
        hdc = win32gui.GetDC(self.hwnd)
        
        # Set transparent background
        win32gui.SetBkMode(hdc, win32con.TRANSPARENT)
        
        # Create yellow background brush and black text
        yellow_brush = win32gui.CreateSolidBrush(win32api.RGB(255, 255, 0))
        black_pen = win32gui.CreatePen(win32con.PS_SOLID, 2, win32api.RGB(0, 0, 0))
        
        # Select objects
        win32gui.SelectObject(hdc, yellow_brush)
        win32gui.SelectObject(hdc, black_pen)
        
        # Set text properties
        win32gui.SetTextColor(hdc, win32api.RGB(0, 0, 0))
        
        # Draw each hint button
        for label, coords in self.buttons.items():
            x, y = coords['x'], coords['y']
            
            # Draw rounded rectangle for button
            win32gui.RoundRect(hdc, x-14, y-11, x+14, y+11, 4, 4)
            
            # Draw text centered
            rect = (x-14, y-11, x+14, y+11)
            win32gui.DrawText(
                hdc,
                label,
                -1,
                rect,
                win32con.DT_CENTER | win32con.DT_VCENTER | win32con.DT_SINGLELINE
            )
        
        # Draw status bar at bottom
        screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        
        # Status background
        status_brush = win32gui.CreateSolidBrush(win32api.RGB(30, 30, 30))
        win32gui.SelectObject(hdc, status_brush)
        win32gui.Rectangle(hdc, 0, screen_height-100, screen_width, screen_height)
        
        # Status text
        win32gui.SetTextColor(hdc, win32api.RGB(0, 255, 0))
        status_text = f"Type hint to click | {len(self.buttons)} hints | ESC to cancel | Typed: {self.typed_keys}"
        status_rect = (10, screen_height-80, screen_width-10, screen_height-10)
        win32gui.DrawText(
            hdc,
            status_text,
            -1,
            status_rect,
            win32con.DT_LEFT | win32con.DT_VCENTER | win32con.DT_SINGLELINE
        )
        
        # Clean up
        win32gui.DeleteObject(yellow_brush)
        win32gui.DeleteObject(black_pen)
        win32gui.DeleteObject(status_brush)
        win32gui.ReleaseDC(self.hwnd, hdc)
    
    def on_key_press(self, event):
        """Handle global keyboard input"""
        if not self.is_active:
            return
        
        key = event.name.lower()
        
        # ESC to cancel
        if key == 'esc':
            self.close()
            return
        
        # Only letters
        if len(key) == 1 and key.isalpha():
            self.typed_keys += key
            print(f"Typed: {self.typed_keys}")
            
            # Redraw to show typed keys
            if self.hwnd:
                win32gui.InvalidateRect(self.hwnd, None, True)
            
            # Check for match
            if self.typed_keys in self.buttons:
                btn = self.buttons[self.typed_keys]
                x, y = btn['x'], btn['y']
                
                print(f"Match! Clicking ({x}, {y})")
                
                # Close overlay first
                self.close()
                
                # Small delay
                time.sleep(0.05)
                
                # Click
                pyautogui.click(x, y)
                
            elif len(self.typed_keys) >= 2:
                # No match, reset
                print("No match, resetting")
                self.typed_keys = ""
                if self.hwnd:
                    win32gui.InvalidateRect(self.hwnd, None, True)
    
    def close(self):
        """Close the overlay"""
        self.is_active = False
        if self.hwnd:
            win32gui.DestroyWindow(self.hwnd)
            self.hwnd = None
        keyboard.unhook_all()


class KeyHintsApp:
    """Main application"""
    
    def __init__(self):
        self.overlay = None
        self.is_scanning = False
    
    def scan_window(self):
        """Scan active window for UI elements"""
        coordinates = []
        seen_coords = set()
        
        target_types = {
            'ButtonControl', 'MenuItemControl', 'TabItemControl',
            'ListItemControl', 'TreeItemControl', 'HyperlinkControl',
            'CheckBoxControl', 'RadioButtonControl', 'ComboBoxControl',
        }
        
        try:
            # Initialize COM
            initializer = automation.UIAutomationInitializerInThread()
            
            desktop = automation.GetRootControl()
            active_window = pyautogui.getActiveWindowTitle()
            
            if not active_window:
                print("No active window")
                del initializer
                return []
            
            print(f"Scanning: {active_window}")
            
            # Find and scan window
            for window in desktop.GetChildren():
                if window.Name == active_window:
                    print(f"Found: {window.ClassName}")
                    
                    def scan_control(control, level=0):
                        if level > 10:  # Limit depth
                            return
                        
                        try:
                            rect = control.BoundingRectangle
                            if rect and rect.width() > 0 and rect.height() > 0:
                                x = rect.left + rect.width() // 2
                                y = rect.top + rect.height() // 2
                                
                                coord_key = (x // 5, y // 5)
                                
                                if coord_key not in seen_coords:
                                    if control.ControlTypeName in target_types:
                                        coordinates.append((x, y))
                                        seen_coords.add(coord_key)
                                        print(f"  {'  '*level}{control.ControlTypeName} @ ({x},{y})")
                            
                            for child in control.GetChildren():
                                scan_control(child, level + 1)
                        except:
                            pass
                    
                    scan_control(window)
                    break
            
            del initializer
            print(f"Found {len(coordinates)} elements")
            return coordinates
            
        except Exception as e:
            print(f"Scan error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def activate(self):
        """Activate hints on current window"""
        if self.is_scanning:
            print("Already scanning...")
            return
        
        self.is_scanning = True
        print("\n" + "="*60)
        print("KeyHints Activated!")
        print("="*60)
        
        # Scan in background thread
        def scan_thread():
            coords = self.scan_window()
            
            if not coords:
                print("No elements found!")
                self.is_scanning = False
                return
            
            # Create overlay with global keyboard hook
            self.overlay = FastOverlay(coords)
            
            # Hook keyboard globally BEFORE showing overlay
            keyboard.on_press(self.overlay.on_key_press)
            
            # Show overlay
            self.overlay.create_overlay()
            
            self.is_scanning = False
            print("KeyHints deactivated")
        
        threading.Thread(target=scan_thread, daemon=True).start()
    
    def run_with_hotkey(self, hotkey='ctrl+shift+k'):
        """Run with global hotkey"""
        print(f"KeyHints Everywhere v2 - Starting...")
        print(f"Press {hotkey.upper()} to activate")
        print(f"Press CTRL+C to exit\n")
        
        keyboard.add_hotkey(hotkey, self.activate)
        
        try:
            keyboard.wait('ctrl+c')
        except KeyboardInterrupt:
            print("\nExiting...")
    
    def test_mode(self):
        """Test on current window"""
        print("Test mode - activating now...")
        coords = self.scan_window()
        
        if not coords:
            print("No elements found!")
            return
        
        # Create and show overlay
        self.overlay = FastOverlay(coords)
        keyboard.on_press(self.overlay.on_key_press)
        self.overlay.create_overlay()


def main():
    app = KeyHintsApp()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        app.test_mode()
    else:
        app.run_with_hotkey('ctrl+shift+k')


if __name__ == '__main__':
    main()
