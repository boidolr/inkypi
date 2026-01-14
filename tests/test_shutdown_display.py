import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add src directory to path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))


class TestShutdownDisplay:
    """Test cases for display shutdown functionality."""

    def test_shutdown_script_exists(self):
        """Test that the shutdown script exists."""
        shutdown_script = Path(__file__).parent.parent / "src" / "shutdown_display.py"
        assert shutdown_script.exists(), "Shutdown script should exist"
        
    def test_shutdown_bash_script_exists(self):
        """Test that the shutdown bash script exists."""
        shutdown_script = Path(__file__).parent.parent / "install" / "shutdown_display.sh"
        assert shutdown_script.exists(), "Shutdown bash script should exist"

    def test_service_file_has_exec_stop(self):
        """Test that the service file includes ExecStop directive."""
        service_file = Path(__file__).parent.parent / "install" / "inkypi.service"
        assert service_file.exists(), "Service file should exist"
        
        content = service_file.read_text()
        assert "ExecStop=" in content, "Service file should have ExecStop directive"
        assert "shutdown_display.sh" in content, "ExecStop should call shutdown_display.sh"
        
    def test_service_file_has_timeout(self):
        """Test that the service file includes TimeoutStopSec."""
        service_file = Path(__file__).parent.parent / "install" / "inkypi.service"
        content = service_file.read_text()
        assert "TimeoutStopSec=" in content, "Service file should have TimeoutStopSec directive"
