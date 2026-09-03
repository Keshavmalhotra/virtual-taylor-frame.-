# Virtual Taylor Frame: User Guide

Virtual Taylor Frame is a keyboard-friendly way to write and explore
mathematics on a computer. It behaves like a Taylor Frame: a grid of small
places holds artificial pegs. You can use it for arithmetic, algebra,
practice exercises, demonstrations, and checking the layout of a calculation.

This guide is for people using the finished Windows application.

## Start the application

1. Download `VirtualTaylorFrame-Setup.exe` from the project's GitHub Releases
   page.
2. Run the installer and follow the instructions. It creates a Start Menu
   shortcut and can create a Desktop shortcut.
3. Open **Virtual Taylor Frame** from that shortcut.

You can also download `VirtualTaylorFrame-Portable.zip`. Extract the ZIP to a
folder and run `VirtualTaylorFrame.exe` from that folder. The portable copy
does not need a separate installation.

When the application opens, the cursor is in the first socket: row 1, column
1. You will hear a welcome message if speech output is available. The main
part of the window is the frame, a grid with row and column numbers.

## The basic idea

Each square in the grid is a **socket**. A socket can be empty or can hold one
artificial peg.

A peg has two important choices:

- Its **type**: Arithmetic or Algebraic.
- Its **end**: the end facing up.

Turning the peg changes its **orientation**. There are eight directions,
45 degrees apart: North, North-East, East, South-East, South, South-West,
West, and North-West.

For example, an Arithmetic peg can show numbers 1 through 8 with its bar end.
Its dots end can show 9, 0, plus, minus, multiplication, division, equals,
or a decimal point. Algebraic pegs provide letters such as `x`, `y`, and `z`,
along with parentheses, an exponent sign, a square-root sign, and other
algebraic punctuation.

You do not need to calculate the direction yourself. Typing a supported
character places the correct peg in the current socket.

## Place mathematical objects

1. Move to the socket where you want to begin.
2. Type a number, letter, or symbol.
3. The peg is placed and the application announces it.
4. By default, the cursor moves one column to the right after typing.

For example, to make `7 + 5 = 12`, type:

```text
7 + 5 = 1 2
```

Spaces above are only for readability. Type the characters in consecutive
sockets. Use **F6** to hear the expression in the current row.

Supported direct characters include numbers, `+`, `-`, `*`, `/`, `=`, `.`,
letters used by the frame, parentheses, `^`, and `_`. The application also
accepts the keyboard forms `*` and `/` for multiplication and division.

## Move around the frame

- **Arrow keys**: move one socket at a time.
- **Ctrl + Arrow**: jump to the next occupied socket in that direction.
- **Home**: go to the first column of the current row.
- **End**: go to the last column of the current row.
- **Ctrl + Home**: go to row 1, column 1.
- **Ctrl + End**: go to the bottom-right socket.
- **Page Up / Page Down**: move five rows up or down.
- **Ctrl + G**: open a dialog and enter an exact row and column.

The current position and the object in the socket are announced as you move.
At an edge, the application announces that you have reached the boundary.

## Inspect what you have written

- **Space**: describe the current socket, including its row, column, object,
  peg type, peg end, direction, and angle.
- **F6**: read the current row as a mathematical expression.
- **F7**: read the current column from top to bottom.
- **F5**: read a summary of the whole frame.
- **Shift + F5**: read the current row (same purpose as F6).
- **Ctrl + F5**: read the current column (same purpose as F7).
- **F8**: describe the four neighboring sockets: North, South, East, and West.

There are also useful jumps for mathematical work. **Ctrl + Alt + T** and
**Ctrl + Alt + P** find the next or previous number. **Ctrl + Alt + O** and
**Ctrl + Alt + I** find the next or previous operator. **Ctrl + Alt + E** and
**Ctrl + Alt + W** move between expressions.

## Change or remove a peg

Put the cursor on an occupied socket, then use:

