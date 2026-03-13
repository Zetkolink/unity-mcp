from __future__ import annotations

import pytest

from .test_helpers import DummyContext

import services.resources.editor_state as editor_state_mod
import services.tools.find_gameobjects as find_go_mod
import services.tools.manage_asset as manage_asset_mod
import services.tools.manage_prefabs as manage_prefabs_mod
import services.tools.manage_scene as manage_scene_mod
import services.tools.preflight as preflight_mod
import services.tools.refresh_unity as refresh_mod


def _dirty_editor_state() -> dict:
    return {
        "success": True,
        "data": {
            "assets": {"external_changes_dirty": True},
            "compilation": {"is_compiling": False, "is_domain_reload_pending": False},
            "tests": {"is_running": False},
        },
    }


@pytest.mark.asyncio
async def test_preflight_blocks_on_external_changes_without_refresh(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

    async def fake_get_editor_state(_ctx):
        return _dirty_editor_state()

    refresh_called = False

    async def fake_refresh_unity(*args, **kwargs):
        nonlocal refresh_called
        refresh_called = True
        return {"success": True}

    monkeypatch.setattr(editor_state_mod, "get_editor_state", fake_get_editor_state)
    monkeypatch.setattr(refresh_mod, "refresh_unity", fake_refresh_unity)

    gate = await preflight_mod.preflight(DummyContext(), block_if_dirty=True)

    assert gate is not None
    assert gate.error == "busy"
    assert gate.data["reason"] == "external_changes_dirty"
    assert refresh_called is False


@pytest.mark.asyncio
async def test_preflight_refreshes_when_dirty_refresh_requested(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

    async def fake_get_editor_state(_ctx):
        return _dirty_editor_state()

    captured: dict[str, object] = {}

    async def fake_refresh_unity(*args, **kwargs):
        captured.update(kwargs)
        return {"success": True}

    monkeypatch.setattr(editor_state_mod, "get_editor_state", fake_get_editor_state)
    monkeypatch.setattr(refresh_mod, "refresh_unity", fake_refresh_unity)

    gate = await preflight_mod.preflight(DummyContext(), refresh_if_dirty=True)

    assert gate is None
    assert captured["mode"] == "if_dirty"
    assert captured["scope"] == "all"
    assert captured["compile"] == "request"
    assert captured["wait_for_ready"] is True


@pytest.mark.asyncio
async def test_preflight_block_if_dirty_takes_precedence_over_refresh(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

    async def fake_get_editor_state(_ctx):
        return _dirty_editor_state()

    refresh_called = False

    async def fake_refresh_unity(*args, **kwargs):
        nonlocal refresh_called
        refresh_called = True
        return {"success": True}

    monkeypatch.setattr(editor_state_mod, "get_editor_state", fake_get_editor_state)
    monkeypatch.setattr(refresh_mod, "refresh_unity", fake_refresh_unity)

    gate = await preflight_mod.preflight(
        DummyContext(),
        refresh_if_dirty=True,
        block_if_dirty=True,
    )

    assert gate is not None
    assert gate.data["reason"] == "external_changes_dirty"
    assert refresh_called is False


@pytest.mark.asyncio
async def test_find_gameobjects_blocks_if_dirty(monkeypatch):
    captured: dict[str, object] = {}

    async def fake_preflight(*args, **kwargs):
        captured.update(kwargs)
        return None

    async def fake_send(cmd, params, **kwargs):
        return {"success": True, "data": {"instanceIDs": []}}

    monkeypatch.setattr(find_go_mod, "preflight", fake_preflight)
    monkeypatch.setattr(find_go_mod, "async_send_command_with_retry", fake_send)

    resp = await find_go_mod.find_gameobjects(
        ctx=DummyContext(),
        search_term="Player",
        search_method="by_name",
    )

    assert resp["success"] is True
    assert captured["wait_for_no_compile"] is True
    assert captured["block_if_dirty"] is True
    assert captured.get("refresh_if_dirty", False) is False


@pytest.mark.asyncio
async def test_manage_scene_read_action_blocks_if_dirty(monkeypatch):
    captured: dict[str, object] = {}

    async def fake_preflight(*args, **kwargs):
        captured.update(kwargs)
        return None

    async def fake_send(cmd, params, **kwargs):
        return {"success": True, "data": {}}

    monkeypatch.setattr(manage_scene_mod, "preflight", fake_preflight)
    monkeypatch.setattr(manage_scene_mod, "async_send_command_with_retry", fake_send)

    resp = await manage_scene_mod.manage_scene(ctx=DummyContext(), action="get_hierarchy")

    assert resp["success"] is True
    assert captured["block_if_dirty"] is True
    assert captured["refresh_if_dirty"] is False


@pytest.mark.asyncio
async def test_manage_scene_mutating_action_refreshes_if_dirty(monkeypatch):
    captured: dict[str, object] = {}

    async def fake_preflight(*args, **kwargs):
        captured.update(kwargs)
        return None

    async def fake_send(cmd, params, **kwargs):
        return {"success": True, "data": {}}

    monkeypatch.setattr(manage_scene_mod, "preflight", fake_preflight)
    monkeypatch.setattr(manage_scene_mod, "async_send_command_with_retry", fake_send)

    resp = await manage_scene_mod.manage_scene(
        ctx=DummyContext(),
        action="create",
        name="NewScene",
    )

    assert resp["success"] is True
    assert captured["refresh_if_dirty"] is True
    assert captured["block_if_dirty"] is False


@pytest.mark.asyncio
async def test_manage_asset_search_blocks_if_dirty(monkeypatch):
    captured: dict[str, object] = {}

    async def fake_preflight(*args, **kwargs):
        captured.update(kwargs)
        return None

    async def fake_send(cmd, params, **kwargs):
        return {"success": True, "data": {}}

    monkeypatch.setattr(manage_asset_mod, "preflight", fake_preflight)
    monkeypatch.setattr(manage_asset_mod, "async_send_command_with_retry", fake_send)

    resp = await manage_asset_mod.manage_asset(
        ctx=DummyContext(),
        action="search",
        path="Assets",
    )

    assert resp["success"] is True
    assert captured["block_if_dirty"] is True
    assert captured["refresh_if_dirty"] is False


@pytest.mark.asyncio
async def test_manage_asset_mutation_refreshes_if_dirty(monkeypatch):
    captured: dict[str, object] = {}

    async def fake_preflight(*args, **kwargs):
        captured.update(kwargs)
        return None

    async def fake_send(cmd, params, **kwargs):
        return {"success": True, "data": {}}

    monkeypatch.setattr(manage_asset_mod, "preflight", fake_preflight)
    monkeypatch.setattr(manage_asset_mod, "async_send_command_with_retry", fake_send)

    resp = await manage_asset_mod.manage_asset(
        ctx=DummyContext(),
        action="create_folder",
        path="Assets/NewFolder",
    )

    assert resp["success"] is True
    assert captured["refresh_if_dirty"] is True
    assert captured["block_if_dirty"] is False


@pytest.mark.asyncio
async def test_manage_prefabs_read_action_blocks_if_dirty(monkeypatch):
    captured: dict[str, object] = {}

    async def fake_preflight(*args, **kwargs):
        captured.update(kwargs)
        return None

    async def fake_send(cmd, params, **kwargs):
        return {"success": True, "data": {}}

    monkeypatch.setattr(manage_prefabs_mod, "preflight", fake_preflight)
    monkeypatch.setattr(manage_prefabs_mod, "async_send_command_with_retry", fake_send)

    resp = await manage_prefabs_mod.manage_prefabs(
        ctx=DummyContext(),
        action="get_info",
        prefab_path="Assets/Prefabs/Player.prefab",
    )

    assert resp["success"] is True
    assert captured["block_if_dirty"] is True
    assert captured["refresh_if_dirty"] is False


@pytest.mark.asyncio
async def test_manage_prefabs_mutation_refreshes_if_dirty(monkeypatch):
    captured: dict[str, object] = {}

    async def fake_preflight(*args, **kwargs):
        captured.update(kwargs)
        return None

    async def fake_send(cmd, params, **kwargs):
        return {"success": True, "data": {}}

    monkeypatch.setattr(manage_prefabs_mod, "preflight", fake_preflight)
    monkeypatch.setattr(manage_prefabs_mod, "async_send_command_with_retry", fake_send)

    resp = await manage_prefabs_mod.manage_prefabs(
        ctx=DummyContext(),
        action="modify_contents",
        prefab_path="Assets/Prefabs/Player.prefab",
    )

    assert resp["success"] is True
    assert captured["refresh_if_dirty"] is True
    assert captured["block_if_dirty"] is False
