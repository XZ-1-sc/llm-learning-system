from collections.abc import Mapping
from typing import TypedDict

from backend.schemas import LearningTopic


class DiagnosticQuestion(TypedDict):
    topic: LearningTopic
    prompt: str
    options: dict[str, str]
    correct_answer: str
    study_tip: str


QUESTIONS: dict[str, DiagnosticQuestion] = {
    "python_list": {
        "topic": "python",
        "prompt": "在 Python 中，len([10, 20, 30]) 返回什么？",
        "options": {"A": "2", "B": "3", "C": "60"},
        "correct_answer": "B",
        "study_tip": "Python：创建一个三元素列表，用 len() 检查长度，再追加一个元素并预测新长度。",
    },
    "llm_context": {
        "topic": "llm",
        "prompt": "怎样让模型在本次生成回答时参考一段项目说明？",
        "options": {
            "A": "提高回答的随机性",
            "B": "提高回答的长度上限",
            "C": "把项目说明放进本次请求的上下文",
        },
        "correct_answer": "C",
        "study_tip": "LLM：对同一个问题分别提供和省略项目说明，比较两次回答引用了哪些信息。",
    },
    "rag_retrieval": {
        "topic": "rag",
        "prompt": "在 RAG 流程中，检索步骤的作用是什么？",
        "options": {
            "A": "找到与问题相关的资料，供模型生成时参考",
            "B": "根据用户的问题重新训练模型",
            "C": "把模型已经生成的回答转换为向量",
        },
        "correct_answer": "A",
        "study_tip": "RAG：准备三段资料，挑出与问题最相关的一段，再用它作为回答依据。",
    },
}


def grade_diagnostic(answers: Mapping[str, str]) -> dict[str, int | list[str]]:
    missing = QUESTIONS.keys() - answers.keys()
    unknown = answers.keys() - QUESTIONS.keys()

    if missing or unknown:
        raise ValueError(f"缺少题号：{sorted(missing)}；未知题号：{sorted(unknown)}")

    incorrect_ids = [
        question_id
        for question_id, question in QUESTIONS.items()
        if answers[question_id] != question["correct_answer"]
    ]

    return {
        "score": len(QUESTIONS) - len(incorrect_ids),
        "total": len(QUESTIONS),
        "incorrect_question_ids": incorrect_ids,
    }


def recommend_study_tasks(
    incorrect_question_ids: list[str],
) -> list[tuple[str, tuple[LearningTopic, ...]]]:
    if not incorrect_question_ids:
        return [(
            "综合练习：选一段与问题相关的资料，将它放进模型请求，再核对回答是否有资料依据。",
            ("llm", "rag"),
        )]

    tasks = [
        (QUESTIONS[question_id]["study_tip"], (QUESTIONS[question_id]["topic"],))
        for question_id in dict.fromkeys(incorrect_question_ids)
        if question_id in QUESTIONS
    ]
    return tasks or [("这次诊断的错题暂无对应练习，请重新测验以获取学习建议。", ())]


def recommend_study(incorrect_question_ids: list[str]) -> list[str]:
    return [task for task, topics in recommend_study_tasks(incorrect_question_ids)]
