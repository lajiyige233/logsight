def analyze_records(records: list[dict]) -> dict:
    """统计请求总数、状态码分布和错误率。"""
    status_counts = {}
    endpoint_counts = {}
    ip_counts = {}

    for record in records:
        status = record["status"]
        status_counts[status] = status_counts.get(status, 0) + 1

        method = record["method"]
        path = record["path"].split("?", 1)[0]
        endpoint = f"{method} {path}"

        endpoint_counts[endpoint] = endpoint_counts.get(endpoint, 0) + 1

        ip = record["ip"]
        ip_counts[ip] = ip_counts.get(ip, 0) + 1
    total_requests = len(records)

    client_error_count = sum(
        count
        for status, count in status_counts.items()
        if 400 <= status < 500
    )

    server_error_count = sum(
        count
        for status, count in status_counts.items()
        if 500 <= status < 600
    )

    top_endpoints = sorted(
        endpoint_counts.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:5]

    top_ips = sorted(
        ip_counts.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:5]

    if total_requests == 0:
        client_error_rate = 0.0
        server_error_rate = 0.0
    else:
        client_error_rate = client_error_count / total_requests
        server_error_rate = server_error_count / total_requests

    return {
        "total_requests": total_requests,
        "status_counts": status_counts,
        "client_error_rate": client_error_rate,
        "server_error_rate": server_error_rate,
        "top_endpoints": top_endpoints,
        "top_ips": top_ips,
    }