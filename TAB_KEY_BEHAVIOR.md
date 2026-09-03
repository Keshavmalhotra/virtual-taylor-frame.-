# Tab key behavior

This is the behavior implemented by the current source. No application source
files were changed for this investigation.

## Main window

`virtual_taylor_frame.ui.main_window.MainWindow` creates a `QMainWindow` with:

- a `QMenuBar` containing the File, Edit, Navigate, Inspect, Accessibility, and
  Help menus;
- a `QScrollArea` as the central widget; and
- a `TaylorFrameWidget` installed inside the scroll area.

During `_init_ui()`, the frame widget is given focus with
`self.frame_widget.setFocus()` (`main_window.py`, approximately lines 95-101).
The frame widget has `StrongFocus` (`frame_widget.py`, approximately line 87).

There is no `Tab`, `Key_Tab`, `Backtab`, or `Shift+Tab` branch anywhere in the
application's key handling. `TaylorFrameWidget.keyPressEvent()` handles arrow
keys and the application's other shortcuts, then falls through to
`super().keyPressEvent(event)` for unrecognized keys. Tab is therefore handled
by Qt's normal focus traversal before it becomes custom Taylor Frame input; it
does not invoke any Taylor Frame command.

## What receives focus

When focus is on the `TaylorFrameWidget`, Tab leaves the grid and follows the
normal Qt focus chain. The next focus target is the next focusable widget in
the containing window, normally the scroll area's focus target/viewport or the
next focusable window control according to Qt's focus-chain ordering. The
source does not define a custom tab order (`setTabOrder` is not used), so the
application does not guarantee a custom named destination for Tab.

When focus is in a dialog, Tab is handled by Qt within that dialog's normal
focus chain. For example, `GoToDialog` and `NewFrameDialog` contain focusable
`QSpinBox` controls, and `InspectDialog` explicitly focuses its text editor on
opening. Tab moves among the dialog's focusable controls according to standard
Qt behavior.

When a menu is open or has keyboard focus, Qt's menu handling controls Tab and
Shift+Tab; no application key handler changes that behavior. `QAction`
objects in `MainWindow._create_actions()` are commands, not custom Tab targets.

## AO3 and frame state

Tab and Shift+Tab do not call `Announcer.output()` or any announcement method.
They therefore produce no AO3 speech/Braille output as a consequence of the
key itself.

They also do not call `TaylorFrame.set_cursor()`, editing commands, selection
commands, or any other model mutation. The mathematical frame state is
unchanged. Only the Qt focus owner changes.

## Shift+Tab

Shift+Tab is the reverse of Tab under standard Qt focus traversal. It has no
custom application handling, no Taylor Frame behavior, and no AO3 output.

## Summary

Tab behavior depends on the current focus context:

1. In the grid, Qt transfers focus out of `TaylorFrameWidget` through the
   containing window's standard focus chain.
2. In a dialog, Qt moves focus between that dialog's controls.
3. In an open menu, Qt handles menu focus navigation.

In all cases, the application does not intercept Tab explicitly, does not
perform custom Taylor Frame navigation, does not announce through AO3, and does
not alter the mathematical frame.
