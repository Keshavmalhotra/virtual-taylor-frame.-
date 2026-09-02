"""
Unit tests for .tframe persistence, format versioning, error handling, and exporters.
"""
import pytest
import tempfile
import os
import json
from pathlib import Path

from virtual_taylor_frame.model import (
    TaylorFrame,
    TaylorPeg,
    PegOrientation,
)
from virtual_taylor_frame.storage import (
    TFrameStorage,
    InvalidTFrameError,
    IncompatibleVersionError,
    TextExporter,
    JSONExporter,
)


class TestStorage:
    def test_save_and_load_tframe(self):
        frame = TaylorFrame(rows=18, cols=24)
        frame.place_peg(2, 5, TaylorPeg.from_symbol("7"))
        frame.place_peg(2, 6, TaylorPeg.from_symbol("+"))
        frame.place_peg(2, 7, TaylorPeg.from_symbol("3"))
        frame.set_cursor(2, 7)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test_math.tframe")
            meta = {"title": "Lesson 1", "notes": "Addition problem"}
            TFrameStorage.save(filepath, frame, metadata=meta)

            loaded_frame, loaded_meta = TFrameStorage.load(filepath)
            assert loaded_frame.rows == 18
            assert loaded_frame.cols == 24
            assert loaded_frame.cursor_row == 2
            assert loaded_frame.cursor_col == 7
            assert loaded_frame.count_occupied() == 3
            assert loaded_frame.get_cell(2, 5).peg.symbol == "7"
            assert loaded_frame.get_cell(2, 6).peg.symbol == "+"
            assert loaded_frame.get_cell(2, 7).peg.symbol == "3"
            assert loaded_meta.get("title") == "Lesson 1"

    def test_malformed_json_handling(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "bad.tframe")
            with open(filepath, "w") as f:
                f.write("{ invalid json content ...")

            with pytest.raises(InvalidTFrameError):
                TFrameStorage.load(filepath)

    def test_invalid_format_name(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "wrong_fmt.tframe")
            with open(filepath, "w") as f:
                json.dump({"format_name": "UnknownFormat", "format_version": "1.0.0"}, f)

            with pytest.raises(InvalidTFrameError) as exc_info:
                TFrameStorage.load(filepath)
            assert "Invalid format identifier" in str(exc_info.value)

    def test_incompatible_major_version(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "future_version.tframe")
            with open(filepath, "w") as f:
                json.dump({
                    "format_name": "TaylorFrame",
                    "format_version": "2.0.0",
                    "dimensions": {"rows": 10, "columns": 10},
                    "cells": [],
                }, f)

            with pytest.raises(IncompatibleVersionError):
                TFrameStorage.load(filepath)

    def test_text_exporter(self):
        frame = TaylorFrame(rows=10, cols=10)
        frame.place_peg(1, 1, TaylorPeg.from_symbol("7"))
        frame.place_peg(1, 2, TaylorPeg.from_symbol("+"))
        frame.place_peg(1, 3, TaylorPeg.from_symbol("3"))

        text = TextExporter.export_text(frame)
        assert "VIRTUAL TAYLOR FRAME" in text
        assert "Row  2:" in text
        assert "7" in text
        assert "Total Objects Placed: 3" in text

    def test_json_exporter(self):
        frame = TaylorFrame(rows=10, cols=10)
        frame.place_peg(0, 0, TaylorPeg.from_symbol("x"))

        json_str = JSONExporter.export_json(frame)
        data = json.loads(json_str)
        assert data["occupied_count"] == 1
        assert data["cells"][0]["symbol"] == "x"
        assert data["cells"][0]["type"] == "ALGEBRAIC"
