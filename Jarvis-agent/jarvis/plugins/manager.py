"""Plugin manager."""
import importlib, importlib.util, inspect
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from ..tools.base import Tool


@dataclass
class PluginInfo:
    name: str
    version: str
    author: str
    description: str
    path: Path
    enabled: bool = True
    loaded_at: Optional[datetime] = None
    error: Optional[str] = None


@dataclass
class Plugin:
    info: PluginInfo
    tools: List[Tool] = field(default_factory=list)


class PluginManager:
    def __init__(self, plugin_dir=None):
        self.plugin_dir = plugin_dir or (Path.home() / ".jarvis" / "plugins")
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
        self.plugins: Dict[str, Plugin] = {}
        self._load_all()

    def _load_all(self):
        b = Path(__file__).parent / "builtins"
        if b.exists(): self._load_from_dir(b)
        if self.plugin_dir.exists(): self._load_from_dir(self.plugin_dir)

    def _load_from_dir(self, directory):
        for p in directory.iterdir():
            if p.is_file() and p.suffix == ".py": self._load_plugin_file(p)
            elif p.is_dir() and (p / "__init__.py").exists(): self._load_plugin_package(p)

    def _load_plugin_file(self, path):
        try:
            spec = importlib.util.spec_from_file_location(f"jarvis_plugin_{path.stem}", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self._register_module(module, path)
        except Exception as e: self._register_error(path, str(e))

    def _load_plugin_package(self, path):
        try:
            spec = importlib.util.spec_from_file_location(f"jarvis_plugin_pkg_{path.name}", path / "__init__.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self._register_module(module, path)
        except Exception as e: self._register_error(path, str(e))

    def _register_module(self, module, path):
        info = PluginInfo(
            name=getattr(module, "__plugin_name__", path.stem),
            version=getattr(module, "__plugin_version__", "1.0.0"),
            author=getattr(module, "__plugin_author__", "Unknown"),
            description=getattr(module, "__plugin_description__", ""),
            path=path, loaded_at=datetime.now()
        )
        tools = []
        for n, o in inspect.getmembers(module, inspect.isclass):
            if issubclass(o, Tool) and o is not Tool:
                try: tools.append(o())
                except: pass
        if not tools and not info.description: return
        self.plugins[info.name] = Plugin(info=info, tools=tools)
        print(f"[Plugin] {info.name} v{info.version} ({len(tools)} tools)")

    def _register_error(self, path, error):
        info = PluginInfo(name=path.stem, version="?", author="?",
            description=f"Erro: {error}", path=path, error=error)
        self.plugins[path.stem] = Plugin(info=info)

    def get_all_tools(self):
        tools = []
        for p in self.plugins.values():
            if p.info.enabled and not p.info.error:
                tools.extend(p.tools)
        return tools

    def list_plugins(self): return [p.info for p in self.plugins.values()]

    def enable(self, name):
        if name in self.plugins: self.plugins[name].info.enabled = True

    def disable(self, name):
        if name in self.plugins: self.plugins[name].info.enabled = False
