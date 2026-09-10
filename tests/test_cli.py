import pytest

from logsight.cli import main


def test_cli_analyzes_simple_log(tmp_path, capsys):
    log_file = tmp_path / "access.log"
    log_file.write_text(
        "2026-09-08T14:32:10 192.168.1.10 "
        "GET /api/users 200 0.083\n",
        encoding="utf-8",
    )

    main([str(log_file), "--format", "simple"])

    output = capsys.readouterr().out

    assert output.count("有效请求总数： 1") == 1
    assert "200: 1" in output
    assert "GET /api/users: 1 次" in output
    assert "192.168.1.10: 1 次" in output
    assert "异常检测结果：" in output
    assert "未发现异常" in output


def test_cli_rejects_missing_file(capsys):
    with pytest.raises(SystemExit) as error:
        main(["no_such_file.log", "--format", "nginx"])

    output = capsys.readouterr().err

    assert error.value.code == 2
    assert "找不到日志文件" in output
