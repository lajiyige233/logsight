import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class LLMConfig:
    """LLM 服务连接配置。"""

    base_url: str
    api_key: str
    model: str
    timeout_seconds: float


def load_llm_config() -> LLMConfig:
    """从环境变量或 .env 文件读取 LLM 配置。"""
    load_dotenv()

    base_url = os.getenv(
        "LOGSIGHT_LLM_BASE_URL",
        "https://api.openai.com/v1",
    )
    api_key = os.getenv("LOGSIGHT_LLM_API_KEY")
    model = os.getenv("LOGSIGHT_LLM_MODEL")
    timeout_seconds = float(
        os.getenv("LOGSIGHT_LLM_TIMEOUT_SECONDS", "60")
    )

    if not api_key:
        raise RuntimeError(
            "缺少环境变量 LOGSIGHT_LLM_API_KEY"
        )

    if not model:
        raise RuntimeError(
            "缺少环境变量 LOGSIGHT_LLM_MODEL"
        )

    return LLMConfig(
        base_url=base_url.rstrip("/"),
        api_key=api_key,
        model=model,
        timeout_seconds=timeout_seconds,
    )