"""
Shared test fixtures for CLI tests.
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner


@pytest.fixture
def runner():
    """Typer CliRunner for testing CLI commands."""
    return CliRunner()


@pytest.fixture
def tmp_skills_dir():
    """Temporary directory that mimics a skills/ tree."""
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture
def app():
    """Import and return the Typer app.

    Ensures src/ is on sys.path so hermes_agent_skills can be imported.
    """
    # Point to the src/ directory
    src_dir = Path(__file__).parent.parent.parent / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    from cli.main import app
    return app
