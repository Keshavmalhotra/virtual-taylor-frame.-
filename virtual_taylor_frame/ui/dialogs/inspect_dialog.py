"""
Accessible Frame Inspection & Expression Viewer Dialog.
"""
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPlainTextEdit,
    QPushButton,
    QApplication,
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt


class InspectDialog(QDialog):
    """
    Dialog displaying the full text summary of the current Taylor Frame.
    """

    def __init__(self, summary_text: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Frame Inspection & Expressions")
        self.resize(680, 500)
        self.setAccessibleName("Taylor Frame Inspection Viewer")

        layout = QVBoxLayout(self)

        self.text_edit = QPlainTextEdit(self)
        self.text_edit.setPlainText(summary_text)
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Consolas", 11))
        self.text_edit.setAccessibleName("Inspection Summary Text")
        self.text_edit.setAccessibleDescription("Use Arrow keys to read through the complete frame description.")
        layout.addWidget(self.text_edit)

        btn_layout = QHBoxLayout()
        self.copy_btn = QPushButton("&Copy to Clipboard", self)
        self.copy_btn.setAccessibleName("Copy summary to clipboard")
        self.copy_btn.clicked.connect(self._copy_to_clipboard)
        btn_layout.addWidget(self.copy_btn)

        btn_layout.addStretch()

        self.close_btn = QPushButton("&Close", self)
        self.close_btn.setAccessibleName("Close Dialog")
        self.close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.close_btn)

        layout.addLayout(btn_layout)
        self.text_edit.setFocus()

    def _copy_to_clipboard(self) -> None:
        QApplication.clipboard().setText(self.text_edit.toPlainText())
        self.copy_btn.setText("Copied!")
