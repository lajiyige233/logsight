import argparse
from pathlib import Path

from logsight.analyzer import analyze_records
from logsight.parser import parser_line, parse_nginx_line
from logsight.detector import detect_anomalies


def load_records(log_path: Path, log_format: str) -> list[dict]:
    """读取日志文件，并返回成功解析的记录。"""
    if log_format == "nginx":
        line_parser = parse_nginx_line
    else:
        line_parser = parser_line

    records = []

    with log_path.open(encoding="utf-8") as file:
        for line in file:
            record = line_parser(line)

            if record is not None:
                records.append(record)

    return records


def print_summary(summary: dict) -> None:
    """在终端输出分析结果。"""
    print("有效请求总数：", summary["total_requests"])
    print("状态码分布：", summary["status_counts"])
    print("4xx 错误率：", f"{summary['client_error_rate']:.2%}")
    print("5xx 错误率：", f"{summary['server_error_rate']:.2%}")

    print("访问量最高的接口：")
    for endpoint, count in summary["top_endpoints"]:
        print(f"  {endpoint}: {count} 次")

    print("请求次数最多的 IP：")
    for ip, count in summary["top_ips"]:
        print(f"  {ip}: {count} 次")


def print_anomalies(anomalies: list[dict]) -> None:
    """在终端输出异常检测结果。"""
    print("异常检测结果：")

    if not anomalies:
        print("  未发现异常")
        return

    for anomaly in anomalies:
        anomaly_type = anomaly["type"]

        if anomaly_type == "high_server_error_rate":
            print(
                "  [高] 5xx 错误率过高："
                f"{anomaly['value']:.2%}"
            )

        elif anomaly_type == "slow_requests":
            print(
                "  [中] 检测到慢请求："
                f"{anomaly['count']} 条"
            )

        elif anomaly_type == "high_frequency_ip":
            print(
                "  [中] IP 请求次数过多："
                f"{anomaly['ip']}，共 {anomaly['count']} 次"
            )


def main(argv: list[str] | None = None) -> None:
    """处理命令行参数并运行日志分析。"""
    argument_parser = argparse.ArgumentParser(
        description="分析 Web 服务访问日志"
    )

    argument_parser.add_argument(
        "log_file",
        type=Path,
        help="需要分析的日志文件路径",
    )

    argument_parser.add_argument(
        "--format",
        dest="log_format",
        choices=("simple", "nginx"),
        default="nginx",
        help="日志格式，默认为 nginx",
    )

    args = argument_parser.parse_args(argv)

    if not args.log_file.is_file():
        argument_parser.error(f"找不到日志文件：{args.log_file}")

    records = load_records(args.log_file, args.log_format)
    summary = analyze_records(records)
    anomalies = detect_anomalies(records)

    print_summary(summary)
    print_anomalies(anomalies)
