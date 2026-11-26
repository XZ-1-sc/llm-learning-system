from backend.learning_resources import LLM_CONTEXT, PYTHON_LISTS, RAG_OVERVIEW, matches_keywords
from backend.schemas import KnowledgePassageRead


KNOWLEDGE_PASSAGES = (
    KnowledgePassageRead(
        id="python-list-append",
        text="列表的 append() 方法把一个对象放到列表末尾，直接修改原列表。"
             "如果对三元素列表调用一次 append()，再次用 len() 检查时会得到四。",
        source=PYTHON_LISTS,
    ),
    KnowledgePassageRead(
        id="llm-context-window",
        text="可以把项目说明和问题放在同一次模型请求中，让模型根据项目说明作答。"
             "上下文窗口以 token 计量，可容纳的内容有限，挑选与当前问题相关的段落更有用。",
        source=LLM_CONTEXT,
    ),
    KnowledgePassageRead(
        id="rag-retrieval-and-generation",
        text="RAG 先在知识库等外部来源检索相关段落，再把检索到的内容作为上下文交给模型生成回答。"
             "检索质量会影响回答，选错资料时，模型即使引用了资料也可能答非所问。",
        source=RAG_OVERVIEW,
    ),
)


def find_knowledge_passages(search_query: str) -> list[KnowledgePassageRead]:
    terms = search_query.casefold().split()
    return [
        passage
        for passage in KNOWLEDGE_PASSAGES
        if matches_keywords(terms, passage.source.topic, passage.source.title, passage.text)
    ]
