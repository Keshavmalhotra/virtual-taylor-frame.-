"""
Accessible New Frame Dialog to configure custom grid dimensions.
"""
from typing import Tuple
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QDialogButtonBox,
    QComboBox,
)


class NewFrameDialog(QDialog):
    """
    Dialog for configuring dimensions when creating a new Taylor Frame.
    """

    PRESETS = [
        ("Standard Frame (20 rows x 30 columns)", 20, 30),
        ("Small Practice Frame (15 rows x 20 columns)", 15, 20),
        ("Large Mathematical Frame (25 rows x 35 columns)", 25, 35),
        ("Compact Frame (10 rows x 15 columns)", 10, 15),
    ]

    def __init__(self, default_rows: int = 20, default_cols: int = 30, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Taylor Frame")
        self.setAccessibleName("Create New Taylor Frame Dialog")

        layout = QVBoxLayout(self)

        # Preset Selector
        preset_layout = QHBoxLayout()
        preset_lbl = QLabel("&Preset Size:", self)
        self.preset_combo = QComboBox(self)
        for label, r, c in self.PRESETS:
            self.preset_combo.addItem(label, (r, c))
        self.preset_combo.addItem("Custom Dimensions...", (default_rows, default_cols))
        preset_lbl.setBuddy(self.preset_combo)
        preset_layout.addWidget(preset_lbl)
        preset_layout.addWidget(self.preset_combo)
        layout.addLayout(preset_layout)

        # Custom Rows
        row_layout = QHBoxLayout()
        row_lbl = QLabel("&Number of Rows (5 - 50):", self)
        self.row_spin = QSpinBox(self)
        self.row_spin.setRange(5, 50)
        self.row_spin.setValue(default_rows)
        row_lbl.setBuddy(self.row_spin)
        row_layout.addWidget(row_lbl)
        row_layout.addWidget(self.row_spin)
        layout.addLayout(row_layout)

        # Custom Columns
        col_layout = QHBoxLayout()
        col_lbl = QLabel("&Number of Columns (5 - 50):", self)
        self.col_spin = QSpinBox(self)
        self.col_spin.setRange(5, 50)
        self.col_spin.setValue(default_cols)
        col_lbl.setBuddy(self.col_spin)
        col_layout.addWidget(col_lbl)
        col_layout.addWidget(self.col_spin)
        layout.addLayout(col_layout)

        self.preset_combo.currentIndexChanged.connect(self._on_preset_changed)

        # Buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def _on_preset_changed(self, index: int) -> None:
        data = self.preset_combo.currentData()
        if data:
            r, c = data
            self.row_spin.setValue(r)
            self.col_spin.setValue(c)

    def get_dimensions(self) -> Tuple[int, int]:
        return self.row_spin.value(), self.col_spin.value()