- **R** or **]**: turn the peg clockwise by 45 degrees.
- **Shift + R** or **[**: turn it counter-clockwise by 45 degrees.
- **F**: turn the peg over to its other end.
- **T**: change between the Arithmetic and Algebraic peg types.
- **Delete** or **Backspace**: remove the peg in the current socket.
- **Shift + Delete**: remove every peg in the current row.

The application announces the result of each change. Turning or changing an
empty socket produces a message explaining that there is no peg to change.

## Select, move, copy, and clear groups

You can work with a rectangular group of sockets.

- Hold **Shift** and press an Arrow key to extend a selection.
- Hold the left mouse button and drag across the frame to select with the
  mouse.
- **Ctrl + A**: select the entire frame.
- **Escape**: clear the selection.
- **Ctrl + Arrow** while a selection is active: move the selected group in the
  chosen direction.
- **Ctrl + C**: copy the selected group. With no selection, it copies the
  current socket.
- **Ctrl + X**: copy and remove the selected group.
- **Ctrl + V**: paste the copied group starting at the current socket.
- **Delete** or **Backspace** with a selection: clear the selected sockets.
- **Ctrl + Z**: undo the last change.
- **Ctrl + Y**, or **Ctrl + Shift + Z**: redo a change.

The Edit menu contains the same actions. The Frame menu also lets you clear
all objects, or extend and shrink the frame by five rows and/or columns.

## Named regions

Named regions let you label parts of a frame. For example, you might make
three regions called **Question**, **Working**, and **Answer**. This makes a
large exercise easier to navigate and lets speech identify the part of the
exercise where the cursor has arrived.

To create one:

1. Select the rectangular area.
2. Press **Ctrl + Alt + R**.
3. Type a name and confirm it.

Use **Ctrl + Alt + G** to jump to the next named region, or **Ctrl + Alt +
Shift + G** to move to the previous one. Use **Ctrl + Alt + M** to hear the
name and contents of the region containing the cursor. Named regions are
saved in `.tframe` files.

You can turn automatic region announcements on or off with **F4**. The
setting is also available in the Accessibility menu and is remembered for
later sessions.

## Accessibility and reading options

The application is designed to be usable from the keyboard. It announces
movement, placement, deletion, selections, boundaries, and inspections.

**F2** or **V** changes the amount of detail:

- **Minimal**: short announcements, usually the symbol or essential position.
- **Normal**: the usual position and object information.
- **Detailed**: the object, type, peg end, angle, and compass direction.

Speech is sent through the application's accessibility output system when a
supported screen reader or speech service is available. On Windows, speech
can fall back to Windows SAPI. The application works with the screen-reader
and accessibility software already installed on the computer; it does not
replace that software.

Sound cues can be enabled or disabled from the Accessibility menu. They are
short sounds for actions such as placing, removing, and reaching an edge.

## Save and open your work

- **Ctrl + S**: save the current frame.
- **Ctrl + Shift + S**: choose a new filename and save a copy.
- **Ctrl + O**: open an existing frame.
- **Ctrl + N**: create a new frame and choose its size.

The normal file type is `.tframe`. It stores the frame, cursor position,
objects, orientations, and named regions so you can continue later. Saving
does not put your work inside the program's installation folder; choose a
personal documents folder or another location you control.

The File menu can also export the current frame as:

- **Plain text (`.txt`)**: a readable description, row expressions, grid, and
  object list.
- **JSON (`.json`)**: a structured copy useful for exchanging frame data with
  other tools.

## Preferences

In the Accessibility menu:

- **F3** toggles automatic movement to the next column after typing.
- **F4** toggles announcements when entering named regions.
- **F2** cycles speech detail.
- Sound cues can be switched on or off.

These choices are remembered in your Windows user profile and are not stored
in the installation folder.

## Troubleshooting

### Nothing is spoken

Check that a screen reader or Windows speech service is running and that your
computer has an available voice. Try pressing **F2** to change the detail
level. The application still provides keyboard and visual feedback when no
speech driver is available.

### Typing does not place a symbol

Click the frame or press an Arrow key to return focus to the grid. Check that
you are not holding Ctrl. Only the supported mathematical characters are
placed directly.

### The cursor did not move after typing

Automatic advance may be off. Press **F3**, or enable **Auto-advance after
input** in the Accessibility menu.

### I cannot find a saved frame

Use **Ctrl + O** and browse to the folder where you saved the `.tframe` file.
The program does not automatically search every folder on the computer.

### I reached an edge unexpectedly

This is normal. The frame announces its boundary and keeps the cursor inside
the grid. Use **Ctrl + G** to go directly to another position.

## Getting help inside the application

Press **F1** to open the built-in keyboard guide and documentation. You can
also use the File, Edit, Frame, Inspect, Accessibility, and Help menus with
the mouse or keyboard.

## About the Project

Virtual Taylor Frame was created by Keshav Malhotra. Keshav is the creator of
the Virtual Taylor Frame. The application was developed with substantial help
from Antigravity AI and Codex, and this user guide was also written with help
from AI. This guide is intended to be useful and honest about how the project
was made; it does not claim that Keshav personally wrote every line of code or
that every feature has been tested.

If you find a problem, notice something that does not work correctly, or have
feedback, please contact Keshav:

- Telegram: `@itskeshavmalhotra`
- Email: `itskeshavmalhotra@gmail.com`
