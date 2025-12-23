# Lightning Explorer - Vimium-Style Navigation Guide

## 🎯 Core Concept

**Every file and folder gets a 2-letter hint label like `[fj]`, `[kl]`, `[aa]`**

Just **type the two letters** to instantly open/navigate to that file!

---

## 📖 How It Works

### Example Screen
```
Current: C:\Users\Andrew\Documents

[aa] 📁 ..
[ab] 📁 Projects          <-- Type 'a' then 'b' to enter
[ac] 📁 Notes             <-- Type 'a' then 'c' to enter
[ad] 📄 resume.pdf        <-- Type 'a' then 'd' to open
[ae] 📄 todo.txt          <-- Type 'a' then 'e' to open
[af] 📁 Archive           <-- Type 'a' then 'f' to enter
...
```

### Navigation Example
```
Want to open "Projects" folder?
1. See the hint: [ab]
2. Type: a
3. Type: b
4. Done! You're now in Projects folder

Want to open "resume.pdf"?
1. See the hint: [ad]  
2. Type: a
3. Type: d
4. Done! PDF opens in default app
```

---

## ⌨️ All Controls

### Hint Navigation (PRIMARY)
| Action | How To |
|--------|--------|
| Open any file/folder | Type its 2-letter hint (e.g., `fj`, `kl`) |
| Go to parent directory | `Backspace` OR type `aa` (usually the `..` hint) |
| Clear typed hint | `Esc` |

### Search
| Action | How To |
|--------|--------|
| Enter search | `/` |
| Type to filter | Just type in search box |
| Exit search | `Esc` then switch focus back |

### Other
| Action | Key |
|--------|-----|
| Refresh directory | `F5` |
| Show help | `?` |

---

## 💡 Advantages Over Traditional Navigation

### Old Way (Vim-style j/k)
```
Want 15th file in list?
Press j 15 times... 😩
```

### New Way (Vimium hints)
```
Want any file in list?
Type its hint (2 keystrokes) ⚡
```

### Example Comparison

**Scenario:** Open a file that's 20 items down in the list

| Method | Keystrokes | Time |
|--------|-----------|------|
| Arrow keys | 20 presses | Slow |
| Vim j/k | 20 presses | Slow |
| Mouse | Click + aim | Medium |
| **Vimium hints** | **2 letters** | **Instant** ⚡ |

---

## 🎨 Visual Feedback

### Hint Buffer Display
Bottom right corner shows what you've typed:

```
Hint: f     ← You typed 'f', waiting for second letter
Hint: fj    ← Complete! File opens immediately
```

### Hint Colors
- **Hint labels**: Yellow/cyan `[ab]` 
- **Your input**: Green in status bar
- **Files**: Colored by type (folders/files)

---

## 🚀 Pro Tips

### 1. Home Row Advantage
Hints use letters `a-z`, so your fingers never leave home row!

### 2. Pattern Recognition
After using it a bit, you'll remember:
- Top items = `aa`, `ab`, `ac`...
- Middle items = `fa`, `fb`, `fc`...
- Bottom items = `za`, `zb`, `zc`...

### 3. Quick Parent Navigation
- `..' is usually `[aa]`
- Just type `aa` to go up!
- Or use `Backspace`

### 4. Dense Directories
In a folder with 100+ files:
- No scrolling needed
- No repeated key presses
- Direct access to ANY file with 2 keys

---

## 🎯 Common Workflows

### Workflow 1: Browse and Open
```
1. Launch Lightning Explorer
2. See list of folders with hints
3. Type hint to enter folder (e.g., 'ab')
4. Type hint to open file (e.g., 'cd')
```

### Workflow 2: Search and Navigate
```
1. Press '/' to search
2. Type filename to filter
3. See fewer results with new hints
4. Type hint to open desired file
```

### Workflow 3: Deep Navigation
```
Documents → Projects → Python → MyProject
   'ab'        'cf'       'ad'      'ae'
   
Just 8 keystrokes to navigate 4 levels deep!
```

---

## 🔮 Why This Is Better

### Compared to Windows Explorer
✅ **No mouse needed**
✅ **Faster than clicking**
✅ **No scrolling required**
✅ **Direct access to any file**

### Compared to Vim j/k navigation
✅ **No repeated key presses**
✅ **Works in dense directories**
✅ **Instant access vs sequential**

### Inspired by Vimium Chrome Extension
If you've used Vimium to navigate web pages with hints, this is the exact same concept applied to file browsing!

---

## 🎓 Learning Curve

### First 5 Minutes
- "Oh, I type the letters in the brackets!"
- Still learning which hint goes where

### After 30 Minutes
- Natural, automatic usage
- Eyes find hint, fingers type it
- Faster than you ever were with mouse

### After 1 Hour
- Can't imagine going back to Windows Explorer
- Telling everyone about how fast you can navigate
- Looking for ways to add hints to other apps 😄

---

## 🐛 Troubleshooting

**Q: I typed a letter and nothing happened**
- Make sure search mode is OFF (press Esc)
- Make sure file list window has focus (click on it)

**Q: How do I cancel a hint in progress?**
- Press `Esc` to clear the hint buffer

**Q: The hints changed after I searched**
- Yes! Hints regenerate based on visible files
- This is intentional - always 2 letters to any visible file

**Q: Can I customize the hints?**
- Currently uses a-z combinations
- Future: may add customization options

---

## 🎉 Summary

**Old way:** Click click click... or j j j j j j...
**New way:** See hint → Type 2 letters → Done! ⚡

**This is keyboard navigation evolved!**

---

*Inspired by Vimium browser extension*
*Built for speed, designed for efficiency*
