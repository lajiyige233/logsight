from logsight.parser import parser_line


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