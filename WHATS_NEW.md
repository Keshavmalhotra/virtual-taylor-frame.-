# What's New

## Dynamically Extendable Frame Size

- Extend the frame by 5 rows with `Ctrl+Alt+Down`.
- Extend the frame by 5 columns with `Ctrl+Alt+Right`.
- Extend both dimensions by 5 with `Ctrl+Alt+End`.
- Existing pegs and mathematical content remain unchanged.
- Frame extensions are undoable and preserved in `.tframe` files.
- AO3 announces the updated frame dimensions after extension.

## Frame Shrinking

- Shrink the frame by 5 rows with `Ctrl+Alt+Up`.
- Shrink the frame by 5 columns with `Ctrl+Alt+Left`.
- Shrink both dimensions by 5 with `Ctrl+Alt+Home`.
- Shrinking is blocked when objects would be removed and is undoable.

## Mathematical Manipulation

- Select one or more pegs with the existing selection controls.
- Move a selected peg, region, or expression with the arrow keys.
- Group movement preserves relative coordinates, peg type, peg end, orientation, and identity.
- Copy and paste preserves the mathematical structure and relative spacing of selected objects.
- Selection movement is integrated with the existing undo/redo history.
- AO3 announces selection and manipulation actions using the existing verbosity settings.
- Contiguous mathematical structures can be selected through the frame model with `select_expression`.
- Manipulated objects continue to save and load through the existing `.tframe` format.

## Meaningful Mathematical Navigation

- Jump between numbers, operators, and mathematical expressions without traversing empty sockets.
- `Ctrl+Alt+N/P`: next/previous number.
- `Ctrl+Alt+O/I`: next/previous operator.
- `Ctrl+Alt+E/W`: next/previous expression.
- `Ctrl+Alt+H/J`: beginning/end of the current expression.
- AO3 announces destinations with mathematical labels and logical frame coordinates.

## Named Regions

- Define rectangular logical frame areas such as Question, Working, and Answer.
- Create a region from the current selection with `Ctrl+Alt+R`, then enter its name.
- Navigate between regions with `Ctrl+Alt+G`; add Shift for the previous region.
- Inspect the region containing the cursor with `Ctrl+Alt+M`.
- Regions are announced through AO3 and saved in `.tframe` files.
- Existing `.tframe` files without regions remain compatible.
- F5 announces named regions separately and skips empty sockets. Without regions, existing F5 behavior is unchanged.

## Configurable Input Auto-Advance

- Added `Auto-advance after input` under the Accessibility menu.
- When enabled, input advances the cursor to the next column as before.
- When disabled, input leaves the cursor on the entered object.
- Toggle with `F3`; the preference persists between launches.
- The setting change is announced through AO3.
- AO3 announces “Auto-advance enabled.” or “Auto-advance disabled.” when changed.
