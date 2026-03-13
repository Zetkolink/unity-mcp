from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ROOT_SKILL_DIR = REPO_ROOT / "unity-mcp-skill"
OPTIONAL_MIRROR_DIRS = [
    REPO_ROOT / ".agents" / "skills" / "unity-mcp-skill",
    REPO_ROOT / ".claude" / "skills" / "unity-mcp-skill",
]
MIRRORED_FILES = [
    Path("SKILL.md"),
    Path("references/tools-reference.md"),
    Path("references/workflows.md"),
]
STALE_PATTERNS = {
    "capture_screenshot (in manage_scene)": "old manage_scene screenshot guidance",
    'manage_scene(action="screenshot")': "old screenshot API example",
    "query_packages": "removed manage_packages action name",
    'editor_state["ready_for_tools"]': "old top-level editor_state ready key",
    'editor_state["is_compiling"]': "old top-level editor_state compile key",
}


def _markdown_files():
    files = list(ROOT_SKILL_DIR.rglob("*.md"))
    for mirror_dir in OPTIONAL_MIRROR_DIRS:
        if mirror_dir.exists():
            files.extend(mirror_dir.rglob("*.md"))
    return files


def test_skill_mirrors_match_root_when_present():
    for relative_path in MIRRORED_FILES:
        root_text = (ROOT_SKILL_DIR / relative_path).read_text(encoding="utf-8")
        for mirror_dir in OPTIONAL_MIRROR_DIRS:
            mirror_path = mirror_dir / relative_path
            if not mirror_path.exists():
                continue
            mirror_text = mirror_path.read_text(encoding="utf-8")
            assert mirror_text == root_text, f"{mirror_path} drifted from {ROOT_SKILL_DIR / relative_path}"


def test_skill_markdown_has_no_stale_patterns():
    for path in _markdown_files():
        text = path.read_text(encoding="utf-8")
        for pattern, description in STALE_PATTERNS.items():
            assert pattern not in text, f"{path} still contains {description}: {pattern}"


def test_resources_reference_documents_readiness_and_tool_groups():
    resources_reference = (ROOT_SKILL_DIR / "references/resources-reference.md").read_text(encoding="utf-8")

    assert "mcpforunity://tool-groups" in resources_reference
    assert "advice.ready_for_tools" in resources_reference
    assert "assets.external_changes_dirty" in resources_reference


def test_tools_reference_documents_manage_tools_and_subscene_actions():
    tools_reference = (ROOT_SKILL_DIR / "references/tools-reference.md").read_text(encoding="utf-8")

    assert "### manage_tools" in tools_reference
    assert "list_subscenes" in tools_reference
    assert "open_subscene" in tools_reference
    assert "close_subscene" in tools_reference
