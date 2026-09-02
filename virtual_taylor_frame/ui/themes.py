"""
Accessible color palettes and high-contrast styling themes for Virtual Taylor Frame.
"""
from dataclasses import dataclass
from PySide6.QtGui import QColor


@dataclass
class ThemeColors:
    name: str
    background: QColor
    board_background: QColor
    socket_border: QColor
    socket_fill: QColor
    peg_body: QColor
    peg_border: QColor
    peg_tactile_ridge: QColor
    peg_text: QColor
    cursor_border: QColor
    cursor_fill: QColor
    selection_fill: QColor
    selection_border: QColor
    grid_label_color: QColor


THEMES = {
    "dark_high_contrast": ThemeColors(
        name="High Contrast Dark (Recommended)",
        background=QColor("#121212"),
        board_background=QColor("#1E1E1E"),
        socket_border=QColor("#555555"),
        socket_fill=QColor("#2A2A2A"),
        peg_body=QColor("#0D47A1"),
        peg_border=QColor("#90CAF9"),
        peg_tactile_ridge=QColor("#FFD600"),
        peg_text=QColor("#FFFFFF"),
        cursor_border=QColor("#00E676"),
        cursor_fill=QColor(0, 230, 118, 50),
        selection_fill=QColor(33, 150, 243, 60),
        selection_border=QColor("#2196F3"),
        grid_label_color=QColor("#B0BEC5"),
    ),
    "light_high_contrast": ThemeColors(
        name="High Contrast Light",
        background=QColor("#F5F5F5"),
        board_background=QColor("#FFFFFF"),
        socket_border=QColor("#9E9E9E"),
        socket_fill=QColor("#EEEEEE"),
        peg_body=QColor("#1565C0"),
        peg_border=QColor("#0D47A1"),
        peg_tactile_ridge=QColor("#D50000"),
        peg_text=QColor("#FFFFFF"),
        cursor_border=QColor("#FF6D00"),
        cursor_fill=QColor(255, 109, 0, 45),
        selection_fill=QColor(66, 165, 245, 50),
        selection_border=QColor("#1976D2"),
        grid_label_color=QColor("#37474F"),
    ),
    "classic_frame": ThemeColors(
        name="Classic Metal Frame",
        background=QColor("#2B2D30"),
        board_background=QColor("#3C3F41"),
        socket_border=QColor("#616161"),
        socket_fill=QColor("#212121"),
        peg_body=QColor("#455A64"),
        peg_border=QColor("#B0BEC5"),
        peg_tactile_ridge=QColor("#ECEFF1"),
        peg_text=QColor("#ECEFF1"),
        cursor_border=QColor("#FFD54F"),
        cursor_fill=QColor(255, 213, 79, 40),
        selection_fill=QColor(128, 203, 196, 50),
        selection_border=QColor("#80CBC4"),
        grid_label_color=QColor("#CFD8DC"),
    ),
}
