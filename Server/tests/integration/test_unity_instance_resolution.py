from __future__ import annotations

import importlib
import inspect
import re
from pathlib import Path

import pytest

from .test_helpers import DummyContext


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("module_name", "func_name", "kwargs", "expected_command"),
    [
        ("services.tools.manage_audio", "manage_audio", {"action": "list_sources"}, "manage_audio"),
        ("services.tools.manage_build", "manage_build", {"action": "get_player_settings"}, "manage_build"),
        ("services.tools.manage_input_system", "manage_input_system", {"action": "list_devices"}, "manage_input_system"),
        ("services.tools.manage_video", "manage_video", {"action": "list_players"}, "manage_video"),
        ("services.tools.manage_addressables", "manage_addressables", {"action": "list_groups"}, "manage_addressables"),
        ("services.tools.rendering_stats", "rendering_stats", {"action": "get_stats"}, "rendering_stats"),
    ],
)
async def test_tool_wrappers_resolve_unity_instance_before_transport(
    monkeypatch,
    module_name: str,
    func_name: str,
    kwargs: dict[str, object],
    expected_command: str,
):
    module = importlib.import_module(module_name)
    handler = getattr(module, func_name)

    async def fake_get_unity_instance_from_context(_ctx):
        return "Project@abc123"

    captured: dict[str, object] = {}

    async def fake_send_with_unity_instance(_send_fn, unity_instance, *args, **_kwargs):
        captured["unity_instance"] = unity_instance
        captured["command"] = args[0] if args else None
        return {"success": True, "message": "OK", "data": {}}

    monkeypatch.setattr(module, "get_unity_instance_from_context", fake_get_unity_instance_from_context)
    monkeypatch.setattr(module, "send_with_unity_instance", fake_send_with_unity_instance)

    response = await handler(ctx=DummyContext(), **kwargs)

    assert response["success"] is True
    assert captured["command"] == expected_command
    assert captured["unity_instance"] == "Project@abc123"
    assert not inspect.isawaitable(captured["unity_instance"])


def test_tool_wrappers_do_not_store_unawaited_unity_instance_coroutines():
    tools_dir = Path(__file__).resolve().parents[2] / "src" / "services" / "tools"
    bad_pattern = re.compile(
        r"^\s*unity_instance\s*=\s*get_unity_instance_from_context\(ctx\)\s*$",
        re.MULTILINE,
    )

    offenders = []
    for path in sorted(tools_dir.rglob("*.py")):
        if bad_pattern.search(path.read_text()):
            offenders.append(path.relative_to(tools_dir).as_posix())

    assert offenders == []
