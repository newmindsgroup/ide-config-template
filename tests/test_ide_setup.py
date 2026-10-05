#!/usr/bin/env python3
"""Behavior checks for the public team setup wizard.

Version-Timestamp: 2026-10-05 19:34:30 AST
"""

from __future__ import annotations

import json
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
WIZARD = ROOT / "scripts" / "ide-setup.py"


def wizard_module():
    spec = importlib.util.spec_from_file_location("ide_setup", WIZARD)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_review_requires_local_entitlement_confirmation():
    module = wizard_module()
    machine = {"recommended_local_tier": "none"}
    profile = {"subscriptions": {"claude": True}}
    assert "pending" in module.routing(profile, machine)["code_design_review"]
    profile.update({"opus_available": True, "fable_available": True, "claude_extra_usage_off": True})
    route = module.routing(profile, machine)
    assert "Opus 5" in route["code_design_review"]
    assert "Fable 5.1" in route["complex_review"]
    profile["subscriptions"]["claude"] = False
    assert "pending" in module.routing(profile, machine)["complex_review"]


def test_new_review_fields_reject_non_boolean():
    module = wizard_module()
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "profile.json"
        path.write_text(json.dumps({"fable_available": "yes"}))
        try:
            module.read_profile(path, False)
        except ValueError:
            pass
        else:
            raise AssertionError("String entitlement must be rejected")


def run(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(WIZARD), *arguments],
        capture_output=True,
        check=False,
        text=True,
    )


def test_scan_reports_only_non_secret_capabilities() -> None:
    result = run("--scan")
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert {"platform", "architecture", "ram_gb", "free_disk_gb", "tools"} <= report.keys()
    assert "subscriptions" not in report
    assert "token" not in result.stdout.lower()


def test_plan_recommends_safe_free_only_boundary() -> None:
    with tempfile.TemporaryDirectory() as directory:
        profile = Path(directory) / "profile.json"
        profile.write_text(
            json.dumps(
                {
                    "name": "Avery",
                    "role": "developer",
                    "goals": ["build web applications"],
                    "privacy": "internal",
                    "ides": ["codex", "cursor"],
                    "subscriptions": {"chatgpt": True, "claude": False, "openrouter_free": False},
                }
            )
        )
        result = run("--plan", "--profile", str(profile))
        assert result.returncode == 0, result.stderr
        plan = json.loads(result.stdout)
        assert plan["routing"]["openrouter"] == "disabled unless explicitly enabled"
        assert plan["routing"]["paid_api_fallback"] == "never automatic"
        assert plan["recommended_skills"] == []
        assert "recommendations only" in plan["skill_catalog"]["policy"]


def test_cursor_subscription_is_not_a_hosted_fallback_provider() -> None:
    with tempfile.TemporaryDirectory() as directory:
        profile = Path(directory) / "profile.json"
        profile.write_text(
            json.dumps(
                {
                    "name": "Avery",
                    "role": "developer",
                    "privacy": "internal",
                    "ides": ["cursor"],
                    "subscriptions": {"cursor": True},
                }
            )
        )
        result = run("--plan", "--non-interactive", "--profile", str(profile))
        assert result.returncode == 0, result.stderr
        plan = json.loads(result.stdout)
        assert plan["routing"]["hosted_default"] == "no hosted provider declared"
        assert "Cursor subscription requires an in-app model check" in plan["routing"]["cursor_note"]


def test_routing_focus_returns_one_canonical_implementation_goal() -> None:
    with tempfile.TemporaryDirectory() as directory:
        profile = Path(directory) / "profile.json"
        profile.write_text(
            json.dumps(
                {
                    "name": "Avery",
                    "role": "developer",
                    "privacy": "internal",
                    "ides": ["codex"],
                    "subscriptions": {"chatgpt": True, "openrouter_free": False},
                }
            )
        )
        result = run("--plan", "--focus", "llm-routing", "--non-interactive", "--profile", str(profile))
        assert result.returncode == 0, result.stderr
        plan = json.loads(result.stdout)
        assert plan["focus"] == "llm-routing"
        assert plan["implementation_goal"] == "Implement a safe LLM routing and fallback strategy for this person and computer."


def test_plan_rejects_secret_like_profile_fields() -> None:
    with tempfile.TemporaryDirectory() as directory:
        profile = Path(directory) / "profile.json"
        profile.write_text(
            json.dumps(
                {
                    "name": "Avery",
                    "role": "developer",
                    "privacy": "internal",
                    "api_key": "must-not-be-stored",
                }
            )
        )
        result = run("--plan", "--non-interactive", "--profile", str(profile))
        assert result.returncode == 2
        assert "unsupported field" in result.stderr.lower()


