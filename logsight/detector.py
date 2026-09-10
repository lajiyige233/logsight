from collections import Counter


def detect_anomalies(
    records: list[dict],
    server_error_rate_threshold: float = 0.1,
    slow_response_time_threshold: float = 1.0,
    ip_request_count_threshold: int = 100,
) -> list[dict]:
    """根据预设规则检测异常请求。"""
    if not records:
        return []

    anomalies = []
    total_requests = len(records)

    # 检测 5xx 服务端错误率
    server_error_count = sum(
        1 for record in records
        if 500 <= record["status"] < 600
    )
    server_error_rate = server_error_count / total_requests

    if server_error_rate >= server_error_rate_threshold:
        anomalies.append({
            "type": "high_server_error_rate",
            "severity": "high",
            "value": round(server_error_rate, 4),
            "threshold": server_error_rate_threshold,
        })

    # 检测响应过慢的请求
    slow_request_count = sum(
        1 for record in records
        if record.get("response_time") is not None
        and record["response_time"] > slow_response_time_threshold
    )

    if slow_request_count > 0:
        anomalies.append({
            "type": "slow_requests",
            "severity": "medium",
            "count": slow_request_count,
            "threshold_seconds": slow_response_time_threshold,
        })

    # 检测请求次数过多的 IP
    ip_counts = Counter(record["ip"] for record in records)

    for ip, count in ip_counts.items():
        if count >= ip_request_count_threshold:
            anomalies.append({
                "type": "high_frequency_ip",
                "severity": "medium",
                "ip": ip,
                "count": count,
                "threshold": ip_request_count_threshold,
            })

    return anomalies