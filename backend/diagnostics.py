from collections.abc import Mapping

QUESTIONS = {
    "python_list": {
        "topic": "python",
        "prompt": "在 Python 中，len([10, 20, 30]) 返回什么？",
        "options": {"A": "2", "B": "3", "C": "60"},
        "correct_answer": "B",
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