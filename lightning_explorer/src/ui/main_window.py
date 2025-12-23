"""
Main window for Lightning Explorer
Vimium-style hint-based file explorer
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
import subprocess
import sys
from pathlib import Path
import itertools
import string

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.file_scanner import FileScanner, FileEntry


# Generate 2-letter hint labels (aa, ab, ac, ... zz)
def generate_hints(count):
    """Generate hint labels like: aa, ab, ac, ba, bb, ..."""
    letters = string.ascii_lowercase
    hints = []
    for combo in itertools.product(letters, repeat=2):
        hints.append(''.join(combo))
        if len(hints) >= count:
            break
    return hints


class LightningExplorer(tk.Tk):
    """Main application window with Vimium-style navigation"""
    
    def __init__(self):
        super().__init__()
        
        # Application state
        self.scanner = FileScanner()
        self.current_files = []
        self.filtered_files = []
        self.file_hints = {}  # Maps hint labels to files
        self.search_mode = False
        self.search_query = ""
        self.hint_buffer = ""  # Typed hint characters
        
        # Setup UI
        self.title("Lightning Explorer")
        self.geometry("1000x700")
        self.configure(bg='#121212')
        
        # Create UI components
        self.create_widgets()
        
        # Bind keyboard shortcuts
        self.bind_keys()
        
        # Initial scan
        self.refresh_files()
        
        # Focus on file list
        self.file_listbox.focus_set()
    
    def create_widgets(self):
        """Create and layout UI widgets"""
        
        # Top bar - Path display
        self.path_frame = tk.Frame(self, bg='#1e1e1e', height=40)
        self.path_frame.pack(fill=tk.X, padx=5, pady=5)
        self.path_frame.pack_propagate(False)
        
        self.path_label = tk.Label(
            self.path_frame,
            text="",
            bg='#1e1e1e',
            fg='#00b4d8',
            font=('Consolas', 11, 'bold'),
            anchor='w',
            padx=10
        )
        self.path_label.pack(fill=tk.BOTH, expand=True)
        
        # Search bar
        self.search_frame = tk.Frame(self, bg='#1e1e1e', height=35)
        self.search_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        self.search_frame.pack_propagate(False)
        
        self.search_label = tk.Label(
            self.search_frame,
            text="Search:",
            bg='#1e1e1e',
            fg='#b3b3b3',
            font=('Segoe UI', 10),
            padx=10
        )
        self.search_label.pack(side=tk.LEFT)
        
        self.search_entry = tk.Entry(
            self.search_frame,
            bg='#2a2a2a',
            fg='#ffffff',
            insertbackground='#00b4d8',
            font=('Consolas', 10),
            relief=tk.FLAT,
            bd=0
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=5)
        self.search_entry.bind('<KeyRelease>', self.on_search_change)
        self.search_entry.bind('<Escape>', self.exit_search_mode)
        self.search_entry.bind('<Return>', self.exit_search_mode)
        
        # File list frame with scrollbar
        self.list_frame = tk.Frame(self, bg='#121212')
        self.list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # Scrollbar
        self.scrollbar = tk.Scrollbar(self.list_frame, bg='#1e1e1e', troughcolor='#121212')
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # File listbox
        self.file_listbox = tk.Listbox(
            self.list_frame,
            bg='#1e1e1e',
            fg='#ffffff',
            selectmode=tk.SINGLE,
            font=('Consolas', 10),
            relief=tk.FLAT,
            bd=0,
            highlightthickness=1,
            highlightbackground='#333333',
            selectbackground='#00b4d8',
            selectforeground='#000000',
            yscrollcommand=self.scrollbar.set
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.file_listbox.yview)
        
        # Status bar
        self.status_frame = tk.Frame(self, bg='#1e1e1e', height=30)
        self.status_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        self.status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            self.status_frame,
            text="",
            bg='#1e1e1e',
            fg='#b3b3b3',
            font=('Segoe UI', 9),
            anchor='w',
            padx=10
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Hint buffer display
        self.hint_label = tk.Label(
            self.status_frame,
            text="",
            bg='#1e1e1e',
            fg='#00ff00',
            font=('Consolas', 10, 'bold'),
            anchor='e',
            padx=10
        )
        self.hint_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.help_label = tk.Label(
            self.status_frame,
            text="? - Help | / - Search | Backspace - Up",
            bg='#1e1e1e',
            fg='#00b4d8',
            font=('Segoe UI', 9),
            anchor='e',
            padx=10
        )
        self.help_label.pack(side=tk.RIGHT)
    
    def bind_keys(self):
        """Bind keyboard shortcuts"""
        
        # Bind all letter keys for hint navigation
        for letter in string.ascii_lowercase:
            self.file_listbox.bind(f'<{letter}>', self.on_hint_key)
        
        # Navigation
        self.file_listbox.bind('<BackSpace>', lambda e: self.navigate_up())
        self.file_listbox.bind('<Escape>', self.clear_hint_buffer)
        
        # Search
        self.file_listbox.bind('<slash>', self.enter_search_mode)
        
        # Refresh
        self.file_listbox.bind('<F5>', lambda e: self.refresh_files())
        
        # Help
        self.file_listbox.bind('<?>', self.show_help)
    
    def refresh_files(self):
        """Scan and display current directory"""
        self.current_files = self.scanner.scan()
        self.filtered_files = self.current_files
        self.selected_index = 0
        self.update_display()
    
    def update_display(self):
        """Update the file list display with hint labels"""
        # Update path
        self.path_label.config(text=str(self.scanner.current_path))
        
        # Clear listbox and hint mapping
        self.file_listbox.delete(0, tk.END)
        self.file_hints.clear()
        
        # Generate hint labels for files
        hints = generate_hints(len(self.filtered_files) + 1)  # +1 for ".."
        hint_index = 0
        
        # Add parent directory entry if not at root
        if self.scanner.current_path.parent != self.scanner.current_path:
            hint = hints[hint_index]
            self.file_listbox.insert(tk.END, f"[{hint}] 📁 ..")
            self.file_hints[hint] = None  # None means parent directory
            hint_index += 1
        
        # Add files with hint labels
        for file in self.filtered_files:
            hint = hints[hint_index]
            icon = "📁" if file.is_dir else "📄"
            display_text = f"[{hint}] {icon} {file.name:<45} {file.size_str:>10}"
            self.file_listbox.insert(tk.END, display_text)
            self.file_hints[hint] = file
            hint_index += 1
        
        # Update status
        file_count = len(self.filtered_files)
        dir_count = sum(1 for f in self.filtered_files if f.is_dir)
        file_file_count = file_count - dir_count
        
        status = f"{file_count} items ({dir_count} folders, {file_file_count} files)"
        if self.search_query:
            status += f" | Filtered by: '{self.search_query}'"
        self.status_label.config(text=status)
    
    def on_hint_key(self, event):
        """Handle hint key press"""
        if self.search_mode:
            return  # Let search handle the key
        
        key = event.char.lower()
        self.hint_buffer += key
        
        # Update hint display
        self.hint_label.config(text=f"Hint: {self.hint_buffer}")
        
        # Check for matches
        matching_hints = [h for h in self.file_hints.keys() if h.startswith(self.hint_buffer)]
        
        if len(matching_hints) == 1 and matching_hints[0] == self.hint_buffer:
            # Exact match - activate the file
            self.activate_hint(matching_hints[0])
        elif len(matching_hints) == 0:
            # No matches - reset
            self.clear_hint_buffer()
        
        return "break"
    
    def activate_hint(self, hint):
        """Activate the file/folder with given hint"""
        if hint not in self.file_hints:
            return
        
        file = self.file_hints[hint]
        self.clear_hint_buffer()
        
        if file is None:
            # Parent directory ".."
            self.navigate_up()
        elif file.is_dir:
            # Navigate into directory
            self.scanner.navigate_to(file)
            self.refresh_files()
        else:
            # Open file with default application
            try:
                if sys.platform == 'win32':
                    os.startfile(file.path)
                else:
                    subprocess.call(['xdg-open', str(file.path)])
                    
                # Show feedback
                self.status_label.config(text=f"Opened: {file.name}")
                self.after(2000, lambda: self.update_display())
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file:\n{e}")
    
    def clear_hint_buffer(self, event=None):
        """Clear the hint buffer"""
        self.hint_buffer = ""
        self.hint_label.config(text="")
        return "break"
    
    def navigate_up(self):
        """Navigate to parent directory"""
        if self.scanner.navigate_up():
            self.refresh_files()
        return "break"
    
    def enter_search_mode(self, event=None):
        """Enter search mode"""
        self.search_mode = True
        self.search_entry.focus_set()
        return "break"
    
    def exit_search_mode(self, event=None):
        """Exit search mode"""
        if self.search_mode:
            self.search_mode = False
            self.file_listbox.focus_set()
        return "break"
    
    def on_search_change(self, event=None):
        """Handle search input changes"""
        self.search_query = self.search_entry.get()
        self.filtered_files = self.scanner.search(self.search_query)
        self.clear_hint_buffer()  # Clear hints when search changes
        self.update_display()
    
    
    def show_help(self, event=None):
        """Show help dialog"""
        help_text = """
Lightning Explorer - Vimium-Style Navigation

HINT-BASED NAVIGATION:
  Each file has a 2-letter hint like [aa], [ab], [kl]
  Just type the hint to open/navigate to that file!
  
  Example:
    - See [fj] next to a folder?
    - Type 'f' then 'j' → Opens that folder
    - No arrow keys needed!
  
NAVIGATION:
  Backspace  - Go to parent directory
  Esc        - Clear current hint input
  [aa],[ab]  - Type any hint to activate file/folder
  
SEARCH:
  /          - Enter search mode
  Type text  - Filter files in real-time
  Esc        - Exit search mode
  
OTHER:
  F5         - Refresh current directory
  ?          - Show this help

TIP: Direct access to any file with just 2 keystrokes!
     Much faster than repeated arrow key presses.
        """
        messagebox.showinfo("Lightning Explorer Help", help_text)
        return "break"


def main():
    """Entry point for Lightning Explorer"""
    app = LightningExplorer()
    app.mainloop()


if __name__ == "__main__":
    main()
