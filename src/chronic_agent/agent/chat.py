from __future__ import annotations

from collections.abc import Sequence

from chronic_agent.platform.settings import settings


class ChatAgent:
    def reply(self, user_message: str, recent_messages: Sequence[tuple[str, str]], extra_context: str = '') -> str:
        if settings.enable_fake_llm:
            return self._fake_reply(user_message, recent_messages, extra_context)
        return self._fake_reply(user_message, recent_messages, extra_context)

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
