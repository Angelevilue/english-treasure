"""
LangChain + DeepSeek 语法分析链

功能：
1. 语法成分标注（主谓宾定状补、从句类型）
2. 语法错误批改（标注错误 + 修改建议 + 解释）
"""

from __future__ import annotations

import json

from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.core.config import settings

# ── System Prompts ──

GRAMMAR_ANALYZE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """你是一位资深的英语语法教师。用户会输入一个英文句子，请对该句子进行详细的语法成分分析。

要求：
1. 标注主谓宾定状补等核心成分
2. 识别从句类型（定语从句、状语从句、名词性从句等）
3. 标注时态和语态
4. 对复杂结构给出解释

请以 JSON 格式返回，结构如下：
{{
  "original": "原句",
  "translation": "中文翻译",
  "components": [
    {{"text": "成分文本", "role": "主语/谓语/宾语/定语/状语/补语", "explanation": "说明"}}
  ],
  "clauses": [
    {{"type": "从句类型", "text": "从句文本", "function": "功能说明"}}
  ],
  "tense": "时态",
  "voice": "主动/被动",
  "notes": ["注意事项", "语法要点"]
}}"""),
    ("human", "{input_text}"),
])

GRAMMAR_CORRECT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """你是一位严谨的英语写作批改老师。用户会输入一段英文写作，请找出所有语法错误并提供修改建议。

请以 JSON 格式返回，结构如下：
{{
  "original": "原文",
  "errors": [
    {{
      "position": "错误位置（片段）",
      "type": "错误类型（主谓一致/时态/冠词/介词/拼写/句式等）",
      "explanation": "错误原因",
      "correction": "修改建议",
      "corrected_text": "修正后的完整片段"
    }}
  ],
  "overall_score": 85,
  "summary": "总体评价与改进方向"
}}"""),
    ("human", "{input_text}"),
])


# ── LLM 实例（懒加载） ──

_llm: ChatDeepSeek | None = None


def _get_llm() -> ChatDeepSeek:
    global _llm
    if _llm is None:
        _llm = ChatDeepSeek(
            model=settings.DEEPSEEK_MODEL,
            api_key=settings.DEEPSEEK_API_KEY,
            api_base=settings.DEEPSEEK_BASE_URL,
            temperature=0.3,
            extra_body={"thinking": {"type": "disabled"}},
        )
    return _llm


# ── 链 ──

def create_analysis_chain():
    """创建语法分析链"""
    return GRAMMAR_ANALYZE_PROMPT | _get_llm() | StrOutputParser()


def create_correction_chain():
    """创建语法纠错链"""
    return GRAMMAR_CORRECT_PROMPT | _get_llm() | StrOutputParser()


async def analyze_grammar(text: str) -> dict:
    """语法成分分析"""
    chain = create_analysis_chain()
    result = await chain.ainvoke({"input_text": text})
    try:
        return json.loads(result)
    except json.JSONDecodeError:
        return {"original": text, "raw_output": result, "parse_error": True}


async def correct_grammar(text: str) -> dict:
    """语法纠错批改"""
    chain = create_correction_chain()
    result = await chain.ainvoke({"input_text": text})
    try:
        return json.loads(result)
    except json.JSONDecodeError:
        return {"original": text, "raw_output": result, "parse_error": True}
