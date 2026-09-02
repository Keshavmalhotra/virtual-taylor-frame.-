"""
Vector rendering of octagonal sockets, tactile peg ridges, orientation indicators, and symbols.
"""
import math
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import (
    QPainter,
    QPen,
    QBrush,
    QColor,
    QFont,
    QPainterPath,
    QPolygonF,
)

from virtual_taylor_frame.model.peg import TaylorPeg
from virtual_taylor_frame.model.types import PegType, PegEnd, PegOrientation
from virtual_taylor_frame.ui.themes import ThemeColors


class PegRenderer:
    """
    Renders individual Taylor Frame sockets and tactile pegs with accurate physical features.
    """

    @staticmethod
    def draw_socket(painter: QPainter, rect: QRectF, theme: ThemeColors) -> None:
        """
        Draw an 8-pointed star / octagonal socket hole.
        """
        cx = rect.center().x()
        cy = rect.center().y()
        radius = min(rect.width(), rect.height()) * 0.44

        # Draw 8-pointed star socket polygon
        points = []
        num_points = 8
        for i in range(num_points):
            angle_outer = math.radians(i * 45 - 90)
            angle_inner = math.radians(i * 45 + 22.5 - 90)
            r_outer = radius
            r_inner = radius * 0.78

            p_outer = QPointF(cx + r_outer * math.cos(angle_outer), cy + r_outer * math.sin(angle_outer))
            p_inner = QPointF(cx + r_inner * math.cos(angle_inner), cy + r_inner * math.sin(angle_inner))
            points.append(p_outer)
            points.append(p_inner)

        star_poly = QPolygonF(points)

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(QPen(theme.socket_border, 1.5))
        painter.setBrush(QBrush(theme.socket_fill))
        painter.drawPolygon(star_poly)
        painter.restore()

    @staticmethod
    def draw_peg(
        painter: QPainter,
        rect: QRectF,
        peg: TaylorPeg,
        theme: ThemeColors,
    ) -> None:
        """
        Draw an authentic tactile peg inserted in the socket with directional ridges and symbol.
        """
        cx = rect.center().x()
        cy = rect.center().y()
        radius = min(rect.width(), rect.height()) * 0.40

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # 1. Draw Peg Body (Octagonal base)
        oct_points = []
        for i in range(8):
            angle = math.radians(i * 45 - 90 + 22.5)
            pt = QPointF(cx + radius * math.cos(angle), cy + radius * math.sin(angle))
            oct_points.append(pt)
        oct_poly = QPolygonF(oct_points)

        painter.setPen(QPen(theme.peg_border, 2.0))
        painter.setBrush(QBrush(theme.peg_body))
        painter.drawPolygon(oct_poly)

        # 2. Draw Tactile Feature (Bar / Dots / Angle)
        painter.translate(cx, cy)
        painter.rotate(peg.orientation.value)

        tactile_pen = QPen(theme.peg_tactile_ridge, 2.5)
        tactile_brush = QBrush(theme.peg_tactile_ridge)
        painter.setPen(tactile_pen)
        painter.setBrush(tactile_brush)

        r_feature = radius * 0.75

        if peg.peg_end == PegEnd.END_A_BAR:
            # Single raised bar pointing Up (0° in local rotated space)
            bar_w = radius * 0.28
            bar_h = radius * 1.1
            painter.drawRoundedRect(
                QRectF(-bar_w / 2, -bar_h + radius * 0.2, bar_w, bar_h),
                2.0,
                2.0,
            )

        elif peg.peg_end == PegEnd.END_B_DOTS:
            # Two distinct raised dots along the top direction
            dot_r = radius * 0.18
            painter.drawEllipse(QPointF(0, -radius * 0.55), dot_r, dot_r)
            painter.drawEllipse(QPointF(0, -radius * 0.15), dot_r, dot_r)

        elif peg.peg_end == PegEnd.END_A_ALGEBRA:
            # V-angle pointing Up
            path = QPainterPath()
            path.moveTo(-radius * 0.4, -radius * 0.2)
            path.lineTo(0, -radius * 0.7)
            path.lineTo(radius * 0.4, -radius * 0.2)
            painter.drawPath(path)

        elif peg.peg_end == PegEnd.END_B_ALGEBRA:
            # Double parallel bars
            bar_w = radius * 0.14
            bar_h = radius * 0.8
            painter.drawRoundedRect(QRectF(-radius * 0.25, -bar_h / 2, bar_w, bar_h), 1.0, 1.0)
            painter.drawRoundedRect(QRectF(radius * 0.11, -bar_h / 2, bar_w, bar_h), 1.0, 1.0)

        painter.restore()

        # 3. Draw Math Symbol & Braille in center/overlay
        painter.save()
        painter.setPen(QPen(theme.peg_text))
        font_size = max(8, int(radius * 0.55))
        font = QFont("Segoe UI", font_size, QFont.Weight.Bold)
        painter.setFont(font)
        text_rect = QRectF(rect.left(), rect.center().y() + radius * 0.15, rect.width(), radius * 0.8)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, peg.symbol)
        painter.restore()
