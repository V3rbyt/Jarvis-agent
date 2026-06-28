"""Executor de planos."""
import time
from typing import Callable, Optional
from ..plugins import PluginManager
from ..tools import ToolRegistry, ToolResult
from .planner import Plan


class Executor:
    def __init__(self, registry, plugins, on_step_start=None,
                 on_step_done=None, on_confirm=None, analytics=None):
        self.tools = {}
        if hasattr(registry, "list_all"):
            for t in registry.list_all():
                self.tools[t.name] = t
        for t in plugins.get_all_tools():
            self.tools[t.name] = t
        self.plugins = plugins
        self.on_step_start = on_step_start
        self.on_step_done = on_step_done
        self.on_confirm = on_confirm
        self.analytics = analytics

    def execute(self, plan):
        if not plan.tool or plan.tool == "nenhuma":
            return ToolResult(True, data={"fala": plan.fala}, display=plan.fala)
        tool = self.tools.get(plan.tool)
        if not tool:
            return ToolResult(False, error=f"Tool nao encontrada: {plan.tool}")
        if getattr(tool, "requires_confirmation", False) and self.on_confirm:
            try:
                if not self.on_confirm(plan):
                    return ToolResult(False, error="Cancelado")
            except Exception as e:
                return ToolResult(False, error=str(e))
        if self.on_step_start:
            try: self.on_step_start(plan)
            except: pass
        start = time.time()
        try:
            result = tool.execute(plan.params)
        except Exception as e:
            result = ToolResult(False, error=str(e))
        if self.analytics:
            try:
                self.analytics.track("tool_use", plan.tool,
                    duration_ms=int((time.time()-start)*1000), success=result.success)
            except: pass
        if self.on_step_done:
            try: self.on_step_done(plan, result)
            except: pass
        return result
