"""
Accessible Help & Keyboard Reference Dialog for Virtual Taylor Frame.
"""
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTextBrowser,
    QPushButton,
    QHBoxLayout,
)
from PySide6.QtCore import Qt


HELP_MARKDOWN = """
# Virtual Taylor Frame: Keyboard & Accessibility Guide

The **Virtual Taylor Frame** is designed to be operated entirely using the keyboard and screen reader.

---

## 1. Navigation Commands
* **Arrow Keys (Up, Down, Left, Right)**: Move cursor by 1 cell.
* **Ctrl + Arrow Keys**: Jump to next occupied peg in that direction.
* **Home**: Jump to Column 1 (start of current row).
* **End**: Jump to last column of current row.
* **Ctrl + Home**: Jump to Top-Left (Row 1, Column 1).
* **Ctrl + End**: Jump to Bottom-Right (or last occupied cell).
* **Page Up / Page Down**: Jump up / down by 5 rows.
* **Ctrl + G**: Go directly to a specific Row and Column.

---

## 2. Placing & Manipulating Pegs
* **Direct Typing (0-9, +, -, *, /, =, ., x, y, z, etc.)**:
  Immediately places the corresponding Taylor peg into the socket and advances cursor right.
* **Delete or Backspace**: Remove peg from current cell.
* **Shift + Delete**: Clear all pegs in the current row.
* **R or ]**: Rotate current peg 45° clockwise.
* **Shift + R or [**: Rotate current peg 45° counter-clockwise.
* **F**: Flip peg between End A (Bar) and End B (Two Dots).
* **T**: Toggle peg type between Arithmetic and Algebraic.

---

## 3. Accessible Inspection & Speech
* **Space**: Inspect current cell (reads coordinates, symbol, peg type, tactile end, orientation angle, and compass direction).
* **F5**: Describe complete frame construction (all rows and expressions).
* **F6 (or Shift + F5)**: Read current row horizontally as a mathematical expression.
* **F7 (or Ctrl + F5)**: Read current column vertically.
* **F8**: Inspect 4-way adjacent neighboring sockets (North, South, East, West).
* **F2 (or V)**: Cycle speech verbosity level (**Minimal** -> **Normal** -> **Detailed**).
* **Ctrl + Alt + T**: Find the next number in the frame.

---

## 4. Editing & Block Selection
* **Ctrl + Alt + Down**: Extend frame by 5 rows.
* **Ctrl + Alt + Right**: Extend frame by 5 columns.
* **Ctrl + Alt + End**: Extend frame by 5 rows and 5 columns.
* **Ctrl + Z**: Undo last operation.
* **Ctrl + Y (or Ctrl + Shift + Z)**: Redo last undone operation.
* **Shift + Arrow Keys**: Expand rectangular selection block.
* **Ctrl + C**: Copy selected block.
* **Ctrl + X**: Cut selected block.
* **Ctrl + V**: Paste copied block starting at current cursor.
* **Escape**: Clear selection / cancel move mode.

---

## 5. File Operations
* **Ctrl + N**: Create new frame.
* **Ctrl + O**: Open an existing `.tframe` file.
* **Ctrl + S**: Save current frame (`.tframe`).
* **Ctrl + Shift + S**: Save As.
* **Ctrl + E**: Export frame to accessible Plain Text (`.txt`) or JSON (`.json`).
* **F1**: Open this Help Dialog.

---

## 6. Taylor Frame Physical Peg Representation
* **Arithmetic Type (End A - Bar)**:
  * 0° (North): **1** | 45° (NE): **2** | 90° (East): **3** | 135° (SE): **4**
  * 180° (South): **5** | 225° (SW): **6** | 270° (West): **7** | 315° (NW): **8**
* **Arithmetic Type (End B - Two Dots)**:
  * 0° (North): **9** | 45° (NE): **0** | 90° (East): **+** | 135° (SE): **-**
  * 180° (South): **×** | 225° (SW): **÷** | 270° (West): **=** | 315° (NW): **.** (decimal)
"""


class HelpDialog(QDialog):
    """
    Accessible help dialog presenting markdown-formatted guide.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Virtual Taylor Frame - Help & Keyboard Reference")
        self.resize(720, 560)
        self.setAccessibleName("Help and Keyboard Reference Dialog")

        layout = QVBoxLayout(self)

        self.browser = QTextBrowser(self)
        self.browser.setMarkdown(HELP_MARKDOWN)
        self.browser.setAccessibleName("Keyboard Reference and Documentation")
        self.browser.setAccessibleDescription("Use Arrow keys or Page Up and Page Down to read through the guide.")
        layout.addWidget(self.browser)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.close_btn = QPushButton("&Close", self)
        self.close_btn.setAccessibleName("Close Help Dialog")
        self.close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.close_btn)

        layout.addLayout(btn_layout)
        self.browser.setFocus()
