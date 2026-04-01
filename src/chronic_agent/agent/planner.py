from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional
import httpx

from chronic_agent.agent.chat import LLMParams
from chronic_agent.platform.settings import settings

logger = logging.getLogger(__name__)

PLANNER_SYSTEM_PROMPT = """你是一个专业的慢性病管理助手，能够理解用户意图并选择合适的工具来处理。
你面前有以下工具：
{tools_metadata}

请根据用户的输入，判断是否需要调用工具。
如果需要，请按以下JSON格式返回：
{{
  "thought": "你的思考过程",
  "name": "工具名称",
  "parameters": {{ "参数名": "参数值" }}
}}
如果不需要调用工具（即用户只是在闲聊或打招呼），请返回：
{{
  "thought": "这是一个普通对话",
  "name": null,
  "parameters": {{}}
}}
请只返回 JSON。
"""

class Planner:
    def plan(self, user_message: str, tools_metadata: List[Dict[str, Any]], llm_params: Optional[LLMParams] = None) -> Dict[str, Any]:
        params = llm_params or LLMParams()
        use_real = bool(params.api_key and params.base_url and not settings.enable_fake_llm)

        if use_real:
            try:
                return self._real_llm_plan(user_message, tools_metadata, params)
            except Exception as exc:
                logger.warning(f"LLM planning failed: {exc}")
                return self._rule_based_plan(user_message)
        else:
            return self._rule_based_plan(user_message)

    def _real_llm_plan(self, user_message: str, tools_metadata: List[Dict[str, Any]], params: LLMParams) -> Dict[str, Any]:
        prompt = PLANNER_SYSTEM_PROMPT.format(tools_metadata=json.dumps(tools_metadata, ensure_ascii=False, indent=2))
        
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_message}
        ]

        base = params.base_url.rstrip("/")
        if not base.endswith("/v1") and not base.endswith("/chat/completions"):
            url = f"{base}/v1/chat/completions"
        elif base.endswith("/v1"):
            url = f"{base}/chat/completions"
        else:
            url = base

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {params.api_key}",
        }
        payload = {
            "model": params.model,
            "messages": messages,
            "temperature": 0.1, # Keep it deterministic
            "response_format": { "type": "json_object" } if "gpt-4" in params.model or "gpt-3.5" in params.model else None
        }

        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"].strip()
            
            # Find JSON if not purely JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "{" in content:
                content = content[content.find("{"):content.rfind("}")+1]
            
            return json.loads(content)

    def _rule_based_plan(self, user_message: str) -> Dict[str, Any]:
        """Simple rule-based planner for demo fallout."""
        msg = user_message.lower()
        if any(k in msg for k in ["总结", "概览", "情况", "最近怎么样"]):
            return {"thought": "用户询问健康概览", "name": "get_today_overview", "parameters": {}}
        if any(k in msg for k in ["记录", "记录了", "血压", "血糖", "体重"]):
            return {"thought": "用户录入健康数据", "name": "record_health_event", "parameters": {"raw_text": user_message}}
        if any(k in msg for k in ["药", "服药", "添加药物"]):
            if "添加" in msg or "加" in msg:
                return {"thought": "用户想要添加药物", "name": None, "parameters": {}} # Needs LLM for parameter extraction
            return {"thought": "用户询问药物清单", "name": "list_medications", "parameters": {}}
        if any(k in msg for k in ["吃了", "吃晚饭", "饮食", "中午吃"]):
            return {"thought": "用户正在描述饮食", "name": "analyze_meal", "parameters": {"description": user_message}}
        if "时间线" in msg or "历史" in msg:
            return {"thought": "用户查看时间线", "name": "get_timeline", "parameters": {}}
        
        return {"thought": "简单闲聊", "name": None, "parameters": {}}
