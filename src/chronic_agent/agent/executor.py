from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from chronic_agent.agent.tool_registry import ToolRegistry

logger = logging.getLogger(__name__)

class Executor:
    def __init__(self, tool_registry: ToolRegistry):
        self.tool_registry = tool_registry

    def execute(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        tool_name = plan.get("name")
        params = plan.get("parameters", {})
        
        if not tool_name:
            return {"status": "skipped", "result": "无具体工具被选取。"}

        try:
            result = self.tool_registry.call_tool(tool_name, **params)
            return {
                "status": "success",
                "tool_name": tool_name,
                "parameters": params,
                "result": result
            }
        except Exception as exc:
            logger.error(f"Execution Error: {exc}")
            return {
                "status": "error",
                "tool_name": tool_name, 
                "error": str(exc),
                "result": f"执行器抛出异常：{exc}"
            }
