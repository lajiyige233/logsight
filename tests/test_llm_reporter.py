from types import SimpleNamespace
from unittest.mock import MagicMock

from logsight.llm_config import LLMConfig
from logsight.llm_reporter import (
    SYSTEM_PROMPT,
    build_user_prompt,
    generate_report,
)


def test_build_user_prompt_contains_analysis_data():
    prompt = build_user_prompt(
        summary={"total_requests": 2},
        anomalies=[{"type": "slow_requests"}],
    )

    assert '"total_requests": 2' in prompt
    assert '"type": "slow_requests"' in prompt


def test_generate_report_uses_configured_client():
    response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content=" 测试分析报告 "
                )
            )
        ]
    )

    client = MagicMock()
    client.chat.completions.create.return_value = response

    config = LLMConfig(
        base_url="http://localhost:11434/v1",
        api_key="test-key",
        model="test-model",
        timeout_seconds=60,
    )

    report = generate_report(
        summary={"total_requests": 2},
        anomalies=[],
        config=config,
        client=client,
    )

    assert report == "测试分析报告"

    request = client.chat.completions.create.call_args.kwargs

    assert request["model"] == "test-model"
    assert request["messages"][0] == {
        "role": "system",
        "content": SYSTEM_PROMPT,
    }
    assert request["messages"][1]["role"] == "user"