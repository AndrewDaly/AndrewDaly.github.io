# Lightning Explorer - Technical Notes

## Insights from the Hotkey Project

Based on analysis of `C:\Dev\hotkey`, this document outlines relevant patterns, libraries, and architectural decisions to inform Lightning Explorer development.

---

## Python-C++ Hybrid Architecture

### Why Hybrid Approach?
The hotkey project demonstrates successful Python-C++ integration for performance-critical operations:

**Python strengths (use for):**
- GUI/UI layer
- Business logic
- Event handling
- Configuration management
- High-level orchestration

**C++ strengths (use for):**
- Low-level keyboard hooks (Windows API)
- Real-time input processing
- Named pipe communication
- Performance-critical loops
- System-level operations

### Communication Pattern: Named Pipes
From `c_server.cpp`:
```cpp
// C++ creates named pipe server
pipe = CreateNamedPipe("\\\\.\\pipe\\HotkeyPipe", ...);

// Python client connects to pipe
// Fast, efficient IPC between Python and C++
```

**Application to Lightning Explorer:**
- C++ handles file system monitoring and indexing
- Python handles UI and user interaction
- Named pipes for low-latency communication
- Async Python workers reading from pipe

---

## Keyboard Navigation Patterns

### Modal Keyboard System (from static_hands_v3.py)

The hotkey project uses 'j' as a modifier key (like Ctrl):
- `j + a` → Select all
- `j + i` → Up
- `j + k` → Down
- `j + f` → Right
- `j + /` → Type literal 'j'

**Lightning Explorer can adopt similar pattern:**
- **Normal Mode**: Navigate file list (vim-style: h/j/k/l)
- **Search Mode**: Type to filter/search
- **Command Mode**: Execute operations
- **Visual Mode**: Select multiple files

### Key Libraries Used

From `requirements.txt`:
```python
keyboard==0.13.5          # Low-level keyboard hooks
PyAutoGUI==0.9.54         # GUI automation
uiautomation==2.0.20      # Windows UI automation
pyperclip==1.8.2          # Clipboard operations
pillow==10.2.0            # Image handling
```

