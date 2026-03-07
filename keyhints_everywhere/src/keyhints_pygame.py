"""
KeyHints Everywhere - Fast pygame version
Ultra-fast overlay with no focus stealing
"""

import time
import pyautogui
import uiautomation as automation
import keyboard
import threading
import itertools
import sys
import pygame
from pygame import NOFRAME, SRCALPHA, HWSURFACE, DOUBLEBUF


class FastOverlay:
    """Fast pygame-based overlay - no focus needed!"""
    
    def __init__(self, coordinates):
        self.coordinates = coordinates
        self.buttons = {}
        self.typed_keys = ""
        self.running = True
        
        # Generate hints
        letters = "abcdefghiklmnopqrstuvwxyz"
        labels = ["".join(pair) for pair in itertools.product(letters, repeat=2)]
        
        for (x, y), label in zip(coordinates, labels[:len(coordinates)]):
            self.buttons[label] = {'x': x, 'y': y}
        
        print(f"Created {len(self.buttons)} hints")
    
    def create_overlay(self):
        """Create fast pygame overlay"""
        pygame.init()
        
        # Get screen size
        info = pygame.display.Info()
        width, height = info.current_w, info.current_h
        
        print(f"Creating overlay: {width}x{height}")
        
        # Create fullscreen window
        self.screen = pygame.display.set_mode(
            (width, height),
            pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
        )
        pygame.display.set_caption("KeyHints")
        
        # Windows API for window manipulation
        import ctypes
        hwnd = pygame.display.get_wm_info()['window']
        
        print(f"Window handle: {hwnd}")
        
        # Force window to foreground and activate it
        SWP_SHOWWINDOW = 0x0040
        HWND_TOPMOST = -1
        SW_SHOW = 5
        
        # Show and activate window
        ctypes.windll.user32.ShowWindow(hwnd, SW_SHOW)
        ctypes.windll.user32.SetForegroundWindow(hwnd)
        ctypes.windll.user32.SetActiveWindow(hwnd)
        
        # Set to topmost
        ctypes.windll.user32.SetWindowPos(
            hwnd, HWND_TOPMOST,
            0, 0, 0, 0,
            0x0001 | 0x0002 | SWP_SHOWWINDOW  # SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW
        )
        
        # Bring to front
        ctypes.windll.user32.BringWindowToTop(hwnd)
        
        print("Window created, activated, and brought to front")
        
        # Fonts
        font_hint = pygame.font.SysFont('Consolas', 16, bold=True)
        font_status = pygame.font.SysFont('Consolas', 20, bold=True)
        font_typed = pygame.font.SysFont('Consolas', 36, bold=True)
        
        clock = pygame.time.Clock()
        
        # Main loop
        while self.running:
            # Handle pygame events (required to keep window responsive)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.close()
            
            # Clear screen with semi-transparent dark overlay (so you can see through!)
            overlay = pygame.Surface((width, height))
            overlay.set_alpha(128)  # 50% transparent
            overlay.fill((15, 15, 15))  # Very dark gray
            self.screen.blit(overlay, (0, 0))
            
            # Draw hint buttons
            for label, coords in self.buttons.items():
                x, y = coords['x'], coords['y']
                
                # Yellow button with border
                button_rect = pygame.Rect(x-14, y-11, 28, 22)
                pygame.draw.rect(self.screen, (255, 255, 0), button_rect, border_radius=4)
                pygame.draw.rect(self.screen, (0, 0, 0), button_rect, 3, border_radius=4)
                
                # Black text
                text = font_hint.render(label, True, (0, 0, 0))
                text_rect = text.get_rect(center=(x, y))
                self.screen.blit(text, text_rect)
            
            # Status bar at bottom (more opaque so it's readable)
            status_surface = pygame.Surface((width, 100))
            status_surface.set_alpha(220)  # More opaque for readability
            status_surface.fill((25, 25, 25))
            self.screen.blit(status_surface, (0, height-100))
            
            # Status text
            status_text = f"Type hint to click | {len(self.buttons)} hints | ESC to cancel"
            status_surf = font_status.render(status_text, True, (0, 255, 0))
            self.screen.blit(status_surf, (10, height-80))
            
            # Typed keys display
            if self.typed_keys:
                typed_surf = font_typed.render(f"Typed: {self.typed_keys}", True, (255, 255, 0))
                typed_rect = typed_surf.get_rect(center=(width//2, height-40))
                self.screen.blit(typed_surf, typed_rect)
            
            pygame.display.flip()
            clock.tick(60)  # 60 FPS
        
        pygame.quit()
    
    def on_key_press(self, event):
        """Handle global keyboard (doesn't need focus!)"""
        if not self.running:
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
            
            # Check for match
            if self.typed_keys in self.buttons:
                btn = self.buttons[self.typed_keys]
                x, y = btn['x'], btn['y']
                
                print(f"Match! Clicking ({x}, {y})")
                
                # Close overlay
                self.close()
                
                # Small delay
                time.sleep(0.05)
                
                # Click
                pyautogui.click(x, y)
                
            elif len(self.typed_keys) >= 2:
                # No match, reset
                print("No match, resetting")
                self.typed_keys = ""
    
    def close(self):
        """Close overlay"""
        self.running = False
        keyboard.unhook_all()


class KeyHintsApp:
    """Main application"""
    
    def __init__(self):
        self.overlay = None
        self.is_scanning = False
    
    def scan_window(self):
        """Scan active window"""
        coordinates = []
        seen_coords = set()
        
        target_types = {
            'ButtonControl', 'MenuItemControl', 'TabItemControl',
            'ListItemControl', 'TreeItemControl', 'HyperlinkControl',
            'CheckBoxControl', 'RadioButtonControl', 'ComboBoxControl',
        }
        
        try:
            initializer = automation.UIAutomationInitializerInThread()
            
            desktop = automation.GetRootControl()
            active_window = pyautogui.getActiveWindowTitle()
            
            if not active_window:
                print("No active window")
                del initializer
                return []
            
            print(f"Scanning: {active_window}")
            
            for window in desktop.GetChildren():
                if window.Name == active_window:
                    print(f"Found: {window.ClassName}")
                    
                    def scan_control(control, level=0):
                        if level > 10:
                            return
                        
                        try:
                            rect = control.BoundingRectangle
                            if rect and rect.width() > 0 and rect.height() > 0:
                                x = rect.left + rect.width() // 2
                                y = rect.top + rect.height() // 2
                                
                                coord_key = (x // 5, y // 5)
                                
                                if coord_key not in seen_coords and control.ControlTypeName in target_types:
                                    coordinates.append((x, y))
                                    seen_coords.add(coord_key)
                                    print(f"  {'  '*level}{control.ControlTypeName[:20]} @ ({x},{y})")
                            
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
            return []
    
    def activate(self):
        """Activate hints"""
        if self.is_scanning:
            return
        
        self.is_scanning = True
        print("\n" + "="*60)
        print("KeyHints Activated!")
        print("="*60)
        
        def scan_and_show():
            coords = self.scan_window()
            
            if not coords:
                print("No elements found!")
                self.is_scanning = False
                return
            
            # Create overlay
            self.overlay = FastOverlay(coords)
            
            # Hook keyboard GLOBALLY (works without focus!)
            keyboard.on_press(self.overlay.on_key_press)
            
            # Show overlay (blocking)
            self.overlay.create_overlay()
            
            self.is_scanning = False
            print("KeyHints deactivated")
        
        threading.Thread(target=scan_and_show, daemon=True).start()
    
    def run_with_hotkey(self, hotkey='ctrl+shift+k'):
        """Run with hotkey"""
        print(f"KeyHints Everywhere (pygame) - Starting...")
        print(f"Press {hotkey.upper()} to activate")
        print(f"Press CTRL+C to exit\n")
        
        keyboard.add_hotkey(hotkey, self.activate)
        
        try:
            keyboard.wait('ctrl+c')
        except KeyboardInterrupt:
            print("\nExiting...")
    
    def test_mode(self):
        """Test mode"""
        print("Test mode...")
        coords = self.scan_window()
        
        if not coords:
            print("No elements!")
            return
        
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
