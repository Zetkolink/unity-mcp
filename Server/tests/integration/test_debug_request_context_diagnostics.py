import pytest


@pytest.mark.asyncio
async def test_debug_request_context_returns_sanitized_diagnostics(monkeypatch):
    # Import inside test so stubs in conftest are applied.
    import services.tools.debug_request_context as mod

    class DummyCtx:
        # minimal surface for debug_request_context
        request_context = None
        session_id = None
        client_id = None

        async def get_state(self, _k):
            return None

    # Ensure get_package_version is stable for assertion
    monkeypatch.setattr(mod, "get_package_version", lambda: "9.9.9-test")

    res = await mod.debug_request_context(DummyCtx())
    assert res.get("success") is True
    data = res.get("data") or {}
    server = data.get("server") or {}
    request_context = data.get("request_context") or {}
    session_state = data.get("session_state") or {}
    assert server.get("version") == "9.9.9-test"
    assert "cwd" not in server
    assert "argv" not in server
    assert request_context.get("present") is False
    assert request_context.get("meta_present") is False
    assert isinstance(session_state.get("derived_key_present"), bool)
    assert "derived_key" not in session_state
    assert "all_keys_in_store" not in session_state
    assert "middleware_id" not in session_state

