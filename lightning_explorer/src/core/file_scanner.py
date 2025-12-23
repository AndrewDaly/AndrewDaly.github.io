"""
File scanner module for Lightning Explorer
Fast directory scanning and file listing
"""
import os
from pathlib import Path
from typing import List, Optional
import time


class FileEntry:
    """Represents a file or directory entry"""
    
    def __init__(self, path: Path):
        self.path = path
        self.name = path.name
        self.is_dir = path.is_dir()
        self.is_file = path.is_file()
        
        try:
            self.size = path.stat().st_size if self.is_file else 0
            self.modified = path.stat().st_mtime
        except (OSError, PermissionError):
            self.size = 0
            self.modified = 0
    
    def __repr__(self):
        return f"FileEntry({self.name}, dir={self.is_dir})"
    
    @property
    def size_str(self):
        """Human-readable file size"""
        if self.is_dir:
            return "<DIR>"
        
        size = self.size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


class FileScanner:
    """Fast file system scanner"""
    
    def __init__(self):
        self.current_path = Path.cwd()
        self.files: List[FileEntry] = []
    
    def scan(self, path: Optional[Path] = None) -> List[FileEntry]:
        """
        Scan directory and return list of files
        
        Args:
            path: Directory to scan (uses current_path if None)
        
        Returns:
            List of FileEntry objects
        """
        if path:
            self.current_path = Path(path)
        
        start_time = time.time()
        files = []
        
        try:
            # Get all entries
            entries = list(self.current_path.iterdir())
            
            # Create FileEntry objects
            for entry in entries:
                try:
                    files.append(FileEntry(entry))
                except (OSError, PermissionError):
                    # Skip files we can't access
                    continue
            
            # Sort: directories first, then alphabetically
            files.sort(key=lambda x: (not x.is_dir, x.name.lower()))
            
        except PermissionError:
            # Can't access directory
            files = []
        
        self.files = files
        scan_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Performance target: < 50ms for 10,000 files
        if len(files) > 1000 and scan_time > 50:
            print(f"⚠️ Scan time: {scan_time:.1f}ms for {len(files)} files (consider C++ optimization)")
        
        return files
    
    def navigate_up(self) -> bool:
        """
        Navigate to parent directory
        
        Returns:
            True if successful, False if already at root
        """
        parent = self.current_path.parent
        if parent != self.current_path:
            self.current_path = parent
            return True
        return False
    
    def navigate_to(self, entry: FileEntry) -> bool:
        """
        Navigate into a directory
        
        Args:
            entry: FileEntry to navigate to
        
        Returns:
            True if successful, False if not a directory
        """
        if entry.is_dir:
            self.current_path = entry.path
            return True
        return False
    
    def search(self, query: str) -> List[FileEntry]:
        """
        Simple fuzzy search through current files
        
        Args:
            query: Search string
        
        Returns:
            Filtered list of FileEntry objects
        """
        if not query:
            return self.files
        
        query_lower = query.lower()
        results = []
        
        for file in self.files:
            # Simple substring matching (can be enhanced with fuzzy matching later)
            if query_lower in file.name.lower():
                results.append(file)
        
        return results
