from logsight.detector import detect_anomalies


def test_empty_records_have_no_anomalies():
    assert detect_anomalies([]) == []


def test_detects_high_server_error_rate():
    records = [
        {"status": 200, "ip": "192.168.1.1"},
        {"status": 500, "ip": "192.168.1.2"},
    ]

    anomalies = detect_anomalies(
        records,
        server_error_rate_threshold=0.5,
    )

    anomaly = next(
        item for item in anomalies
        if item["type"] == "high_server_error_rate"
    )

    assert anomaly["severity"] == "high"
    assert anomaly["value"] == 0.5


def test_detects_slow_requests():
    records = [
        {
            "status": 200,
            "ip": "192.168.1.1",
            "response_time": 0.2,
        },
        {
            "status": 200,
            "ip": "192.168.1.2",
            "response_time": 1.5,
        },
    ]

    anomalies = detect_anomalies(
        records,
        slow_response_time_threshold=1.0,
    )

    anomaly = next(
        item for item in anomalies
        if item["type"] == "slow_requests"
    )

    assert anomaly["count"] == 1
    assert anomaly["threshold_seconds"] == 1.0


def test_detects_high_frequency_ip():
    records = [
        {"status": 200, "ip": "192.168.1.1"},
        {"status": 200, "ip": "192.168.1.1"},
        {"status": 200, "ip": "192.168.1.2"},
    ]

    anomalies = detect_anomalies(
        records,
        ip_request_count_threshold=2,
    )

    anomaly = next(
        item for item in anomalies
        if item["type"] == "high_frequency_ip"
    )

    assert anomaly["ip"] == "192.168.1.1"
    assert anomaly["count"] == 2