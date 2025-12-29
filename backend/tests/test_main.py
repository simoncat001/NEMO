"""
Basic API tests
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root():
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200
    assert "NEMO FastAPI Backend" in response.json()["message"]


def test_health_check():
    """测试健康检查"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_docs():
    """测试 API 文档可访问"""
    response = client.get("/api/v1/docs")
    assert response.status_code == 200


# 更多测试待添加...
