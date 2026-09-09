from logsight.analyzer import analyze_records


def test_analyze_records():
    records = [
        {
            "ip": "192.168.1.10",
            "method": "GET",
            "path": "/api/users",
            "status": 200,
        },
        {
            "ip": "192.168.1.10",
            "method": "GET",
            "path": "/api/users?limit=10",
            "status": 200,
        },
        {
            "ip": "192.168.1.10",
            "method": "POST",
            "path": "/api/login",
            "status": 404,
        },
        {
            "ip": "192.168.1.11",
            "method": "GET",
            "path": "/api/orders",
            "status": 500,
        },
    ]

    summary = analyze_records(records)

    assert summary["total_requests"] == 4
    assert summary["status_counts"] == {200: 2, 404: 1, 500: 1}
    assert summary["client_error_rate"] == 0.25
    assert summary["server_error_rate"] == 0.25
    assert summary["top_endpoints"][0] == ("GET /api/users", 2)
    assert summary["top_ips"][0] == ("192.168.1.10", 3)