"""
Interchange JSON exporter for Taylor Frame.
"""
import json
from typing import Dict, Any
from virtual_taylor_frame.model.frame import TaylorFrame


class JSONExporter:
    """
    Exports Taylor Frame to standardized generic JSON for external tools/web visualizers.
    """

    @staticmethod
    def export_json(frame: TaylorFrame, indent: int = 2) -> str:
        data = {
            "dimensions": {
                "rows": frame.rows,
                "columns": frame.cols,
            },
            "cursor": {
                "row": frame.display_cursor_row,
                "column": frame.display_cursor_col,
            },
            "occupied_count": frame.count_occupied(),
            "cells": [
                {
                    "row": cell.display_row,
                    "column": cell.display_col,
                    "symbol": cell.peg.symbol,
                    "label": cell.peg.label,
                    "type": cell.peg.peg_type.value,
                    "end": cell.peg.peg_end.value,
                    "orientation": cell.peg.orientation.value,
                    "compass": cell.peg.orientation.compass_name,
                    "braille": cell.peg.braille,
                }
                for cell in frame.occupied_cells()
            ],
        }
        return json.dumps(data, indent=indent, ensure_ascii=False)
