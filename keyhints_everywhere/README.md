# KeyHints Everywhere

**Vimium-style keyboard hints for ANY Windows application!**

Add 2-letter hint overlays to any clickable element in any Windows program. No more mouse needed!

## 🎯 What It Does

Press `CTRL+SHIFT+K` and watch as every clickable element gets a yellow hint label like `[aa]`, `[ab]`, `[kl]`.

Type the 2-letter code to instantly click that element!

## ✨ Features

- **Universal**: Works with ANY Windows application (File Explorer, Chrome, Excel, etc.)
- **Fast**: Only 2 keystrokes to click any element
- **Visual**: Clear yellow hint labels show exactly where you can click
- **Smart**: Uses Windows UI Automation to detect all clickable elements
- **Non-intrusive**: Overlay disappears after you click or press ESC

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python src/keyhints.py
```

### Usage

1. **Start the app** - It runs in the background
2. **Press `CTRL+SHIFT+K`** in any window
3. **See hint labels** appear over clickable elements
4. **Type 2-letter hint** to click that element
5. **Press `ESC`** to cancel

## 📋 Example Use Cases

### File Explorer
```
Open any folder: CTRL+SHIFT+K → [ab]
Click any file: CTRL+SHIFT+K → [cd]
```

### Web Browser
```
Click link: CTRL+SHIFT+K → [fg]
Click button: CTRL+SHIFT+K → [hi]
```

### Any Application
```
Click menu item: CTRL+SHIFT+K → [jk]
Click checkbox: CTRL+SHIFT+K → [lm]
```

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `CTRL+SHIFT+K` | Activate hints on current window |
| `[hint]` | Type 2-letter hint to click element |
| `ESC` | Cancel and close overlay |
| `CTRL+C` | Exit the app |

## 🎨 How It Works

1. **Scan**: Uses Windows UI Automation API to detect clickable elements
2. **Generate**: Creates unique 2-letter hints for each element
3. **Overlay**: Shows transparent fullscreen with yellow hint buttons
4. **Click**: Types hint → moves mouse → clicks element
5. **Close**: Overlay disappears automatically

## 🔧 Technical Details

- **Language**: Python 3.11
- **UI**: tkinter (transparent overlay)
- **Automation**: `uiautomation` library (Windows UI Automation)
- **Input**: `keyboard` library (global hotkeys)
- **Mouse**: `pyautogui` (programmatic clicking)

### Architecture

```
KeyHintsApp (main)
├── UIScanner (scans Windows UI tree)
│   └── scan_control() (recursive element detection)
├── KeyHintsOverlay (transparent tkinter window)
│   ├── Hint buttons [aa], [ab], etc.
│   └── Typing buffer display
└── Threading model
    ├── UI scan in background thread
    └── Overlay in main thread (tkinter requirement)
```

## 🐛 Troubleshooting

**Q: Nothing happens when I press CTRL+SHIFT+K**
- Make sure the app is running (you should see "KeyHints Everywhere - Starting...")
- Check that the target window is active and in focus

**Q: No hints appear**
- Some windows may not expose UI elements via UI Automation
- Try a different application (File Explorer works well)
- Check console for errors

**Q: "CoInitialize has not been called" error**
- This should be fixed in the code (we use UIAutomationInitializerInThread)
- Make sure you're using the latest version

**Q: Hints appear in wrong positions**
- Some apps have complex layouts
- Try resizing the window or toggling fullscreen

## 🎯 Supported Applications

**Works Great:**
- ✅ Windows File Explorer
- ✅ Google Chrome / Edge
- ✅ Microsoft Office (Word, Excel, PowerPoint)
- ✅ Visual Studio Code
- ✅ Most native Windows apps

**May Have Issues:**
- ⚠️ Some legacy Win32 apps
- ⚠️ Games (usually block UI Automation)
- ⚠️ Admin-protected windows (run as admin)

## 🔮 Future Enhancements

- [ ] Customizable hotkey
- [ ] Filter by element type (buttons only, links only, etc.)
- [ ] Persistent mode (hints stay visible)
- [ ] Smart hint generation (shorter hints for common elements)
- [ ] Multi-monitor support
- [ ] Configuration file
- [ ] Built-in element inspector

## 🙏 Inspiration

Based on [Vimium](https://vimium.github.io/) Chrome extension, which pioneered keyboard-based web navigation with hints.

This project brings that same efficiency to **all Windows applications**!

## 📝 License

MIT License - Feel free to use, modify, and distribute!

## 🤝 Contributing

Contributions welcome! This is a proof-of-concept that can be expanded in many directions.

---

**KeyHints Everywhere**: Never reach for the mouse again! 🖱️❌⌨️✅
