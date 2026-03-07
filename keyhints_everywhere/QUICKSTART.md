# KeyHints Everywhere - Quick Start

## Install and Run (30 seconds)

```bash
# 1. Install dependencies
cd keyhints_everywhere
pip install -r requirements.txt

# 2. Run the app
python src/keyhints.py
```

You should see:
```
KeyHints Everywhere - Starting...
Press CTRL+SHIFT+K to activate hints on any window
Press CTRL+C to exit
```

## First Use

1. **Open any application** (try File Explorer: `Win+E`)

2. **Press `CTRL+SHIFT+K`**

3. **Watch the magic!** Yellow hint labels appear:
   ```
   [aa] on first button
   [ab] on second button
   [ac] on third button
   ...
   ```

4. **Type a hint** (e.g., `ab`) to click that element

5. **Done!** The overlay disappears and the element is clicked

## Test Mode (No Hotkey)

Want to test without hotkeys?

```bash
python src/keyhints.py --test
```

This scans the **currently active window** immediately and shows hints.

## Tips for First-Timers

✅ **Best apps to try first:**
- Windows File Explorer
- Google Chrome
- Any dialog box with buttons

✅ **What to expect:**
- Yellow `[aa]` style labels
- Big typing buffer at bottom showing what you type
- Hint count in status bar

✅ **If you make a mistake:**
- Press `ESC` to cancel
- The overlay closes, no harm done

✅ **To exit the app:**
- Press `CTRL+C` in the terminal

## Common First-Run Issues

**Issue: "Module not found"**
```bash
pip install uiautomation pyautogui keyboard PyGetWindow
```

**Issue: "No hints appear"**
- Make sure target window is in foreground
- Try File Explorer first (most reliable)
- Some apps don't expose UI elements

**Issue: "Hints in wrong place"**
- Some apps have complex layouts
- Try again or try different app

**Issue: "Permission denied"**
- Some apps require admin rights
- Try running terminal as administrator

## Next Steps

Once it works:
- Try it on different applications
- Customize the hotkey in the code
- Read the full README.md for details

---

**That's it!** You now have Vimium-style hints in every Windows app! 🎉
