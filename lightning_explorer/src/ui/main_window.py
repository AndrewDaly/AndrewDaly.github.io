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
import shutil

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
        
        # Clipboard state for copy/cut/paste
        self.clipboard_file = None
        self.clipboard_operation = None  # 'copy' or 'cut'
        self.right_clicked_file = None  # Track which file was right-clicked
        
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
            font=('Consolas', 14, 'bold'),
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
            font=('Segoe UI', 12),
            padx=10
        )
        self.search_label.pack(side=tk.LEFT)
        
        self.search_entry = tk.Entry(
            self.search_frame,
            bg='#2a2a2a',
            fg='#ffffff',
            insertbackground='#00b4d8',
            font=('Consolas', 12),
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
        
        # File list (using Text widget for colored hints)
        self.file_listbox = tk.Text(
            self.list_frame,
            bg='#1e1e1e',
            fg='#ffffff',
            font=('Consolas', 13),
            relief=tk.FLAT,
            bd=0,
            highlightthickness=1,
            highlightbackground='#333333',
            yscrollcommand=self.scrollbar.set,
            wrap=tk.NONE,
            cursor='arrow',
            state=tk.DISABLED  # Make read-only initially
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.file_listbox.yview)
        
        # Configure tags for colored hints
        self.file_listbox.tag_configure('hint', foreground='#ffff00', background='#3a3a00', font=('Consolas', 13, 'bold'))
        self.file_listbox.tag_configure('folder', foreground='#ffffff')
        self.file_listbox.tag_configure('file', foreground='#b3b3b3')
        
        # Create context menu
        self.create_context_menu()
        
        # Typing buffer display (shows last 4 keystrokes)
        self.typing_frame = tk.Frame(self, bg='#3a3a00', height=60)
        self.typing_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        self.typing_frame.pack_propagate(False)
        
        tk.Label(
            self.typing_frame,
            text="Typing:",
            bg='#3a3a00',
            fg='#ffff00',
            font=('Segoe UI', 10, 'bold'),
            anchor='w',
            padx=5
        ).pack(side=tk.LEFT)
        
        self.typing_display = tk.Label(
            self.typing_frame,
            text="",
            bg='#3a3a00',
            fg='#ffff00',
            font=('Consolas', 32, 'bold'),
            anchor='center',
            padx=20
        )
        self.typing_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Legend/Help bar
        self.legend_frame = tk.Frame(self, bg='#2a2a2a', height=40)
        self.legend_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        self.legend_frame.pack_propagate(False)
        
        self.legend_label = tk.Label(
            self.legend_frame,
            text="  [ab] - Open  |  r[ab] - Actions  |  SHIFT-H - Back  |  SHIFT-D - Page Down  |  SHIFT-U - Page Up  |  / - Search  |  ? - Help  ",
            bg='#2a2a2a',
            fg='#00b4d8',
            font=('Segoe UI', 11, 'bold'),
            anchor='center',
            padx=10
        )
        self.legend_label.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_frame = tk.Frame(self, bg='#1e1e1e', height=35)
        self.status_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        self.status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            self.status_frame,
            text="",
            bg='#1e1e1e',
            fg='#b3b3b3',
            font=('Segoe UI', 11),
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
            font=('Consolas', 12, 'bold'),
            anchor='e',
            padx=10
        )
        self.hint_label.pack(side=tk.RIGHT, padx=(10, 0))
    
    def create_context_menu(self):
        """Create right-click context menu"""
        self.context_menu = tk.Menu(self, tearoff=0, bg='#2a2a2a', fg='#ffffff', 
                                     activebackground='#00b4d8', activeforeground='#000000')
        self.context_menu.add_command(label="Open", command=self.context_open)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Copy", command=self.context_copy)
        self.context_menu.add_command(label="Cut", command=self.context_cut)
        self.context_menu.add_command(label="Paste", command=self.context_paste)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Copy Full Path", command=self.context_copy_path)
        
        # Bind right-click to file list
        self.file_listbox.bind('<Button-3>', self.show_context_menu)
    
    def bind_keys(self):
        """Bind keyboard shortcuts"""
        
        # Bind all letter keys for hint navigation
        for letter in string.ascii_lowercase:
            self.file_listbox.bind(f'<{letter}>', self.on_hint_key)
        
        # Navigation
        self.file_listbox.bind('<BackSpace>', lambda e: self.navigate_up())
        self.file_listbox.bind('<Escape>', self.clear_hint_buffer)
        
        # SHIFT navigation commands
        self.file_listbox.bind('<H>', lambda e: self.navigate_up())  # SHIFT-H
        self.file_listbox.bind('<D>', self.page_down)  # SHIFT-D
        self.file_listbox.bind('<U>', self.page_up)    # SHIFT-U
        
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
        self.file_listbox.config(state=tk.NORMAL)
        self.file_listbox.delete('1.0', tk.END)
        self.file_hints.clear()
        
        # Generate hint labels for files
        hints = generate_hints(len(self.filtered_files) + 1)  # +1 for ".."
        hint_index = 0
        
        # Add parent directory entry if not at root
        if self.scanner.current_path.parent != self.scanner.current_path:
            hint = hints[hint_index]
            # Insert with colored hint
            self.file_listbox.insert(tk.END, f"[{hint}]", 'hint')
            self.file_listbox.insert(tk.END, f" 📁 ..\n", 'folder')
            self.file_hints[hint] = None  # None means parent directory
            hint_index += 1
        
        # Add files with hint labels
        for file in self.filtered_files:
            hint = hints[hint_index]
            icon = "📁" if file.is_dir else "📄"
            tag = 'folder' if file.is_dir else 'file'
            
            # Insert with colored hint
            self.file_listbox.insert(tk.END, f"[{hint}]", 'hint')
            self.file_listbox.insert(tk.END, f" {icon} {file.name:<45} {file.size_str:>10}\n", tag)
            self.file_hints[hint] = file
            hint_index += 1
        
        # Make read-only
        self.file_listbox.config(state=tk.DISABLED)
        
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
        
        # Update hint display (traditional small display)
        self.hint_label.config(text=f"Hint: {self.hint_buffer}")
        
        # Update typing buffer display (shows last 4 chars in big font)
        display_text = self.hint_buffer[-4:] if len(self.hint_buffer) > 4 else self.hint_buffer
        self.typing_display.config(text=display_text)
        
        # Check if this is a context menu mode (starts with 'r')
        if self.hint_buffer.startswith('r') and len(self.hint_buffer) == 3:
            # User typed 'r' + hint (e.g., 'rab') -> open context menu
            hint = self.hint_buffer[1:]  # Extract the hint part (remove 'r')
            if hint in self.file_hints:
                self.right_clicked_file = self.file_hints[hint]
                self.clear_hint_buffer()
                self.show_keyboard_context_menu()
                return "break"
            else:
                # Invalid hint, reset
                self.clear_hint_buffer()
                return "break"
        
        # Check for matches (only if not in 'r' mode)
        if not self.hint_buffer.startswith('r'):
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
        self.typing_display.config(text="")
        return "break"
    
    def navigate_up(self):
        """Navigate to parent directory"""
        if self.scanner.navigate_up():
            self.refresh_files()
        return "break"
    
    def page_down(self, event=None):
        """Scroll down one page"""
        # Scroll down approximately one page
        try:
            # Get visible height in lines
            visible_height = int(self.file_listbox.winfo_height() / self.file_listbox.tk.call('font', 'metrics', self.file_listbox.cget('font'), '-linespace'))
            lines_to_scroll = max(1, visible_height - 2)  # Leave some overlap
            self.file_listbox.yview_scroll(lines_to_scroll, 'units')
        except:
            # Fallback: scroll by fixed amount
            self.file_listbox.yview_scroll(10, 'units')
        
        return "break"
    
    def page_up(self, event=None):
        """Scroll up one page"""
        # Scroll up approximately one page
        try:
            # Get visible height in lines
            visible_height = int(self.file_listbox.winfo_height() / self.file_listbox.tk.call('font', 'metrics', self.file_listbox.cget('font'), '-linespace'))
            lines_to_scroll = max(1, visible_height - 2)  # Leave some overlap
            self.file_listbox.yview_scroll(-lines_to_scroll, 'units')
        except:
            # Fallback: scroll by fixed amount
            self.file_listbox.yview_scroll(-10, 'units')
        
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
  
  Type hint to open:
    - Type 'ab' → Opens/navigates to that file
  
  Type 'r' + hint for actions menu:
    - Type 'rab' → Opens keyboard menu with options:
      [o] Open    [c] Copy    [x] Cut
      [v] Paste   [p] Copy Full Path
  
