from __future__ import annotations

import logging
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Optional

import httpx

from chronic_agent.platform.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class LLMParams:
    api_key: str = ''
    base_url: str = ''
    model: str = 'gpt-4o-mini'


SYSTEM_PROMPT = (
    '你是一位慢性病管理 AI 助手 (CarePilot)，专注于中国大陆 2 型糖尿病合并高血压患者的日常健康管理。'
    '请从以下五个维度给出简洁、专业且友好的建议：控糖、控压、依从性、饮食和复诊准备。'
    '回复必须使用简体中文，并在必要时引用患者的最新监测数据来佐证你的分析。'
    '如果信息不足，主动引导患者补充今日血糖、血压、饮食或服药情况。'
)


class ChatAgent:
    """Wraps both real LLM calls and a rule-based fallback."""

    def reply(
        self,
        user_message: str,
        recent_messages: Sequence[tuple[str, str]],
        extra_context: str = '',
        llm_params: Optional[LLMParams] = None,
    ) -> str:
        params = llm_params or LLMParams()

        # Decide whether to call the real LLM
        use_real = bool(params.api_key and params.base_url and not settings.enable_fake_llm)

        if use_real:
            try:
                return self._real_llm_call(user_message, recent_messages, extra_context, params)
            except Exception as exc:
                logger.warning('LLM call failed, falling back to rules: %s', exc)
                return f'[LLM 调用失败: {exc}]\n\n' + self._fake_reply(user_message, recent_messages, extra_context)

        return self._fake_reply(user_message, recent_messages, extra_context)

    # ── Real LLM Call (OpenAI-Compatible) ─────────────────────
    def _real_llm_call(
        self,
        user_message: str,
        recent_messages: Sequence[tuple[str, str]],
        extra_context: str,
        params: LLMParams,
    ) -> str:
        messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]

        # Inject recent conversation history
        for role, content in recent_messages[-6:]:
            messages.append({'role': role, 'content': content})

        # Inject extra context as a system hint
        if extra_context:
            messages.append({'role': 'system', 'content': f'以下是患者的当前健康概览，请结合此信息回复：{extra_context}'})

        messages.append({'role': 'user', 'content': user_message})

        # Build the API endpoint
        base = params.base_url.rstrip('/')
        # Support both "/v1" style and direct base URL
        if not base.endswith('/v1') and not base.endswith('/chat/completions'):
            url = f'{base}/v1/chat/completions'
        elif base.endswith('/v1'):
            url = f'{base}/chat/completions'
        else:
            url = base

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {params.api_key}',
        }

        payload = {
            'model': params.model,
            'messages': messages,
            'temperature': 0.7,
            'max_tokens': 1024,
        }

        logger.info('Calling LLM: %s model=%s', url, params.model)

        with httpx.Client(timeout=60.0) as client:
            resp = client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        return data['choices'][0]['message']['content'].strip()

    # ── Rule-Based Fallback ───────────────────────────────────
    def _fake_reply(self, user_message: str, recent_messages: Sequence[tuple[str, str]], extra_context: str = '') -> str:
        prefix = '我会从控糖、控压、依从性、饮食和复诊准备角度给你建议。'
        if '总结' in user_message or '复诊' in user_message:
            return f"{prefix}\n你已经接近需要门诊摘要的场景，建议生成 previsit digest，并重点核对最近 7 到 14 天的血糖、血压、漏药和高风险饮食。\n{extra_context}".strip()
        if '血糖' in user_message:
            return f"{prefix}\n血糖管理重点是区分空腹和餐后模式，并结合晚餐结构、夜间加餐和漏服降糖药来判断。\n{extra_context}".strip()
        if '血压' in user_message:
            return f"{prefix}\n血压管理请优先关注晨间血压、盐摄入、睡眠不足和是否规律服用降压药。\n{extra_context}".strip()
        if any(k in user_message for k in ['吃', '饮食', '奶茶', '火锅', '外卖']):
            return f"{prefix}\n饮食管理建议优先减少高糖饮料、主食过量和高盐外卖，并尽量把餐次记录得更具体。\n{extra_context}".strip()
        if '药' in user_message or '提醒' in user_message:
            return f"{prefix}\n请结合今日提醒和服药计划，核对是否存在漏服、错时服药或连续跳过的情况。\n{extra_context}".strip()
        if recent_messages:
            return f"{prefix}\n我已结合你最近的记录继续跟进。当前更建议补齐今天的血糖、血压、饮食或服药执行情况。\n{extra_context}".strip()
        return f"{prefix}\n你可以直接提问，也可以用 [TRACK] 记录血糖、血压、饮食、症状或体重。\n{extra_context}".strip()
