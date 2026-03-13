import pytest

from .test_helpers import DummyContext
import services.resources.prefab as prefab_res_mod


@pytest.mark.asyncio
async def test_get_prefab_hierarchy_truncates_by_default(monkeypatch):
    captured = {}

    async def fake_send(cmd, params, **kwargs):
        captured["cmd"] = cmd
        captured["params"] = params
        return {
            "success": True,
            "data": {
                "prefabPath": "Assets/Prefabs/Player.prefab",
                "total": 250,
                "items": [
                    {"name": f"Item{i}", "instanceId": i, "path": f"/Root/Item{i}"}
                    for i in range(250)
                ],
            },
        }

    monkeypatch.setattr(prefab_res_mod, "async_send_command_with_retry", fake_send)

    resp = await prefab_res_mod.get_prefab_hierarchy(
        ctx=DummyContext(),
        encoded_path="Assets%2FPrefabs%2FPlayer.prefab",
    )

    assert resp.success is True
    assert captured["params"]["action"] == "get_hierarchy"
    assert resp.data["returnedCount"] == 200
    assert resp.data["truncated"] is True
    assert resp.data["remainingCount"] == 50
    assert len(resp.data["items"]) == 200


@pytest.mark.asyncio
async def test_get_prefab_hierarchy_honors_explicit_max_items(monkeypatch):
    async def fake_send(cmd, params, **kwargs):
        return {
            "success": True,
            "data": {
                "prefabPath": "Assets/Prefabs/Small.prefab",
                "total": 5,
                "items": [
                    {"name": f"Item{i}", "instanceId": i, "path": f"/Root/Item{i}"}
                    for i in range(5)
                ],
            },
        }

    monkeypatch.setattr(prefab_res_mod, "async_send_command_with_retry", fake_send)

    resp = await prefab_res_mod.get_prefab_hierarchy(
        ctx=DummyContext(),
        encoded_path="Assets%2FPrefabs%2FSmall.prefab",
        max_items=3,
    )

    assert resp.success is True
    assert resp.data["returnedCount"] == 3
    assert resp.data["truncated"] is True
    assert resp.data["remainingCount"] == 2
    assert len(resp.data["items"]) == 3


@pytest.mark.asyncio
async def test_get_prefab_hierarchy_rejects_invalid_max_items():
    resp = await prefab_res_mod.get_prefab_hierarchy(
        ctx=DummyContext(),
        encoded_path="Assets%2FPrefabs%2FSmall.prefab",
        max_items=0,
    )

    assert resp.success is False
    assert "max_items" in (resp.error or "")
