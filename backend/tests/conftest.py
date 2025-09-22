"""
Pytest configuration and fixtures for MCU-Copilot tests
"""

import pytest
import os
import sys
from pathlib import Path
from httpx import AsyncClient
from fastapi.testclient import TestClient

# Add the parent directory to Python path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.main import app

@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)

@pytest.fixture
def async_client():
    """Create a test client for the FastAPI app (using sync TestClient for simplicity)"""
    return TestClient(app)

@pytest.fixture
def sample_requirements():
    """Sample requirements for testing NL to Assembly functionality"""
    return [
        "控制P05引脚输出高电平，点亮LED",
        "让P03引脚的LED闪烁",
        "读取P01引脚的按键状态",
        "设置P07引脚为输入模式",
    ]

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing"""
    # Mock API keys for testing - use real ones if available, fallback to test values
    import os
    monkeypatch.setenv("QIANWEN_APIKEY", os.getenv("QIANWEN_APIKEY", "test-qianwen-key"))
    monkeypatch.setenv("GEMINI_APIKEY", os.getenv("GEMINI_APIKEY", "test-gemini-key"))
    monkeypatch.setenv("JWT_SECRET_KEY", os.getenv("JWT_SECRET_KEY", "test-secret-key-that-is-long-enough"))
    monkeypatch.setenv("API_TOKEN", os.getenv("API_TOKEN", "test-api-token"))

@pytest.fixture
def auth_headers():
    """Create authentication headers for testing"""
    # Use the default API token or get from environment
    import os
    api_token = os.getenv("API_TOKEN", "mcu-copilot-2025-seed-token")
    return {"Authorization": f"Bearer {api_token}"}

@pytest.fixture(scope="session")
def test_config():
    """Test configuration"""
    return {
        "timeout": 30,  # seconds
        "compilation_required": True,
        "min_assembly_lines": 5,
        "expected_instructions": ["LDINS", "ST", "JUMP", "JZ"]
    }