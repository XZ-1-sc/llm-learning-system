import json
from pathlib import Path

from backend.knowledge import KNOWLEDGE_PASSAGES, find_knowledge_passages


def format_metric(matched: int, total: int) -> str:
    return f"{matched}/{total} ({matched / total:.1%})" if total else "无适用样本"


def main() -> None:
    cases = json.loads(Path(__file__).with_name("retrieval_cases.json").read_text(encoding="utf-8"))
    known_ids = {passage.id for passage in KNOWLEDGE_PASSAGES}
    relevant_count = 0
    retrieved_relevant_count = 0
    no_answer_count = 0
    correctly_empty_count = 0
    exact_count = 0

    for case in cases:
        expected = set(case["expected_passage_ids"])
        unknown = expected - known_ids
        if unknown:
            raise ValueError(f"样例 {case['id']} 引用了未知片段 {sorted(unknown)}")

        actual = {passage.id for passage in find_knowledge_passages(case["query"])}
        relevant_count += len(expected)
        retrieved_relevant_count += len(expected & actual)
        if not expected:
            no_answer_count += 1
            correctly_empty_count += int(not actual)

        if actual == expected:
            exact_count += 1
        else:
            print(f"{case['id']} | {case['query']} | 漏检 {sorted(expected - actual)} | 多返回 {sorted(actual - expected)}")

    print(f"片段召回率 {format_metric(retrieved_relevant_count, relevant_count)}")
    print(f"无答案正确返回空列表 {format_metric(correctly_empty_count, no_answer_count)}")
    print(f"用例完全匹配 {format_metric(exact_count, len(cases))}")


if __name__ == "__main__":
    main()
