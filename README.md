# Virtual Taylor Frame

**Virtual Taylor Frame** is a Windows desktop application designed from the ground up for blind and visually impaired mathematics students. It provides a full digital emulation of a physical **Taylor Frame** (Taylor's Mathematical Frame), combining non-visual keyboard-first interaction, Accessible Output 3 (AO3) screen reader integration, a decoupled mathematical model, and high-contrast tactile rendering.

---

## 🌟 Key Features

1. **True Physical Taylor Frame Emulation**:
   - **8-Socket Orientations**: Each cell is an octagonal socket supporting 8 orientations (0° North to 315° NW in 45° steps).
   - **Arithmetic Pegs**:
     - **End A (Single Raised Bar)**: Digits `1` to `8` mapped by rotational orientation.
     - **End B (Two Raised Dots)**: `9`, `0`, and arithmetic operators (`+`, `-`, `×`, `÷`, `=`, `.`).
   - **Algebraic Pegs**:
     - **End A (V-Angle)**: Variables and letters (`x`, `y`, `z`, `a`, `b`, `c`, `d`, `e`).
     - **End B (Double Bar / Notch)**: Parentheses `(`, `)`, exponents `^`, radicals `√`, separators, and horizontal lines `_`.
2. **Keyboard-First Non-Visual Interaction**:
   - Every single operation is accessible via keyboard shortcuts without needing sight or mouse.
   - Dual-mode input: Type math characters directly (`0-9`, `+`, `-`, `*`, `/`, `=`, `x`, `y`, etc.) or manually rotate (`[` / `]`), flip (`F`), and toggle peg types (`T`).
3. **Screen Reader & Braille Output (Accessible Output 3)**:
   - Interfaces natively with **NVDA**, **JAWS**, and **Windows SAPI / Narrator**.
   - Dual speech and Braille display output.
   - Intelligent multi-level verbosity (**Minimal**, **Normal**, **Detailed**) with on-the-fly toggling (`F2` / `V`).
4. **Spatial Math & Frame Inspection**:
   - **Space**: Inspect current socket, peg type, tactile end, and orientation angle in degrees and compass bearings.
   - **F5**: Full construction summary of all rows and expressions.
   - **F6** (or `Shift+F5`): Read horizontal continuous row expressions.
   - **F7** (or `Ctrl+F5`): Read vertical columns (for column arithmetic / alignment).
   - **F8**: Inspect 4-way adjacent neighbor sockets (North, South, East, West).
5. **Persistence & Formats**:
   - Native `.tframe` format preserving pure mathematical state, coordinates, orientations, and metadata.
   - Plain text export (`.txt`) with ASCII visual layout and object inventory.
   - Structured JSON export (`.json`) for data interchange.
6. **Reversible History**:
   - Command pattern undo/redo operating directly on the mathematical state (`Ctrl+Z`, `Ctrl+Y`).

---

## ⌨️ Keyboard Shortcuts Reference

| Shortcut | Action | Accessible Speech Announcement |
|---|---|---|
| `Arrow Keys` | Move cursor by 1 cell | `"Down. Row 5, column 8. Empty."` |
| `Ctrl + Arrows` | Jump to next occupied peg | `"Jump Down. Row 5, column 12. Number 10."` |
| `Home` / `End` | Start / End of current row | `"Start of row. Column 1."` |
| `Ctrl + Home / End` | Top-Left (1,1) / Bottom-Right | `"Top-Left: Row 1, Column 1."` |
| `Page Up / Down` | Jump 5 rows up / down | `"Page Down. Row 6, column 8."` |
| `Ctrl + G` | Go to Row & Column Dialog | Accessible coordinate jump dialog |
| `0-9, +, -, *, /, =, ., a-z` | Direct placement & advance right | `"Placed Number 7 at Row 5, Column 8."` |
| `Delete` / `Backspace` | Remove peg at cursor | `"Removed Number 7. Empty."` |
| `Shift + Delete` | Clear entire current row | `"Cleared 4 objects from Row 5."` |
| `R` or `]` | Rotate 45° clockwise | `"Rotated clockwise to Number 2."` |
| `Shift + R` or `[` | Rotate 45° counter-clockwise | `"Rotated counter-clockwise to Number 8."` |
| `F` | Flip peg end (Bar <-> Dots) | `"Flipped to End B (Two Dots): Plus."` |
| `T` | Toggle peg family (Arithmetic <-> Algebraic) | `"Switched to Algebraic Type: Variable x."` |
| `Space` | Inspect current socket | Full tactile end, orientation, compass name |
| `F5` | Full frame inspection summary | Comprehensive mathematical breakdown |
| `F6` (or `Shift+F5`) | Read row horizontally | `"Row 5: 7 plus 3 equals 10."` |
| `F7` (or `Ctrl+F5`) | Read column vertically | `"Column 8 (4 items): Row 3: 4, Row 4: 1..."` |
| `F8` | Inspect surrounding 4 neighbors | `"Neighbors around Row 5, Column 8: ..."` |
| `F2` or `V` | Cycle verbosity level | `"Verbosity set to Detailed."` |
| `Ctrl + Z` | Undo last operation | `"Undone: Place 7."` |
| `Ctrl + Y` | Redo last operation | `"Redone: Place 7."` |
| `Shift + Arrows` | Expand selection rectangle | `"Selected 2 rows by 3 columns."` |
| `Ctrl + C / X / V` | Copy, Cut, Paste block | Clipboard block manipulation |
| `Ctrl + N` | New frame dialog | Choose frame dimensions |
| `Ctrl + O` | Open file (`.tframe`) | Open saved mathematical frame |
| `Ctrl + S` | Save file (`.tframe`) | Save current work |
| `Ctrl + Shift + S` | Save As | Save with new filename |
| `Ctrl + E` | Export to Plain Text or JSON | Export dialog |
| `F1` | Help Manual | Opens comprehensive accessible documentation |

---

## 🏗️ Architecture

```text
                    Virtual Taylor Frame
                             |
                     Mathematical Model
     (TaylorFrame, Cell, TaylorPeg, Types, ExpressionAnalyzer)
                             |
                  Command & History Layer
          (Place, Remove, Rotate, UndoRedoManager)
                             |
                 Accessibility / Event Layer
             (Announcer, AO3Engine, AudioCues)
                             |
                    Accessible Output 3
                             |
             +---------------+---------------+
             |               |               |
           Speech         Braille       Screen Reader
       (NVDA/JAWS/SAPI)   Display      (Accessible Name)
```

---

## 🚀 Running the Application

### 1. Launch with default 20x30 frame:
```bash
python main.py
```

### 2. Launch with a sample mathematical file:
```bash
python main.py examples/column_addition.tframe
```

### 3. Launch with custom dimensions & verbosity:
```bash
python main.py --rows 15 --cols 20 --verbosity detailed
```

---

## 🧪 Automated Testing

To run the complete automated test suite (54 unit, integration, and UI tests):
```bash
python -m pytest tests/ -v
```

To run with coverage report:
```bash
python -m pytest --cov=virtual_taylor_frame --cov-report=term-missing
```