NAVIGATION:
  SHIFT-H or Backspace - Go to parent directory
  SHIFT-D              - Page down (scroll down)
  SHIFT-U              - Page up (scroll up)
  Esc                  - Clear current hint input
  [aa],[ab]            - Type hint to open file/folder
  r[aa],r[ab]          - Type 'r' + hint for actions
  
SEARCH:
  /          - Enter search mode
  Type text  - Filter files in real-time
  Esc        - Exit search mode
  
OTHER:
  F5         - Refresh current directory
  ?          - Show this help
  Right-click - Mouse context menu (if you prefer)

TIP: Everything is keyboard accessible!
     Type hint → opens file
     Type 'r' then hint → actions menu
     No mouse needed!
        """
        messagebox.showinfo("Lightning Explorer Help", help_text)
        return "break"
    
    def show_context_menu(self, event):
        """Show context menu on right-click"""
        # Get the line number clicked
        line_index = self.file_listbox.index(f"@{event.x},{event.y}")
        line_num = int(float(line_index))
        
        # Map line number to file
        has_parent = self.scanner.current_path.parent != self.scanner.current_path
        file_index = line_num - 1
        if has_parent:
            file_index -= 1
        
        # Set the right-clicked file
        if file_index == -1 and has_parent:
            self.right_clicked_file = None  # Clicked on ".."
        elif 0 <= file_index < len(self.filtered_files):
            self.right_clicked_file = self.filtered_files[file_index]
        else:
            self.right_clicked_file = None
        
        # Update paste menu state
        if self.clipboard_file:
            self.context_menu.entryconfig("Paste", state=tk.NORMAL)
        else:
            self.context_menu.entryconfig("Paste", state=tk.DISABLED)
        
        # Show menu
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def show_keyboard_context_menu(self):
        """Show keyboard-accessible context menu overlay"""
        if not self.right_clicked_file:
            return
        
        # Create overlay window
        overlay = tk.Toplevel(self)
        overlay.title(f"Actions: {self.right_clicked_file.name}")
        overlay.geometry("400x250")
        overlay.configure(bg='#1e1e1e')
        overlay.transient(self)
        overlay.grab_set()
        
        # Center on parent
        overlay.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - overlay.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - overlay.winfo_height()) // 2
        overlay.geometry(f"+{x}+{y}")
        
        # Title
        title_label = tk.Label(
            overlay,
            text=f"File: {self.right_clicked_file.name}",
            bg='#1e1e1e',
            fg='#00b4d8',
            font=('Consolas', 12, 'bold'),
            pady=10
        )
        title_label.pack()
        
        # Options frame
        options_frame = tk.Frame(overlay, bg='#1e1e1e')
        options_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Define options with hints
        options = [
            ('[o] Open', 'o', self.context_open),
            ('[c] Copy', 'c', self.context_copy),
            ('[x] Cut', 'x', self.context_cut),
            ('[p] Copy Full Path', 'p', self.context_copy_path),
        ]
        
        # Add paste if clipboard has content
        if self.clipboard_file:
            options.append(('[v] Paste', 'v', self.context_paste))
        
        # Create option labels
        for text, key, command in options:
            label = tk.Label(
                options_frame,
                text=text,
                bg='#1e1e1e',
                fg='#ffffff',
                font=('Consolas', 14),
                anchor='w',
                pady=5
            )
            label.pack(fill=tk.X)
            
            # Highlight the hint
            label.config(fg='#b3b3b3')
        
        # Instructions
        inst_label = tk.Label(
            overlay,
            text="Type a letter to select, [w] or ESC to cancel",
            bg='#1e1e1e',
            fg='#00b4d8',
            font=('Segoe UI', 10),
            pady=10
        )
        inst_label.pack()
        
        # Key bindings
        def handle_key(event):
            key = event.char.lower()
            
            # Check for cancel key 'w'
            if key == 'w':
                overlay.destroy()
                self.right_clicked_file = None
                return
            
            # Check for action keys
            for text, opt_key, command in options:
                if key == opt_key:
                    overlay.destroy()
                    command()
                    self.right_clicked_file = None
                    return
        
        def handle_escape(event):
            overlay.destroy()
            self.right_clicked_file = None
        
        overlay.bind('<Key>', handle_key)
        overlay.bind('<Escape>', handle_escape)
        overlay.focus_set()
    
    def context_open(self):
        """Open the right-clicked file/folder"""
        if not self.right_clicked_file:
            return
        
        if self.right_clicked_file.is_dir:
            self.scanner.navigate_to(self.right_clicked_file)
            self.refresh_files()
        else:
            try:
                if sys.platform == 'win32':
                    os.startfile(self.right_clicked_file.path)
                else:
                    subprocess.call(['xdg-open', str(self.right_clicked_file.path)])
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file:\n{e}")
    
    def context_copy(self):
        """Copy file to clipboard"""
        if not self.right_clicked_file:
            return
        
        self.clipboard_file = self.right_clicked_file
        self.clipboard_operation = 'copy'
        self.status_label.config(text=f"Copied: {self.right_clicked_file.name}")
        self.after(2000, lambda: self.update_display())
    
    def context_cut(self):
        """Cut file to clipboard"""
        if not self.right_clicked_file:
            return
        
        self.clipboard_file = self.right_clicked_file
        self.clipboard_operation = 'cut'
        self.status_label.config(text=f"Cut: {self.right_clicked_file.name}")
        self.after(2000, lambda: self.update_display())
    
    def context_paste(self):
        """Paste file from clipboard"""
        if not self.clipboard_file:
            return
        
        source_path = self.clipboard_file.path
        dest_dir = self.scanner.current_path
        dest_path = dest_dir / self.clipboard_file.name
        
        try:
            # Check if destination already exists
            if dest_path.exists():
                # Ask for confirmation to overwrite
                response = messagebox.askyesno(
                    "File Exists",
                    f"{dest_path.name} already exists.\nOverwrite?"
                )
                if not response:
                    return
            
            # Perform copy or move
            if self.clipboard_operation == 'copy':
                if source_path.is_dir():
                    shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                else:
                    shutil.copy2(source_path, dest_path)
                self.status_label.config(text=f"Copied: {self.clipboard_file.name}")
            elif self.clipboard_operation == 'cut':
                shutil.move(str(source_path), str(dest_path))
                self.status_label.config(text=f"Moved: {self.clipboard_file.name}")
                self.clipboard_file = None  # Clear clipboard after cut
                self.clipboard_operation = None
            
            # Refresh the display
            self.refresh_files()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not paste file:\n{e}")
    
    def context_copy_path(self):
        """Copy full file path to clipboard"""
        if not self.right_clicked_file:
            return
        
        try:
            # Copy to system clipboard
            self.clipboard_clear()
            self.clipboard_append(str(self.right_clicked_file.path))
            self.status_label.config(text=f"Path copied: {self.right_clicked_file.path}")
            self.after(2000, lambda: self.update_display())
        except Exception as e:
            messagebox.showerror("Error", f"Could not copy path:\n{e}")


def main():
    """Entry point for Lightning Explorer"""
    app = LightningExplorer()
    app.mainloop()


if __name__ == "__main__":
    main()
