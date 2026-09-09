from pathlib import Path
from logsight.analyzer import analyze_records
from logsight.parser import parser_line

log_path = Path(__file__).parent / "sample_data" / "access.log"
records = []

with log_path.open(encoding="utf-8") as file:
    for line in file:
        result = parser_line(line)

        if result is not None:
            records.append(result)

summary = analyze_records(records)

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