def test_apply_creates_reversible_local_outputs_and_does_not_overwrite_user_rules() -> None:
    with tempfile.TemporaryDirectory() as directory:
        home = Path(directory) / "home"
        workspace = Path(directory) / "workspace"
        home.mkdir()
        workspace.mkdir()
        codex_agents = home / ".codex" / "AGENTS.md"
        codex_agents.parent.mkdir()
        codex_agents.write_text("# Existing user instructions\n")
        profile = Path(directory) / "profile.json"
        profile.write_text(
            json.dumps(
                {
                    "name": "Avery",
                    "role": "designer",
                    "astra_available": True,
                    "goals": ["design and review interfaces"],
                    "privacy": "confidential",
                    "ides": ["codex", "claude", "cursor"],
                    "subscriptions": {"chatgpt": True, "claude": True, "openrouter_free": False},
                }
            )
        )
        missing_confirmation = run("--apply", "--profile", str(profile), "--home", str(home), "--workspace", str(workspace))
        assert missing_confirmation.returncode == 2
        result = run("--apply", "--confirm", "--profile", str(profile), "--home", str(home), "--workspace", str(workspace))
        assert result.returncode == 0, result.stderr
        assert "# Existing user instructions" in codex_agents.read_text()
        assert "IDE-CONFIG-TEMPLATE:START" in codex_agents.read_text()
        assert "Astra, Low effort, Standard speed" in codex_agents.read_text()
        assert (home / ".claude" / "CLAUDE.md").is_file()
        assert (workspace / ".cursor" / "rules" / "ide-config-template.mdc").is_file()
        manual = home / ".ide-config" / "manual"
        assert (manual / "chatgpt-custom-instructions.md").is_file()
        assert (manual / "claude-web-project-instructions.md").is_file()
        assert (home / ".ide-config" / "backups").is_dir()
        assert not (home / ".ide-config" / "profile.local.json").read_text().count("api_key")


def test_remove_managed_blocks_requires_confirmation_and_preserves_user_text() -> None:
    with tempfile.TemporaryDirectory() as directory:
        home = Path(directory) / "home"
        home.mkdir()
        profile = Path(directory) / "profile.json"
        profile.write_text(json.dumps({"name": "Avery", "role": "developer", "ides": ["codex"]}))
        applied = run("--apply", "--confirm", "--profile", str(profile), "--home", str(home))
        assert applied.returncode == 0, applied.stderr
        agents = home / ".codex" / "AGENTS.md"
        agents.write_text("# Existing instructions\n\n" + agents.read_text())
        refused = run("--remove-managed-block", "--profile", str(profile), "--home", str(home))
        assert refused.returncode == 2
        removed = run("--remove-managed-block", "--confirm", "--profile", str(profile), "--home", str(home))
        assert removed.returncode == 0, removed.stderr
        assert "# Existing instructions" in agents.read_text()
        assert "IDE-CONFIG-TEMPLATE:START" not in agents.read_text()


def test_local_tier_is_limited_by_free_disk() -> None:
    module = wizard_module()
    assert module.local_tier(128, 5, True) == "none"
    assert module.local_tier(128, 20, True) == "light"
    assert module.local_tier(128, 130, True) == "full"


def test_astra_requires_explicit_access_and_reaches_instructions() -> None:
    module = wizard_module()
    machine = {"recommended_local_tier": "none"}
    profile = {"subscriptions": {"chatgpt": True}, "name": "Avery", "role": "developer", "goals": [], "stack": [], "privacy": "internal"}
    assert "Astra" not in module.routing(profile, machine)["substantial_work"]
    profile["astra_available"] = True
    route = module.routing(profile, machine)
    assert "Astra" in route["substantial_work"]
    instruction = module.compact_instruction(profile, {"recommended_skills": [], "routing": route})
    assert "Astra" in instruction
    profile["subscriptions"] = {}
    assert "Astra" not in module.routing(profile, machine)["substantial_work"]


