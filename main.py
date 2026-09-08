from pathlib import Path
from logsight.parser import parser_line

log_path = Path(__file__).parent / "sample_data" / "access.log"

with log_path.open(encoding="utf-8") as file:
    for line in file:
        result = parser_line(line)
        print(result)