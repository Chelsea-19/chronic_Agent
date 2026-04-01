from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
import httpx
import json

from sqlalchemy.orm import Session
from chronic_agent.agent.chat import ChatAgent, LLMParams, SYSTEM_PROMPT
from chronic_agent.agent.planner import Planner
from chronic_agent.agent.executor import Executor
from chronic_agent.agent.tool_registry import ToolRegistry
from chronic_agent.platform.settings import settings

logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self, db: Session, patient_id: int):
        self.db = db
        self.patient_id = patient_id
        self.tool_registry = ToolRegistry(db, patient_id)
        self.planner = Planner()
        self.executor = Executor(self.tool_registry)
        self.chat_agent = ChatAgent()

    def handle_message(
        self, 
        user_message: str, 
        recent_messages: List[tuple[str, str]], 
        llm_params: Optional[LLMParams] = None
    ) -> Dict[str, Any]:
        params = llm_params or LLMParams()
        trace = []

        try:
            # 1. Planning Step
            plan = self.planner.plan(user_message, self.tool_registry.get_tool_metadata(), params)
            trace.append({"step": "plan", "output": plan})

            # 2. Execution Step
            execution_result = {}
            if plan.get("name"):
                execution_result = self.executor.execute(plan)
                trace.append({"step": "execute", "output": execution_result})

            # 3. Response Synthesis
            tool_feedback = ""
            if execution_result.get("status") == "success":
                tool_feedback = f"【系统动作】已调用并成功执行工具：{execution_result.get('tool_name')}。结果已同步到当前会话。"
            elif execution_result.get("status") == "error":
                tool_feedback = f"【系统动作】试图执行工具 {execution_result.get('tool_name')} 时遇到问题，但仍将为您提供建议。"

            context = f"\n\n[Agent Trace: {json.dumps(trace, ensure_ascii=False)}]\n\n" if settings.app_env == 'dev' else ""
            
            final_reply = self.chat_agent.reply(
                user_message=user_message,
                recent_messages=recent_messages,
                extra_context=f"{tool_feedback}\n{context}",
                llm_params=params
            )

            return {
                "reply": final_reply,
                "trace": trace,
                "has_tool_use": bool(plan.get("name")),
                "status": "success"
            }
        except Exception as exc:
            logger.error(f"Orchestrator Error: {exc}", exc_info=True)
            return {
                "reply": f"抱歉，系统在处理您的请求时遇到了内部错误。请复查您的模型配置或稍后重试。\n错误详情: {exc}",
                "trace": trace,
                "has_tool_use": False,
                "status": "error"
            }