def test_selective_prompt_planning_instructions():
    module = wizard_module()
    profile = {"subscriptions": {}, "goals": [], "name": "Tester", "role": "developer", "stack": [], "privacy": "internal"}
    route = module.routing(profile, {"recommended_local_tier": "none"})
    instruction = module.compact_instruction(profile, {"recommended_skills": [], "routing": route})
    for term in ("Refine once, then execute", "not ordinary coding or tool errors",
                 "Planning grants no implementation or deployment authority",
                 "Neither planning nor refinement automatically raises effort"):
        assert term in instruction
        for platform in ("ChatGPT", "Claude"):
            assert term in module.web_instruction(profile, {"routing": route}, platform)


def test_app_profile_defaults_and_exact_access():
    module = wizard_module()
    machine = {"recommended_local_tier": "none"}
    profile = {"subscriptions": {"chatgpt": True, "claude": True}, "astra_available": True,
               "app_quality_first": True, "claude_extra_usage_off": True, "opus_available": True}
    route = module.routing(profile, machine)
    assert "Astra Medium" in route["app_implementation"]
    assert "pending" in route["app_review"]
    profile.update(sol_current_available=True, opus_current_available=True)
    route = module.routing(profile, machine)
    assert "GPT-6.1 Sol Medium" in route["app_implementation"]
    assert "claude-opus-5-5" in route["app_review"]
    assert "pending" not in route["app_review"]
    assert "Astra High" in route["app_implementation"]
    profile["claude_extra_usage_off"] = False
    assert "pending" in module.routing(profile, machine)["app_review"]
    profile["subscriptions"] = {}
    assert "pending" in module.routing(profile, machine)["app_implementation"]
    profile["app_quality_first"] = False
    assert "not selected" in module.routing(profile, machine)["app_implementation"]


def test_sol_access_does_not_declare_astra_and_disabled_profile_is_quiet():
    module=wizard_module()
    profile={"name":"Tester","role":"developer","goals":[],"stack":[],"privacy":"internal",
             "subscriptions":{"chatgpt":True},"sol_current_available":True,"app_quality_first":True}
    route=module.routing(profile,{"recommended_local_tier":"none"})
    assert "Astra access pending" in route["app_implementation"]
    assert "Astra Medium" not in route["app_implementation"]
    profile['app_quality_first']=False
    plan={"recommended_skills":[],"routing":module.routing(profile,{"recommended_local_tier":"none"})}
    for text in [module.compact_instruction(profile,plan),module.web_instruction(profile,plan,"ChatGPT")]:
        assert "App implementation:" not in text
        assert "Opus 5.5" not in text
        assert "Sonnet 5.5" not in text


def test_schema_and_profile_fields_match():
    module=wizard_module()
    schema=json.loads((ROOT/'profile.schema.json').read_text())
    assert set(schema['properties']) == module.PROFILE_FIELDS
    for field in ('app_quality_first','sol_current_available','opus_current_available'):
        assert schema['properties'][field]['default'] is False
        assert schema['properties'][field]['type'] == 'boolean'


def test_app_profile_validation_and_old_profile_compatibility():
    module = wizard_module()
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "profile.json"
        path.write_text("{}")
        old = module.read_profile(path, False)
        for field in ("app_quality_first", "sol_current_available", "opus_current_available"):
            assert old[field] is False
            path.write_text(json.dumps({field: "yes"}))
            try:
                module.read_profile(path, False)
            except ValueError:
                pass
            else:
                raise AssertionError("Non-boolean access must fail")


def test_app_guidance_reaches_ide_and_web_without_privacy_override():
    module = wizard_module()
    profile = {"name": "Tester", "role": "developer", "goals": [], "stack": [],
               "privacy": "confidential", "subscriptions": {"chatgpt": True, "claude": True},
               "app_quality_first": True, "sol_current_available": True,
               "opus_current_available": True, "claude_extra_usage_off": True}
    plan = {"recommended_skills": [], "routing": module.routing(profile, {"recommended_local_tier": "none"})}
    outputs = [module.compact_instruction(profile, plan)]
    outputs += [module.web_instruction(profile, plan, platform) for platform in ("ChatGPT", "Claude")]
    for text in outputs:
        assert "GPT-6.1 Sol Medium" in text
        assert "claude-opus-5-5" in text
        assert "24 hours" in text
        assert "project-specific approval" in text
        assert "Design evidence" in text
        assert "no model guarantees" in text.lower()
        assert len(text.split()) <= 3000
        import re
        assert not re.search(r"/Users/|/private/var/|[A-Za-z]:\\Users\\|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", text)
        for private_term in ("private-client-evidence", "personal-account-receipt", "ANTHROPIC_API_KEY", "api_key"):
            assert private_term not in text


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS - {test.__name__}")
