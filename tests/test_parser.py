from logsight.parser import parser_line, parse_nginx_line

def test_parse_valid_line():
    line = "2026-09-08T14:32:10 192.168.1.10 GET /api/users 200 0.083"

    result = parser_line(line)

    assert result is not None
    assert result["ip"] == "192.168.1.10"
    assert result["method"] == "GET"
    assert result["path"] == "/api/users"
    assert result["status"] == 200
    assert result["response_time"] == 0.083


def test_parse_wrong_field_count():
    result = parser_line("这是一行错误的日志")

    assert result is None


def test_parse_invalid_numbers():
    line = "2026-09-08T14:32:10 192.168.1.10 GET /api/users error unknown"

    result = parser_line(line)

    assert result is None

def test_parse_valid_nginx_line():
    line = (
        '192.168.1.10 - - [09/Sep/2026:20:15:30 +0800] '
        '"GET /api/users HTTP/1.1" 200 512 '
        '"https://example.com/" "Mozilla/5.0"'
    )

    result = parse_nginx_line(line)

    assert result is not None
    assert result["ip"] == "192.168.1.10"
    assert result["method"] == "GET"
    assert result["path"] == "/api/users"
    assert result["protocol"] == "HTTP/1.1"
    assert result["status"] == 200
    assert result["response_size"] == 512
    assert result["referer"] == "https://example.com/"
    assert result["user_agent"] == "Mozilla/5.0"


def test_parse_invalid_nginx_line():
    result = parse_nginx_line("这是一行损坏的日志")

    assert result is None