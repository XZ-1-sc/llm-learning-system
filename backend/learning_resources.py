from backend.schemas import LearningResourceRead


PYTHON_LISTS = LearningResourceRead(
    topic="python",
    title="Python 教程：列表",
    publisher="Python 官方文档",
    source_url="https://docs.python.org/zh-cn/3.10/tutorial/datastructures.html#more-on-lists",
    summary="了解如何添加和删除列表元素，再用 len() 检查列表长度的变化。",
)
LLM_CONTEXT = LearningResourceRead(
    topic="llm",
    title="提示词工程：提供相关上下文",
    publisher="OpenAI 官方文档",
    source_url="https://developers.openai.com/api/docs/guides/prompt-engineering#include-relevant-context-information",
    summary="学习如何在请求中提供背景资料，让模型据此回答问题。",
)
RAG_OVERVIEW = LearningResourceRead(
    topic="rag",
    title="什么是检索增强生成（RAG）？",
    publisher="Google Cloud",
    source_url="https://cloud.google.com/use-cases/retrieval-augmented-generation?hl=zh-cn",
    summary="了解怎样先从外部资料中检索信息，再用检索结果辅助模型生成回答。",
)

LEARNING_RESOURCES = (PYTHON_LISTS, LLM_CONTEXT, RAG_OVERVIEW)


def matches_keywords(terms: list[str], *fields: str) -> bool:
    searchable_text = " ".join(fields).casefold()
    return bool(terms) and all(term in searchable_text for term in terms)


def find_learning_resources(search_query: str) -> list[LearningResourceRead]:
    terms = search_query.casefold().split()
    return [
        resource
        for resource in LEARNING_RESOURCES
        if matches_keywords(terms, resource.topic, resource.title, resource.publisher, resource.summary)
    ]
