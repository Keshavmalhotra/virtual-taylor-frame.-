"""
Accessible Go-To Row & Column Dialog for Virtual Taylor Frame.
"""
from typing import Tuple, Optional
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QPushButton,
    QDialogButtonBox,
)
from PySide6.QtCore import Qt


class GoToDialog(QDialog):
    """
    Accessible dialog to jump directly to a row and column coordinate (1-based).
    """

    def __init__(
        self,
        current_row: int,
        current_col: int,
        max_rows: int,
        max_cols: int,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Go To Coordinate")
        self.setAccessibleName("Go To Row and Column Dialog")
        self.setAccessibleDescription("Enter target row and column to move the cursor.")

        layout = QVBoxLayout(self)

        # Row Input
        row_layout = QHBoxLayout()
        row_label = QLabel("&Row (1 to %d):" % max_rows, self)
        self.row_spin = QSpinBox(self)
        self.row_spin.setRange(1, max_rows)
        self.row_spin.setValue(current_row + 1)
        self.row_spin.setAccessibleName("Target Row")
        row_label.setBuddy(self.row_spin)
        row_layout.addWidget(row_label)
        row_layout.addWidget(self.row_spin)
        layout.addLayout(row_layout)

        # Column Input
        col_layout = QHBoxLayout()
        col_label = QLabel("&Column (1 to %d):" % max_cols, self)
        self.col_spin = QSpinBox(self)
        self.col_spin.setRange(1, max_cols)
        self.col_spin.setValue(current_col + 1)
        self.col_spin.setAccessibleName("Target Column")
        col_label.setBuddy(self.col_spin)
        col_layout.addWidget(col_label)
        col_layout.addWidget(self.col_spin)
        layout.addLayout(col_layout)

        # Dialog Buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

        self.row_spin.setFocus()
        self.row_spin.selectAll()

    def get_coordinates(self) -> Tuple[int, int]:
        """Returns 0-based (row, col)."""
        return self.row_spin.value() - 1, self.col_spin.value() - 1
