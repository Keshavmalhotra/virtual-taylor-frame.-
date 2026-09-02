"""
Unit tests for CLI parsing and main bootstrap.
"""
import pytest
from unittest.mock import patch
from virtual_taylor_frame.main import parse_args


def test_cli_defaults():
    with patch("sys.argv", ["main.py"]):
        args = parse_args()
        assert args.rows == 20
        assert args.cols == 30
        assert args.verbosity == "normal"
        assert args.no_audio is False


def test_cli_custom_args():
    with patch("sys.argv", ["main.py", "my_file.tframe", "--rows", "15", "--cols", "25", "--verbosity", "detailed", "--no-audio"]):
        args = parse_args()
        assert args.file == "my_file.tframe"
        assert args.rows == 15
        assert args.cols == 25
        assert args.verbosity == "detailed"
        assert args.no_audio is True
