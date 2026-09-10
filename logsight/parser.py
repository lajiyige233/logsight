import re
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

NGINX_LOG_PATTERN = re.compile(
    r"(?P<ip>\S+) - (?P<remote_user>\S+) "
    r"\[(?P<timestamp>[^\]]+)\] "
    r'"(?P<method>[A-Z]+) (?P<path>\S+) (?P<protocol>HTTP/\d(?:\.\d)?)" '
    r"(?P<status>\d{3}) (?P<response_size>\d+|-) "
    r'"(?P<referer>[^"]*)" "(?P<user_agent>[^"]*)"'
)


def parse_nginx_line(line: str) -> dict | None:
    """解析一行 Nginx access.log，格式错误时返回 None。"""
    match = NGINX_LOG_PATTERN.fullmatch(line.strip())

    if match is None:
        return None

    record = match.groupdict()
    status = int(record["status"])

    if not 100 <= status < 600:
        return None

    record["status"] = status

    if record["response_size"] == "-":
        record["response_size"] = None
    else:
        record["response_size"] = int(record["response_size"])

    return record