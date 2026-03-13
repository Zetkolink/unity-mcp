import asyncio

from .test_helpers import DummyContext
import services.tools.manage_asset as manage_asset_mod


def test_manage_asset_search_preview_applies_small_default_page_size(monkeypatch):
    captured = {}

    async def fake_async_send(_cmd, params, **kwargs):
        captured["params"] = params
        return {"success": True, "data": {}}

    monkeypatch.setattr(manage_asset_mod, "async_send_command_with_retry", fake_async_send)

    result = asyncio.run(
        manage_asset_mod.manage_asset(
            ctx=DummyContext(),
            action="search",
            path="Assets",
            generate_preview=True,
        )
    )

    assert result == {"success": True, "data": {}}
    assert captured["params"]["generatePreview"] is True
    assert captured["params"]["pageSize"] == 10


def test_manage_asset_search_preview_keeps_explicit_page_size(monkeypatch):
    captured = {}

    async def fake_async_send(_cmd, params, **kwargs):
        captured["params"] = params
        return {"success": True, "data": {}}

    monkeypatch.setattr(manage_asset_mod, "async_send_command_with_retry", fake_async_send)

    result = asyncio.run(
        manage_asset_mod.manage_asset(
            ctx=DummyContext(),
            action="search",
            path="Assets",
            generate_preview=True,
            page_size=3,
        )
    )

    assert result == {"success": True, "data": {}}
    assert captured["params"]["pageSize"] == 3
