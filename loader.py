"""Plugin discovery and loading for DashApp tools."""

import importlib
import json
import logging
from pathlib import Path
from typing import Any

from tools.base import BaseTool

logger = logging.getLogger(__name__)

TOOLS_DIR = Path(__file__).parent / "tools"


def load_tools() -> list[BaseTool]:
    """Discover and instantiate all valid tool plugins.

    Returns:
        List of instantiated BaseTool subclasses, sorted by directory name.
    """
    tools: list[BaseTool] = []
    for tool_dir in sorted(TOOLS_DIR.iterdir()):
        if not tool_dir.is_dir() or tool_dir.name.startswith("_"):
            continue
        tool = _load_tool(tool_dir)
        if tool is not None:
            tools.append(tool)
    return tools


def _load_tool(tool_dir: Path) -> BaseTool | None:
    """Attempt to load a single tool from *tool_dir*.

    Args:
        tool_dir: Directory expected to contain manifest.json and tool.py.

    Returns:
        An instantiated tool, or None on any error.
    """
    manifest_path = tool_dir / "manifest.json"
    tool_path = tool_dir / "tool.py"

    if not manifest_path.exists():
        logger.warning("Skipping %s: missing manifest.json", tool_dir.name)
        return None
    if not tool_path.exists():
        logger.warning("Skipping %s: missing tool.py", tool_dir.name)
        return None

    manifest = _read_manifest(manifest_path)
    if manifest is None:
        return None

    return _import_tool(tool_dir.name, manifest)


def _read_manifest(path: Path) -> dict[str, Any] | None:
    """Parse and validate a manifest.json file.

    Args:
        path: Path to manifest.json.

    Returns:
        Parsed manifest dict, or None if invalid.
    """
    try:
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Skipping %s: bad manifest — %s", path.parent.name, exc)
        return None

    if "name" not in data:
        logger.warning("Skipping %s: manifest missing 'name' key", path.parent.name)
        return None

    return data


def _import_tool(dir_name: str, manifest: dict[str, Any]) -> BaseTool | None:
    """Import tool.py from the named sub-package and return an instance.

    Args:
        dir_name: The tool's directory name (used as the sub-package name).
        manifest: Parsed manifest dict (unused here but available for future use).

    Returns:
        An instantiated BaseTool, or None on import/type errors.
    """
    module_path = f"tools.{dir_name}.tool"
    try:
        module = importlib.import_module(module_path)
    except Exception as exc:
        logger.warning("Skipping %s: import error — %s", dir_name, exc)
        return None

    tool_class = getattr(module, "Tool", None)
    if tool_class is None:
        logger.warning("Skipping %s: no 'Tool' class in tool.py", dir_name)
        return None

    if not (isinstance(tool_class, type) and issubclass(tool_class, BaseTool)):
        logger.warning("Skipping %s: 'Tool' does not subclass BaseTool", dir_name)
        return None

    try:
        return tool_class()
    except Exception as exc:
        logger.warning("Skipping %s: instantiation error — %s", dir_name, exc)
        return None
