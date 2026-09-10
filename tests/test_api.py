from fastapi.testclient import TestClient
from openai import OpenAIError

from logsight.api import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_nginx_logs():
    response = client.post(
        "/analyze",
        json={
            "log_format": "nginx",
            "lines": [
                (
                    '192.168.1.10 - - '
                    '[09/Sep/2026:20:15:30 +0800] '
                    '"GET /api/users HTTP/1.1" 200 512 '
                    '"-" "Mozilla/5.0"'
                ),
                (
                    '192.168.1.11 - - '
                    '[09/Sep/2026:20:15:31 +0800] '
                    '"GET /api/orders HTTP/1.1" 500 64 '
                    '"-" "curl/8.0"'
                ),
                "这是一行损坏的日志",
            ],
        },
    )

    assert response.status_code == 200

    result = response.json()
    assert result["anomalies"] == [
        {
            "type": "high_server_error_rate",
            "severity": "high",
            "value": 0.5,
            "threshold": 0.1,
        }
    ]
    assert result["valid_lines"] == 2
    assert result["invalid_lines"] == 1
    assert result["summary"]["total_requests"] == 2
    assert result["summary"]["status_counts"] == {
        "200": 1,
        "500": 1,
    }
    assert result["summary"]["server_error_rate"] == 0.5
    assert len(result["anomalies"]) == 1
    assert result["anomalies"][0]["type"] == "high_server_error_rate"
    assert result["anomalies"][0]["value"] == 0.5


def test_rejects_unknown_log_format():
    response = client.post(
        "/analyze",
        json={
            "log_format": "unknown",
            "lines": ["some log"],
        },
    )

    assert response.status_code == 422


def test_rejects_empty_lines():
    response = client.post(
        "/analyze",
        json={
            "log_format": "nginx",
            "lines": [],
        },
    )

    assert response.status_code == 422

def test_analyze_can_include_llm_report(monkeypatch):
    def fake_generate_report(
        summary: dict,
        anomalies: list[dict],
    ) -> str:
        assert summary["total_requests"] == 1
        assert len(anomalies) == 2
        return "这是一份模拟的日志分析报告"

    monkeypatch.setattr(
        "logsight.api.generate_report",
        fake_generate_report,
    )

    response = client.post(
        "/analyze",
        json={
            "log_format": "simple",
            "include_report": True,
            "lines": [
                (
                    "192.168.1.10 "
                    "2026-09-10T12:00:00 "
                    "GET /api/users 500 1.2"
                )
            ],
        },
    )

    assert response.status_code == 200
    assert response.json()["report"] == (
        "这是一份模拟的日志分析报告"
    )


def test_analyze_reports_missing_llm_config(monkeypatch):
    def fake_generate_report(
        summary: dict,
        anomalies: list[dict],
    ) -> str:
        raise RuntimeError(
            "缺少环境变量 LOGSIGHT_LLM_API_KEY"
        )

    monkeypatch.setattr(
        "logsight.api.generate_report",
        fake_generate_report,
    )

    response = client.post(
        "/analyze",
        json={
            "log_format": "simple",
            "include_report": True,
            "lines": [
                (
                    "192.168.1.10 "
                    "2026-09-10T12:00:00 "
                    "GET /health 200 0.1"
                )
            ],
        },
    )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "缺少环境变量 LOGSIGHT_LLM_API_KEY"
    )


def test_analyze_reports_llm_connection_failure(monkeypatch):
    def fake_generate_report(
        summary: dict,
        anomalies: list[dict],
    ) -> str:
        raise OpenAIError("connection failed")

    monkeypatch.setattr(
        "logsight.api.generate_report",
        fake_generate_report,
    )

    response = client.post(
        "/analyze",
        json={
            "log_format": "simple",
            "include_report": True,
            "lines": [
                (
                    "192.168.1.10 "
                    "2026-09-10T12:00:00 "
                    "GET /health 200 0.1"
                )
            ],
        },
    )

    assert response.status_code == 502
    assert response.json()["detail"] == (
        "LLM 服务暂时不可用"
    )