**Recommendations for Lightning Explorer:**
- `keyboard` - Global hotkey registration
- `pyperclip` - Copy/paste file paths
- Skip PyAutoGUI (we're building our own UI)
- Consider `pywin32` for deeper Windows integration

---

## UI Overlay Technique (from py_vimium.py)

### Vimium-Style Keyboard Navigation
The `py_vimium.py` implements a clever overlay system:

1. **Detect clickable regions** using OpenCV (MSER algorithm)
2. **Create transparent overlay** with tkinter
3. **Label each region** with 2-letter codes (aa, ab, ac...)
4. **Type to click** - user types label to click that region

```python
# Key insight: fullscreen transparent overlay
root.attributes("-fullscreen", True)
root.attributes("-alpha", 0.3)
root.attributes("-topmost", True)
```

**Application to Lightning Explorer:**
- Quick file selection by typing labels
- Preview overlay without opening files
- Context menu navigation via keyboard
- Multi-pane navigation labels

---

## Performance Considerations

### C++ for Low-Level Operations

From `c_server.cpp` (keyboard hook):
- Uses Windows `SetWindowsHookEx` API
- Tracks key state with boolean flags
- Zero-allocation hot path
- Named pipe for IPC (not slow sockets)

### File System Operations in C++

**Recommended C++ components for Lightning Explorer:**

1. **File System Watcher** (C++)
   ```cpp
   // Use Windows ReadDirectoryChangesW API
   // Real-time monitoring without polling
   // Send changes to Python via named pipe
   ```

2. **Directory Indexer** (C++)
   ```cpp
   // Fast recursive directory traversal
   // Build search index in background
   // Memory-mapped file for index storage
   ```

3. **Search Engine** (C++)
   ```cpp
   // Fuzzy string matching
   // Parallel search across indexed files
   // Return results to Python via pipe
   ```

---

## Recommended Architecture

### Component Breakdown

```
┌─────────────────────────────────────────┐
│         Python GUI Layer                │
│  (tkinter/PyQt - Event Loop)            │
└───────────┬─────────────────────────────┘
            │ Named Pipe IPC
┌───────────┴─────────────────────────────┐
│         C++ Performance Layer           │
│  ┌─────────────────────────────────┐   │
│  │  File System Monitor            │   │
│  │  (ReadDirectoryChangesW)        │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │  Directory Indexer              │   │
│  │  (Recursive Traversal)          │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │  Search Engine                  │   │
│  │  (Fuzzy Matching)               │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### Python-Only Prototype First

**Start with pure Python (Py311):**
```python
import os
import pathlib
from tkinter import *
from watchdog import observers  # File monitoring

# Measure performance bottlenecks
# Only port slow parts to C++
```

**Benchmark before optimizing:**
- Profile with `cProfile`
- Identify bottlenecks (likely: directory scan, search)
- Port only what's necessary to C++

---

## GUI Framework Options

### tkinter (used in hotkey project)
**Pros:**
- Built-in, no dependencies
- Lightweight and fast startup
- Good keyboard event handling
- Example: `navigation.py` shows clean key binding

**Cons:**
- Basic styling
- No native Windows 11 look

### PyQt5/PyQt6
**Pros:**
- Professional appearance
- Rich widget set
- Excellent keyboard handling
- Native file dialogs

**Cons:**
- Larger dependency
- Slower startup

### Recommendation: Start with tkinter
- Hotkey project proves tkinter is sufficient
- Fast development iteration
- Easy keyboard binding
- Can switch to PyQt later if needed

---

## Keyboard Event Handling

### Global Hotkeys (C++)
From `c_server.cpp`:
```cpp
HHOOK hook = SetWindowsHookEx(WH_KEYBOARD_LL, KeyboardProc, NULL, 0);
```

**Application:**
- Win+E replacement to launch Lightning Explorer
- Global hotkey to activate search from anywhere
- System-wide keyboard intercept if needed

### Application-Level Hotkeys (Python)
From `navigation.py`:
```python
self.label.bind("<w>", self.on_wasd)
self.label.bind("<a>", self.on_wasd)
# Clean, simple event binding
```

**Application:**
- Use tkinter `.bind()` for all in-app shortcuts
- Keep bindings in central configuration
- Allow user customization

---

## File Operations Strategy

### Python Standard Library (Start Here)
```python
import os
import pathlib
import shutil
from pathlib import Path

# Fast enough for most operations
Path.iterdir()    # List directory
shutil.copy2()    # Copy with metadata
os.rename()       # Move/rename
```

### When to Use C++
Only if benchmarks show slowness:
1. Recursive directory scan of 100K+ files
2. Real-time file system monitoring
3. Search indexing of large directory trees
4. Calculating directory sizes recursively

### Hybrid Example
```python
# Python UI
def scan_directory(path):
    if use_cpp:
        # Call C++ via named pipe
        result = cpp_scanner.scan(path)
    else:
        # Pure Python fallback
        result = list(Path(path).rglob('*'))
    return result
```

---

## Named Pipe IPC Pattern

### C++ Server (from c_server.cpp)
```cpp
pipe = CreateNamedPipe("\\\\.\\pipe\\LEPipe", ...);
ConnectNamedPipe(pipe, NULL);

// Send message to Python
WriteFile(pipe, message.c_str(), ...);
```

### Python Client
```python
import win32pipe
import win32file

pipe = win32file.CreateFile(
    r'\\.\pipe\LEPipe',
    win32file.GENERIC_READ | win32file.GENERIC_WRITE,
    0, None,
    win32file.OPEN_EXISTING,
    0, None
)

# Read from C++
result = win32file.ReadFile(pipe, 4096)
```

---

## Development Workflow

### Phase 1: Pure Python Prototype (Week 1-2)
- Implement basic file listing with pathlib
- Build keyboard navigation with tkinter
- Simple fuzzy search with Python
- Benchmark all operations

### Phase 2: Identify Bottlenecks (Week 3)
- Profile with cProfile
- Test with large directories (10K+ files)
- Measure startup time
- Measure search latency

### Phase 3: C++ Optimization (Week 4+)
- Port identified bottlenecks to C++
- Implement named pipe communication
- Keep Python for UI/logic
- Benchmark improvements

---

## Testing Strategy

### Performance Targets
Based on hotkey project learnings:
- Startup time: < 500ms (Python is fast enough)
- Keyboard response: < 16ms (60 FPS feel)
- Directory scan: < 1s for 10K files
- Search: < 100ms for fuzzy match

### Test Directories
```
Small:  100 files
Medium: 1,000 files
Large:  10,000 files
Huge:   100,000 files
```

### Fallback Strategy
If Python is too slow:
1. Try PyPy (JIT compilation)
2. Use multiprocessing
3. Only then port to C++

---

## Security Considerations

### Workplace Deployment
- No elevated privileges required
- Portable installation (user directory)
- No system hooks unless explicitly enabled
- Clear permissions for file operations

### Code Signing
- Sign .exe files for Windows SmartScreen
- Use PyInstaller for distribution
- Include clear uninstall process

---

## C++ Compiler Setup

### Available Compilers

**Your System:**
- ✅ **Visual Studio** (MSVC) - Found at `C:\Program Files\Microsoft Visual Studio`
- 📁 **GCC Source Code** - Available at `C:\Dev\gcc` (needs compilation)

### Building C++ Components with MSVC

**Option 1: Visual Studio (Recommended for Windows)**

MSVC is ideal for Windows-native development and integrates well with Windows APIs.

```powershell
# Open Developer Command Prompt for VS
# Navigate to lightning_explorer directory

# Compile C++ component
cl /EHsc /O2 file_scanner.cpp /link /OUT:file_scanner.exe

# With Windows API libraries
cl /EHsc /O2 fs_monitor.cpp /link kernel32.lib user32.lib /OUT:fs_monitor.exe
```

**Build Configuration for Named Pipe Communication:**
```cpp
// fs_monitor.cpp
#include <windows.h>
#include <iostream>

// Compile with: cl /EHsc /O2 fs_monitor.cpp /link kernel32.lib
int main() {
    HANDLE pipe = CreateNamedPipe(
        "\\\\.\\pipe\\LEPipe",
        PIPE_ACCESS_DUPLEX,
        PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT,
        1, 1024, 1024, 0, NULL
    );
    // ... implementation
}
```

### Building with GCC (If Needed)

**Option 2: Compile GCC from Source (C:\Dev\gcc)**

If you want to use GCC instead of MSVC:

```powershell
# Navigate to GCC source directory
cd C:\Dev\gcc

# Configure and build (this takes several hours!)
./configure --prefix=/usr/local --enable-languages=c,c++
make -j8
make install
```

**Option 3: Install MinGW-w64 (Faster Alternative)**

Instead of compiling GCC from source, install pre-built MinGW:

```powershell
# Using Chocolatey
choco install mingw

# Or download from: https://www.mingw-w64.org/
# Add to PATH: C:\MinGW\bin
```

### Recommended Build System: CMake

For cross-compiler compatibility, use CMake:

**CMakeLists.txt:**
```cmake
cmake_minimum_required(VERSION 3.15)
project(LightningExplorer)

set(CMAKE_CXX_STANDARD 17)

# File system scanner
add_executable(fs_scanner
    src/fs_scanner.cpp
    src/named_pipe.cpp
)

# Link Windows libraries
target_link_libraries(fs_scanner
    kernel32
    user32
)

# Python bindings (optional, using pybind11)
find_package(pybind11 CONFIG)
if(pybind11_FOUND)
    pybind11_add_module(le_native
        src/python_bindings.cpp
        src/fs_scanner.cpp
    )
endif()
```

**Build commands:**
```powershell
# Create build directory
mkdir build
cd build

# Configure with MSVC
cmake .. -G "Visual Studio 17 2022"

# Or configure with MinGW
cmake .. -G "MinGW Makefiles"

# Build
cmake --build . --config Release
```

### Python-C++ Bindings with pybind11

**Install pybind11:**
```powershell
pip install pybind11
```

**Example binding (fs_scanner_binding.cpp):**
```cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <string>

namespace py = pybind11;

std::vector<std::string> scan_directory(const std::string& path) {
    // Fast C++ directory scanning
    std::vector<std::string> files;
    // ... implementation using Windows API
    return files;
}

PYBIND11_MODULE(le_native, m) {
    m.doc() = "Lightning Explorer native accelerated functions";
    m.def("scan_directory", &scan_directory, 
          "Scan directory and return file list",
          py::arg("path"));
}
```

**Python usage:**
```python
import le_native

# Use C++ accelerated function
files = le_native.scan_directory("C:\\Users")
```

### Compilation Quick Reference

| Compiler | Command | Use Case |
|----------|---------|----------|
| **MSVC (cl.exe)** | `cl /EHsc /O2 file.cpp` | Windows-native, best Windows API support |
| **GCC (g++)** | `g++ -O2 -std=c++17 file.cpp` | Cross-platform, good optimization |
| **CMake** | `cmake --build . --config Release` | Multi-compiler support |

### Performance Compiler Flags

**MSVC Optimization:**
```powershell
cl /O2 /GL /arch:AVX2 file.cpp /link /LTCG
# /O2: Maximum optimization
# /GL: Whole program optimization
# /arch:AVX2: Use modern CPU instructions
# /LTCG: Link-time code generation
```

**GCC Optimization:**
```bash
g++ -O3 -march=native -flto file.cpp
# -O3: Aggressive optimization
# -march=native: Optimize for local CPU
# -flto: Link-time optimization
```

### Development Workflow with C++

1. **Start with Python-only implementation**
2. **Profile and identify bottlenecks**
3. **Create C++ module for slow operations**
4. **Build with MSVC (fastest on Windows)**
5. **Use named pipes or pybind11 for Python integration**

### Example: File Scanner Performance Module

**Directory structure:**
```
lightning_explorer/
├── src/
│   ├── main.py              # Python UI
│   ├── cpp/
│   │   ├── fs_scanner.cpp   # C++ file scanner
│   │   ├── fs_scanner.h
│   │   └── CMakeLists.txt
│   └── native_bindings.py   # Python wrapper
├── build/                   # Compiled binaries
│   └── Release/
│       └── fs_scanner.exe
└── requirements.txt
```

**Build script (build.ps1):**
```powershell
# Build C++ components
cd src/cpp
mkdir -Force build
cd build

cmake .. -G "Visual Studio 17 2022"
cmake --build . --config Release

# Copy to project root
cp Release/*.exe ../../../
```

---

## Next Steps

1. **Create pure Python MVP** (this week)
   - Basic file listing
   - Keyboard navigation
   - Simple search
   - **No C++ needed yet!**

2. **Benchmark and profile** (next week)
   - Identify slow operations
   - Compare to Windows Explorer
   - Measure with real-world directories

3. **Iterative C++ optimization** (if needed)
   - Use MSVC for Windows-native performance
   - Build with CMake for flexibility
   - Maintain Python-first architecture
   - Add C++ only where benchmarks prove necessary

---

## Conclusion

The hotkey project demonstrates:
- ✅ Python is sufficient for UI and logic
- ✅ C++ needed only for low-level OS integration
- ✅ Named pipes are fast and reliable for IPC
- ✅ tkinter is lightweight and capable
- ✅ Hybrid approach allows iterative optimization

**Start with Python, optimize with C++ only where necessary.**
