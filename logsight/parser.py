def parser_line(line: str) -> dict | None:
    """解析一行访问日志，成功时返回字典，失败时返回 None。"""
    parts = line.split()

    if len(parts) != 6:
        return None

    try:
        status = int(parts[4])
        response_time = float(parts[5])
    except ValueError:
        return None

    return {
        "timestamp": parts[0],
        "ip": parts[1],
        "method": parts[2],
        "path": parts[3],
        "status": status,
        "response_time": response_time,
    }