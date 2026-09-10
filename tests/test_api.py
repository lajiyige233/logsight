from fastapi.testclient import TestClient

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