from typing import Any

from core.telemetry import get_package_version

from fastmcp import Context
from mcp.types import ToolAnnotations

from services.registry import mcp_for_unity_tool
from transport.unity_instance_middleware import get_unity_instance_middleware
from transport.plugin_hub import PluginHub


@mcp_for_unity_tool(
    unity_target=None,
    group="debug",
    description=(
        "Return a sanitized summary of the current FastMCP request context for troubleshooting "
        "routing and session issues. Raw metadata and middleware internals are omitted."
    ),
    annotations=ToolAnnotations(
        title="Debug Request Context",
        readOnlyHint=True,
    ),
)
async def debug_request_context(ctx: Context) -> dict[str, Any]:
    # Check request_context properties
    rc = getattr(ctx, "request_context", None)
    rc_client_id = getattr(rc, "client_id", None)
    rc_session_id = getattr(rc, "session_id", None)
    meta = getattr(rc, "meta", None)

    # Check direct ctx properties (per latest FastMCP docs)
    ctx_session_id = getattr(ctx, "session_id", None)
    ctx_client_id = getattr(ctx, "client_id", None)

    # Get session state info via middleware
    middleware = get_unity_instance_middleware()
    derived_key = await middleware.get_session_key(ctx)
    active_instance = await middleware.get_active_instance(ctx)

    plugin_hub_configured = PluginHub.is_configured()

    return {
        "success": True,
        "data": {
            "server": {
                "version": get_package_version(),
            },
            "request_context": {
                "present": rc is not None,
                "client_id_present": rc_client_id is not None,
                "session_id_present": rc_session_id is not None,
                "meta_present": meta is not None,
                "meta_type": type(meta).__name__ if meta is not None else None,
            },
            "direct_properties": {
                "session_id_present": ctx_session_id is not None,
                "client_id_present": ctx_client_id is not None,
            },
            "session_state": {
                "derived_key_present": derived_key is not None,
                "active_instance": active_instance,
                "plugin_hub_configured": plugin_hub_configured,
            },
            "note": "Sanitized summary only; raw metadata and middleware internals are intentionally omitted.",
        },
    }
