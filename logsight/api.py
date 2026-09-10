from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field

from logsight.analyzer import analyze_records
from logsight.parser import parser_line, parse_nginx_line


app = FastAPI(
    title="Log-Sight API",
    version="0.1.0",
    description="Web 服务访问日志分析接口",
)


class AnalyzeRequest(BaseModel):
    """日志分析请求。"""

    log_format: Literal["simple", "nginx"] = "nginx"
    lines: list[str] = Field(min_length=1, max_length=10_000)


@app.get("/health")
def health() -> dict[str, str]:
    """检查服务是否正常运行。"""
    return {"status": "ok"}


@app.post("/analyze")
def analyze_logs(request: AnalyzeRequest) -> dict:
    """解析日志并返回统计结果。"""
    if request.log_format == "nginx":
        line_parser = parse_nginx_line
    else:
        line_parser = parser_line

    records = []
    invalid_lines = 0

    for line in request.lines:
        record = line_parser(line)

        if record is None:
            invalid_lines += 1
        else:
            records.append(record)

    summary = analyze_records(records)

    return {
        "log_format": request.log_format,
        "valid_lines": len(records),
        "invalid_lines": invalid_lines,
        "summary": summary,
    }