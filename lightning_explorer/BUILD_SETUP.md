# Lightning Explorer - Build Setup Guide

## Quick Start

### System Requirements
- ✅ Windows 10/11
- ✅ Python 3.11+
- ✅ Visual Studio 2019+ (for C++ components, optional)
- ✅ 4GB RAM minimum
- ✅ 100MB disk space

## Python Environment Setup

### 1. Create Virtual Environment
```powershell
# Navigate to project directory
cd "C:\Dev\cursor_ai\AndrewDaly.github.io\lightning_explorer"

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Install Python Dependencies
```powershell
# Install required packages
pip install --upgrade pip

# Core dependencies
pip install keyboard pyperclip watchdog

# Optional: If building GUI with PyQt
pip install PyQt6

# Optional: If using pybind11 for C++ bindings
pip install pybind11
```

### 3. Create requirements.txt
```powershell
pip freeze > requirements.txt
```

## Project Structure

```
lightning_explorer/
│
├── src/
│   ├── main.py                 # Entry point
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py      # Main UI
│   │   └── file_list.py        # File list widget
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── file_scanner.py     # Python file scanner
│   │   ├── search.py           # Search logic
│   │   └── keyboard_handler.py # Keyboard shortcuts
│   │
│   └── cpp/                    # C++ performance modules (optional)
│       ├── CMakeLists.txt
│       ├── fs_scanner.cpp
│       └── fs_scanner.h
│
├── build/                      # C++ build output (gitignored)
├── tests/                      # Unit tests
├── venv/                       # Virtual environment (gitignored)
│
├── README.md                   # Project overview
├── TECHNICAL_NOTES.md          # Architecture docs
├── BUILD_SETUP.md              # This file
├── requirements.txt            # Python dependencies
└── .gitignore
```

## Phase 1: Pure Python MVP (Start Here!)

### Create Basic File Scanner

**src/main.py:**
```python
#!/usr/bin/env python3
"""
Lightning Explorer - Fast keyboard-driven file explorer
"""
import sys
from pathlib import Path

def main():
    print("Lightning Explorer v0.1")
    print("=" * 50)
    
    # Start in current directory
    current_path = Path.cwd()
    print(f"Scanning: {current_path}")
    
    # List files
    files = sorted(current_path.iterdir())
    
    for i, file in enumerate(files[:20], 1):  # Show first 20
        icon = "📁" if file.is_dir() else "📄"
        print(f"{i:2d}. {icon} {file.name}")
    
    print(f"\nTotal: {len(files)} items")

if __name__ == "__main__":
    main()
```

### Run Your First Build
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run the application
python src/main.py
```

## Phase 2: C++ Optimization (Only If Needed)

### When to Add C++
Only proceed with C++ if:
- Python file scanning takes > 1 second for 10,000 files
- Search is noticeably slow
- Benchmarks show clear bottlenecks

### Setup MSVC Build Environment

**1. Open Visual Studio Developer Command Prompt**
```
Start Menu → Visual Studio 2022 → Developer Command Prompt
```

**2. Navigate to project**
```cmd
cd C:\Dev\cursor_ai\AndrewDaly.github.io\lightning_explorer
```

**3. Create CMakeLists.txt**

**src/cpp/CMakeLists.txt:**
```cmake
cmake_minimum_required(VERSION 3.15)
project(LightningExplorerNative)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Python
find_package(Python COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

# Native Python module
pybind11_add_module(le_native
    fs_scanner.cpp
    search_engine.cpp
    bindings.cpp
)

# Windows-specific libraries
target_link_libraries(le_native PRIVATE
    kernel32
    user32
)

# Optimization flags
if(MSVC)
    target_compile_options(le_native PRIVATE /O2 /GL)
    target_link_options(le_native PRIVATE /LTCG)
endif()
```

**4. Build C++ Module**
```powershell
# In Developer Command Prompt
cd src/cpp
mkdir build
cd build

# Configure
cmake .. -G "Visual Studio 17 2022" -A x64

# Build
cmake --build . --config Release

# Module will be at: Release/le_native.pyd
# Copy to src/ directory
cp Release/le_native*.pyd ../../
```

### Using C++ Module in Python

**src/core/file_scanner.py:**
```python
import sys
from pathlib import Path

# Try to use C++ acceleration
try:
    import le_native
    USE_NATIVE = True
    print("✓ Using C++ accelerated scanning")
except ImportError:
    USE_NATIVE = False
    print("✓ Using pure Python scanning")

def scan_directory(path):
    """Scan directory, use C++ if available"""
    if USE_NATIVE:
        return le_native.scan_directory(str(path))
    else:
        # Pure Python fallback
        return [str(f) for f in Path(path).iterdir()]
```

## Testing

### Run Tests
```powershell
# Install pytest
pip install pytest

# Run tests
pytest tests/
```

### Performance Benchmarks
```powershell
python tests/benchmark_scan.py
```

## Common Issues & Solutions

### Issue: Can't activate virtual environment
**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: Python not found
**Solution:**
```powershell
# Add Python to PATH or specify full path
C:\Users\YourName\AppData\Local\Programs\Python\Python311\python.exe -m venv venv
```

### Issue: CMake not found
**Solution:**
Install CMake:
```powershell
# Using chocolatey
choco install cmake

# Or download from: https://cmake.org/download/
```

### Issue: pybind11 not found
**Solution:**
```powershell
pip install pybind11[global]
```

## Next Steps

1. ✅ Setup Python environment
2. ✅ Run pure Python MVP
3. ⏳ Implement keyboard navigation
4. ⏳ Add search functionality
5. ⏳ Benchmark performance
6. ⏳ Add C++ optimization (if needed)

## Additional Resources

- [Python 3.11 Documentation](https://docs.python.org/3.11/)
- [CMake Tutorial](https://cmake.org/cmake/help/latest/guide/tutorial/)
- [pybind11 Documentation](https://pybind11.readthedocs.io/)
- [Hotkey Project Reference](C:\Dev\hotkey)

## Support

For issues or questions, refer to:
- `TECHNICAL_NOTES.md` - Architecture details
- `README.md` - Project overview
- Hotkey project at `C:\Dev\hotkey` - Working examples
