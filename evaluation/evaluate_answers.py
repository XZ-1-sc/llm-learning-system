import argparse
import json
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel

from backend.knowledge import KNOWLEDGE_PASSAGES
from backend.rag_answer import (
    RagModelNotConfiguredError,
    RagModelResponseError,
    answer_from_knowledge,
)
from backend.schemas import RagAnswerRead


class AnswerCase(BaseModel):
    id: str
    question: str
    search_query: str
    expected_status: Literal["answered", "insufficient_evidence"]
    expected_passage_ids: list[str]
    expected_keyword_groups: list[list[str]]


def load_cases() -> list[AnswerCase]:
    records = json.loads(Path(__file__).with_name("answer_cases.json").read_text(encoding="utf-8"))
    cases = [AnswerCase.model_validate(record) for record in records]
    known_ids = {passage.id for passage in KNOWLEDGE_PASSAGES}
    for case in cases:
        unknown = set(case.expected_passage_ids) - known_ids
        if unknown:
            raise ValueError(f"样例 {case.id} 引用了未知片段 {sorted(unknown)}")
    return cases


def grade_answer(case: AnswerCase, result: RagAnswerRead) -> list[str]:
    issues = []
    if result.status != case.expected_status:
        issues.append(f"回答状态为 {result.status}，预期 {case.expected_status}")

    actual_ids = {citation.passage_id for citation in result.citations}
    expected_ids = set(case.expected_passage_ids)
    if actual_ids != expected_ids:
        issues.append(f"缺少引用 {sorted(expected_ids - actual_ids)}，额外引用 {sorted(actual_ids - expected_ids)}")

    text = result.answer.casefold()
    missing = [
        group
        for group in case.expected_keyword_groups
        if not any(phrase.casefold() in text for phrase in group)
    ]
    if missing:
        issues.append(f"缺少答案要点（每组接受任一表述）{missing}")
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="检查 RAG 回答状态、引用和答案要点")
    parser.add_argument("--live", action="store_true", help="使用本地配置调用真实模型")
    options = parser.parse_args(argv)
    cases = load_cases()
    if not options.live:
        print(f"已校验 {len(cases)} 个问答样例。添加 --live 可运行真实模型评测。")
        return 0

    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    passed = 0
    for case in cases:
        try:
            result = answer_from_knowledge(case.question, case.search_query)
        except RagModelNotConfiguredError:
            print("模型未配置，请在 .env 中填写 OPENAI_API_KEY 和 OPENAI_MODEL。")
            return 1
        except RagModelResponseError:
            print(f"失败 {case.id} | 模型请求失败或返回无效引用")
            continue

        issues = grade_answer(case, result)
        if issues:
            print(f"失败 {case.id} | {'，'.join(issues)}")
        else:
            passed += 1
            print(f"通过 {case.id}")

    print(f"问答检查通过 {passed}/{len(cases)}")
    return int(passed != len(cases))


if __name__ == "__main__":
    raise SystemExit(main())
