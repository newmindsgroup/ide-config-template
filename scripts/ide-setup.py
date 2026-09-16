#!/usr/bin/env python3
"""Create a safe, role-aware, local AI-IDE configuration plan.

The wizard stores non-secret preferences on the current computer. It never reads
credentials, downloads models, enables paid APIs, or modifies configuration until
the caller supplies --apply --confirm.

Version-Timestamp: 2026-09-16 16:02:15 AST
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import os
import stat
import tempfile
import uuid
import json
from pathlib import Path
import platform
import shutil
import socket
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any


MARKER_START = "<!-- IDE-CONFIG-TEMPLATE:START -->"
MARKER_END = "<!-- IDE-CONFIG-TEMPLATE:END -->"
VERSION = "2026-09-16 16:02:15 AST"
ROLES = {"developer", "designer", "writer", "product", "operations", "analyst", "general"}
PRIVACY_LEVELS = {"public", "internal", "confidential"}
IDE_NAMES = {"codex", "claude", "cursor", "antigravity"}
PROFILE_FIELDS = {"$schema", "schema_version", "version_timestamp", "name", "role", "goals", "stack", "privacy", "ides", "subscriptions", "astra_available", "opus_available", "fable_available", "claude_extra_usage_off"}
SUBSCRIPTION_FIELDS = {"chatgpt", "claude", "gemini", "cursor", "openrouter_free"}
FOCUSES = {"general", "llm-routing"}
LLM_ROUTING_GOAL = "Implement a safe LLM routing and fallback strategy for this person and computer."

CATALOG_PATH = Path(__file__).resolve().parents[1] / "approved-skills.json"
CATALOG = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
ROLE_SKILLS = CATALOG["roles"]



def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def command_output(*command: str) -> str | None:
    try:
        return subprocess.check_output(command, text=True, stderr=subprocess.DEVNULL, timeout=5).strip()
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None


def memory_gb() -> int | None:
    if sys.platform == "darwin":
        value = command_output("sysctl", "-n", "hw.memsize")
        return round(int(value) / 1024**3) if value and value.isdigit() else None
    meminfo = Path("/proc/meminfo")
    if meminfo.is_file():
        for line in meminfo.read_text().splitlines():
            if line.startswith("MemTotal:"):
                return round(int(line.split()[1]) / 1024**2)
    return None


def local_tier(ram_gb: int | None, free_disk_gb: int, ollama: bool) -> str:
    if not ollama or ram_gb is None or ram_gb < 16:
        return "none"
    memory_tier = "light" if ram_gb < 32 else "standard" if ram_gb < 64 else "advanced" if ram_gb < 96 else "full"
    disk_tier = "none" if free_disk_gb < 12 else "light" if free_disk_gb < 25 else "standard" if free_disk_gb < 60 else "advanced" if free_disk_gb < 100 else "full"
    return min((memory_tier, disk_tier), key=("none", "light", "standard", "advanced", "full").index)


def scan() -> dict[str, Any]:
    home = Path.home()
    tools = {name: command_exists(name) for name in ("git", "python", "python3", "py", "node", "codex", "claude", "ollama")}
    ram = memory_gb()
    free_disk = round(shutil.disk_usage(home).free / 1024**3)
    return {
        "schema_version": 1,
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "ram_gb": ram,
        "free_disk_gb": free_disk,
        "tools": tools,
        "recommended_local_tier": local_tier(ram, free_disk, tools["ollama"]),
    }


def prompt(question: str, default: str) -> str:
    response = input(f"{question} [{default}]: ").strip()
    return response or default


def choose(question: str, options: set[str], default: str) -> str:
    response = prompt(question, default).lower()
    if response not in options:
        raise ValueError(f"Unsupported answer for {question}: {response}")
    return response


def interview() -> dict[str, Any]:
    print("This collects non-secret preferences only. Do not enter passwords, API keys, or client data.")
    name = prompt("Your name", "Team member")
    role = choose("Role: developer, designer, writer, product, operations, analyst, general", ROLES, "general")
    goals = [item.strip() for item in prompt("Primary goals, comma-separated", "build reliable work").split(",") if item.strip()]
    stack = [item.strip() for item in prompt("Main stack or tools, comma-separated", "varies by project").split(",") if item.strip()]
    privacy = choose("Default data sensitivity: public, internal, confidential", PRIVACY_LEVELS, "internal")
    ides = [item.strip().lower() for item in prompt("Tools: codex, claude, cursor, antigravity, comma-separated", "codex").split(",") if item.strip()]
    if not set(ides) <= IDE_NAMES:
        raise ValueError("Unsupported IDE. Choose codex, claude, cursor, or antigravity.")
    yes_no = {"yes", "no"}
    subscriptions = {
        "chatgpt": choose("ChatGPT subscription available here? yes/no", yes_no, "no") == "yes",
        "claude": choose("Claude subscription available here? yes/no", yes_no, "no") == "yes",
        "gemini": choose("Gemini subscription available here? yes/no", yes_no, "no") == "yes",
        "cursor": choose("Cursor subscription available here? yes/no", yes_no, "no") == "yes",
        "openrouter_free": choose("Enable OpenRouter free-only for public or sanitized work? yes/no", yes_no, "no") == "yes",
    }
    astra_available = subscriptions["chatgpt"] and choose("Have you confirmed Astra is selectable in your Codex account? yes/no", yes_no, "no") == "yes"
    opus_available = subscriptions["claude"] and choose("Confirmed Opus 5 included and selectable on this computer? yes/no", yes_no, "no") == "yes"
    fable_available = subscriptions["claude"] and choose("Confirmed Fable 5.1 included and selectable on this computer? yes/no", yes_no, "no") == "yes"
    extra_off = subscriptions["claude"] and choose("Confirmed Claude extra usage and usage-credit billing disabled? yes/no", yes_no, "no") == "yes"
    return {"name": name, "role": role, "goals": goals, "stack": stack, "privacy": privacy, "ides": ides, "subscriptions": subscriptions, "astra_available": astra_available, "opus_available": opus_available, "fable_available": fable_available, "claude_extra_usage_off": extra_off}


def read_profile(path: Path | None, interactive: bool) -> dict[str, Any]:
    profile = interview() if interactive else json.loads(path.read_text(encoding="utf-8")) if path else None
    if not isinstance(profile, dict):
        raise ValueError("Provide --profile for non-interactive use, or omit it for the guided interview.")
    unsupported = set(profile) - PROFILE_FIELDS
    if unsupported:
        raise ValueError(f"Unsupported field in profile: {', '.join(sorted(unsupported))}")
    profile.setdefault("name", "Team member")
    profile.setdefault("schema_version", 1)
    profile.setdefault("version_timestamp", VERSION)
    profile.setdefault("role", "general")
    profile.setdefault("goals", [])
    profile.setdefault("stack", [])
    profile.setdefault("privacy", "internal")
    profile.setdefault("ides", [])
    profile.setdefault("subscriptions", {})
    profile.setdefault("astra_available", False)
    for field in ("opus_available", "fable_available", "claude_extra_usage_off"):
        profile.setdefault(field, False)
    if (
        not isinstance(profile["astra_available"], bool)
        or any(not isinstance(profile[field], bool) for field in ("opus_available", "fable_available", "claude_extra_usage_off"))
        or not isinstance(profile["role"], str)
        or profile["role"] not in ROLES
        or not isinstance(profile["privacy"], str)
        or profile["privacy"] not in PRIVACY_LEVELS
        or not isinstance(profile["name"], str)
        or type(profile["schema_version"]) is not int
        or profile["schema_version"] != 1
        or not isinstance(profile["version_timestamp"], str)
        or not isinstance(profile["goals"], list)
        or not isinstance(profile["stack"], list)
        or not isinstance(profile["ides"], list)
        or not all(isinstance(value, str) for value in profile["goals"])
        or not all(isinstance(value, str) for value in profile["stack"])
        or not all(isinstance(value, str) for value in profile["ides"])
        or not set(profile["ides"]) <= IDE_NAMES
        or not isinstance(profile["subscriptions"], dict)
        or not set(profile["subscriptions"]) <= SUBSCRIPTION_FIELDS
        or not all(isinstance(value, bool) for value in profile["subscriptions"].values())
    ):
        raise ValueError("Profile contains an unsupported value.")
    for value in [profile["name"], profile["version_timestamp"], *profile["goals"], *profile["stack"]]:
        if len(value) > 2000 or any(token in value for token in ("<!--", "-->", "\x00")):
            raise ValueError("Profile text contains reserved delimiters or exceeds the size limit.")
    return profile


def routing(profile: dict[str, Any], machine: dict[str, Any]) -> dict[str, str]:
    subscriptions = profile["subscriptions"]
    review_enabled = subscriptions.get("claude") and profile.get("claude_extra_usage_off", False)
    hosted = (
        "ChatGPT subscription"
        if subscriptions.get("chatgpt")
        else "Claude subscription"
        if subscriptions.get("claude")
        else "Gemini subscription"
        if subscriptions.get("gemini")
        else "no hosted provider declared"
    )
    return {
        "default": "deterministic tools first, then the smallest safe route",
        "private_work": "local model when installed and suitable" if machine["recommended_local_tier"] != "none" else "approved subscription with minimized context",
        "hosted_default": hosted,
        "substantial_work": "Astra, Low effort, Standard speed; raise to Medium or High on evidence or consequence" if subscriptions.get("chatgpt") and profile.get("astra_available", False) else "best suitable model confirmed in the available subscription; otherwise a suitable installed local model",
        "routine_work": "Terra Medium for routine implementation; Luna Low for narrow hosted work, when available",
        "high_consequence": "raise effort to High only when warranted; keep tests, browser checks and independent review",
        "capacity_fallback": "On shared OpenAI quota exhaustion, checkpoint and use an approved available Claude subscription or suitable local model. Switching OpenAI models does not reset allowance.",
        "automation": "instruction and recommendation only; no quota polling, provider execution or automatic replay",
        "premium_review": "use an available subscription only for high-consequence synthesis or independent review",
        "code_design_review": "Opus 5 Medium after real checks at meaningful code, UI, UX and visual milestones" if review_enabled and profile.get("opus_available") else "pending confirmed included reviewer access, billing and data approval; request an approved substitute",
        "complex_review": "Fable 5.1 High for complex architecture, major design systems, persistent defects and difficult synthesis; review approach and completed milestone" if review_enabled and profile.get("fable_available") else "pending Fable access and billing confirmation; use confirmed Opus only as an explicitly recorded substitute",
        "review_evidence": "requirements, changes and actual check results; desktop/mobile screenshots and changed interaction states for UI. Resolve findings and rerun checks. No model response is release approval.",
        "review_scope": "also review consequential research, client deliverables, strategy, forecasts and automation; use proportionate source, calculation and human checks",
        "substantial_review": "Fable 5.1 Medium for substantial bounded synthesis across coding, design, content, planning and analysis; High for complex or consequential work. Opus 5 for smaller focused reviews." if review_enabled and profile.get("fable_available") else "Use only an explicitly confirmed included reviewer; keep review pending when unavailable.",
        "review_budget": "One reviewer per milestone; at most two attempts per phase, no duplicate unchanged evidence. Stop and checkpoint on persistent failure. This template supplies instructions, not an executable review counter.",
        "context_budget": "Keep essential safety and project rules always loaded; load exact skills on demand. Store approved plans, decisions and checks in project files. Do not delete safeguards or move data to external memory without approval. Reuse a short task brief, not a separate self-prompt. Use prompt-engineering-expert when installed for instruction deliverables, complex handoffs or demonstrated instruction-caused failures, not ordinary coding or tool errors. Refine once, then execute. Recommend Plan mode for unresolved consequential decisions or broad, costly-to-reverse changes; never claim prose switches modes. Resolve consequential decisions with the user before execution, regardless of mode. Planning grants no implementation or deployment authority. Neither planning nor refinement automatically raises effort or calls another model. Real checks remain required.",
        "measurement": "Record opaque task ID, model, effort, acceptance, elapsed time and repairs locally. Add approximate usage deltas only when known. Evaluate ten real tasks without duplicating paid work.",
        "openrouter": "free-only, public or sanitized work" if subscriptions.get("openrouter_free") else "disabled unless explicitly enabled",
        "paid_api_fallback": "never automatic",
        "fast_mode": "only when the person explicitly prioritizes latency",
        "cursor_note": "Cursor subscription requires an in-app model check and is not a provider fallback route." if subscriptions.get("cursor") else "Cursor is not selected as a provider fallback route.",
    }


def make_plan(profile: dict[str, Any], machine: dict[str, Any], focus: str) -> dict[str, Any]:
    role = profile["role"]
    return {
        "schema_version": 1,
        "focus": focus,
        "implementation_goal": LLM_ROUTING_GOAL if focus == "llm-routing" else "Implement a safe personalized AI development environment for this person and computer.",
        "profile": {key: profile[key] for key in ("name", "role", "goals", "stack", "privacy", "ides")},
        "machine": {key: machine[key] for key in ("platform", "architecture", "ram_gb", "free_disk_gb", "tools", "recommended_local_tier")},
        "recommended_skills": ROLE_SKILLS[role],
        "skill_catalog": {"source": CATALOG["source"], "policy": "recommendations only; no installation or removal", "skills": [entry for entry in CATALOG["skills"] if entry["name"] in ROLE_SKILLS[role]]},
        "routing": routing(profile, machine),
        "install_actions": {
            "codex": "managed AGENTS.md block" if "codex" in profile["ides"] else "manual prompt pack only",
            "claude_code": "managed CLAUDE.md block" if "claude" in profile["ides"] else "manual prompt pack only",
            "cursor": "workspace rule" if "cursor" in profile["ides"] else "manual prompt pack only",
            "antigravity": "managed GEMINI.md block" if "antigravity" in profile["ides"] else "manual prompt pack only",
            "web": "copy-ready ChatGPT and Claude instructions",
        },
        "safety": [
            "No credentials, cookies, or API keys are requested or stored.",
            "No paid API fallback is enabled.",
            "No local model is downloaded automatically.",
            "Existing instruction files are backed up before a managed block is added.",
        ],
    }


def compact_instruction(profile: dict[str, Any], plan: dict[str, Any]) -> str:
    goals = ", ".join(profile["goals"]) or "reliable work"
    skills = ", ".join(plan["recommended_skills"]) or "none required by this role; use the approved catalog only when relevant"
    return f"""# Personalized AI Working Instructions

Version-Timestamp: {VERSION}

## Role and objective

Support {profile['name']}, a {profile['role']}. Primary goals: {goals}.
Main stack or tools: {', '.join(profile['stack']) or 'varies by project'}.

## Operating rules

1. Start with deterministic checks, search, tests, formatting, and builds when they answer the question.
2. Treat {profile['privacy']} material as the default data boundary. Do not send it to an unapproved external provider.
3. Select the smallest safe model route. Do not enable paid API fallback or fast mode automatically.
4. Use a relevant skill only when it supplies a concrete method. Suggested skills: {skills}. These are optional recommendations, not installed or automatically authorized. Review the pinned public catalog; keep project-specific and private skills within approved project boundaries.
5. Before claiming work is complete, run the relevant tests or validation and report any gaps.
6. For code and visual changes, validate real rendered behavior when applicable. For public content, ground facts and edit for the intended audience.

## Routing

Substantial work: {plan['routing']['substantial_work']}.
Routine work: {plan['routing']['routine_work']}.
High consequence: {plan['routing']['high_consequence']}.
Capacity fallback: {plan['routing']['capacity_fallback']}
Automation boundary: {plan['routing']['automation']}.
Code and design review: {plan['routing']['code_design_review']}.
Complex review: {plan['routing']['complex_review']}.
Review evidence: {plan['routing']['review_evidence']}
Extended review: {plan['routing']['review_scope']}.
Substantial review: {plan['routing']['substantial_review']}
Review budget: {plan['routing']['review_budget']}
Context budget: {plan['routing']['context_budget']}
Measurement: {plan['routing']['measurement']}

## Response contract

State the recommended approach, assumptions, risks, and the next safe action. Ask only questions that would materially change the result. Never request credentials or expose secrets.
"""


def web_instruction(profile: dict[str, Any], plan: dict[str, Any], platform_name: str) -> str:
    return f"""# {platform_name} Instructions for {profile['name']}

Version-Timestamp: {VERSION}

Copy the block below into {platform_name}'s instructions or project settings. Keep it separate from credentials and client records.

```text
Role: Act as a practical AI collaborator for a {profile['role']}.
Objective: Help with {', '.join(profile['goals']) or 'reliable work'}.
Context: Default data sensitivity is {profile['privacy']}. Ask before using an external service for sensitive material.
Requirements: Use deterministic checks before reasoning when possible. Give a direct recommendation first. State assumptions, risks, and validation steps. Use the smallest safe level of effort. Do not claim tests or external facts were verified unless you actually verified them.
Output: Provide an actionable answer, then concise next steps. For implementation, include validation commands. For public-facing content, identify audience and fact gaps first.
Evaluation: The answer is useful when it is accurate, specific, safe with data, and clear about what remains unverified.
Routing: {plan['routing']['substantial_work']}. Web controls differ from Codex; never claim these instructions switch a model automatically.
Context: {plan['routing']['context_budget']}
Review: {plan['routing']['substantial_review']} {plan['routing']['review_budget']}
Measurement: {plan['routing']['measurement']}
```

Routing note: {plan['routing']['default']}. {plan['routing']['openrouter']}.
Codex preference: {plan['routing']['substantial_work']}. Web products use their own available model controls.
Continuity: {plan['routing']['capacity_fallback']}
"""


def managed_block(profile: dict[str, Any], plan: dict[str, Any]) -> str:
    return f"{MARKER_START}\n{compact_instruction(profile, plan)}{MARKER_END}\n"


def safe_path(path: Path) -> Path:
    """Reject links and special files without following them."""
    path = path.absolute()
    for item in [path, *path.parents]:
        if item.is_symlink():
            raise ValueError(f"Symlink requires manual review: {item}")
        if item.exists() and item != path and not item.is_dir():
            raise ValueError(f"Parent is not a directory: {item}")
    if path.exists() and (not path.is_file() or path.stat().st_nlink > 1):
        raise ValueError(f"Expected an unlinked regular file: {path}")
    return path


def anchor(path: Path) -> Path:
    path = path.expanduser().absolute()
    for item in [path, *path.parents]:
        if item.is_symlink():
            # macOS supplies these root aliases. No user-created aliases are followed.
            allowed = sys.platform == "darwin" and str(item) in ("/var", "/tmp", "/etc") and item.resolve() == Path("/private") / item.name
            if not allowed:
                raise ValueError(f"Home/workspace ancestor is a symlink: {item}")
    return path.resolve()


def marker_span(text: str) -> tuple[int, int] | None:
    starts = text.count(MARKER_START)
    ends = text.count(MARKER_END)
    if not starts and not ends:
        return None
    if starts != 1 or ends != 1:
        raise ValueError("Expected exactly one complete managed marker pair")
    start, end = text.index(MARKER_START), text.index(MARKER_END)
    if start > end or (start and text[start-1] != "\n") or (end and text[end-1] != "\n"):
        raise ValueError("Managed markers must be ordered and on separate lines")
    end += len(MARKER_END)
    if text[end:end+2] == "\r\n":
        end += 2
    elif text[end:end+1] == "\n":
        end += 1
    elif end != len(text):
        raise ValueError("Managed end marker must end its line")
    if text[start+len(MARKER_START):start+len(MARKER_START)+1] not in ("\r", "\n"):
        raise ValueError("Managed start marker must end its line")
    return start, end


def merged_content(path: Path, block: str, cursor: bool = False) -> bytes:
    safe_path(path)
    original = path.read_bytes().decode("utf-8") if path.exists() else ""
    span = marker_span(original)
    if span:
        return (original[:span[0]] + block + original[span[1]:]).encode("utf-8")
    header = "---\ndescription: Portable operating rules\nalwaysApply: true\n---\n\n" if cursor else ""
    if cursor and path.exists():
        if original != header:
            raise ValueError("Existing Cursor rule is not managed by this template; choose manual setup")
        original = ""  # Exact empty scaffold left by our removal can be reused.
    return (header + block + original).encode("utf-8")


def atomic_write(path: Path, data: bytes, mode: int) -> None:
    safe_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".ide-config-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def commit_changes(changes: dict[Path, bytes], home: Path, expected_hashes: dict[Path, str | None] | None = None) -> list[Path]:
    """Preflight every path, save private recovery copies, rollback ordinary failures.

    Not a cross-file power-loss transaction. Run without concurrent editors.
    """
    root = home / ".ide-config"
    backup_root = root / "backups"
    safe_path(root / "placeholder")
    safe_path(backup_root / "placeholder")
    snapshots = {}
    for path, data in changes.items():
        safe_path(path)
        before = path.read_bytes() if path.exists() else None
        if expected_hashes is not None and (hashlib.sha256(before).hexdigest() if before is not None else None) != expected_hashes[path]:
            raise ValueError("Destination changed after preview; no writes performed")
        if before != data:
            snapshots[path] = (before, stat.S_IMODE(path.stat().st_mode) if before is not None else 0o600)
    if not snapshots:
        return []
    run = backup_root / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:12])
    run.mkdir(parents=True, mode=0o700)
    os.chmod(run, 0o700)
    journal = []
    for number, (path, (before, mode)) in enumerate(snapshots.items()):
        copy = f"{number:03d}.bak" if before is not None else None
        if copy:
            atomic_write(run / copy, before, 0o600)
        journal.append({"path": str(path), "backup": copy, "mode": mode})
    atomic_write(run / "manifest.json", (json.dumps({"version_timestamp": VERSION, "files": journal}, indent=2) + "\n").encode(), 0o600)
    written = []
    try:
        for path, (before, mode) in snapshots.items():
            safe_path(path)
            if (path.read_bytes() if path.exists() else None) != before:
                raise ValueError("Destination changed during apply; stop concurrent editors")
            atomic_write(path, changes[path], mode)
            written.append(path)
    except (OSError, ValueError) as error:
        failures = []
        for path in reversed(written):
            before, mode = snapshots[path]
            try:
                if path.read_bytes() != changes[path]:
                    raise ValueError("Destination changed after write; preserve later edits")
                if before is None:
                    path.unlink()
                else:
                    atomic_write(path, before, mode)
            except (OSError, ValueError) as recovery_error:
                failures.append(str(recovery_error))
        if failures:
            raise OSError(f"Apply failed; recovery incomplete. Inspect {run}") from error
        raise
    return written


def app_roots(home: Path, overrides: dict[str, Path] | None = None, use_env: bool | None = None, selected: list[str] | None = None) -> dict[str, Path]:
    if use_env is None:
        use_env = home == Path.home().resolve()
    overrides = overrides or {}
    roots = {}
    for ide, folder, variable in (("codex", ".codex", "CODEX_HOME"), ("claude", ".claude", "CLAUDE_CONFIG_DIR")):
        if selected is not None and ide not in selected:
            roots[ide] = home / folder
            continue
        chosen = overrides.get(ide) or (os.environ.get(variable) if use_env else None) or home / folder
        candidate = Path(chosen).expanduser()
        if not candidate.is_absolute():
            raise ValueError(f"{variable} or its explicit override must be an absolute directory")
        roots[ide] = anchor(candidate)
    roots["antigravity"] = home / ".gemini"
    return roots


def instruction_targets(profile: dict[str, Any], home: Path, workspace: Path | None,
                        roots: dict[str, Path] | None = None) -> list[tuple[Path, bool]]:
    roots = roots or app_roots(home, selected=profile["ides"])
    targets = []
    for ide, filename in (("codex", "AGENTS.md"), ("claude", "CLAUDE.md"), ("antigravity", "GEMINI.md")):
        if ide in profile["ides"]:
            targets.append((roots[ide] / filename, False))
    if "cursor" in profile["ides"] and workspace:
        targets.append((workspace / ".cursor/rules/ide-config-template.mdc", True))
    return targets


def adapter_for(path: Path) -> str | None:
    if path.name == "ide-config-template.mdc" and path.parent.name == "rules" and path.parent.parent.name == ".cursor":
        return "cursor"
    return {"AGENTS.md": "codex", "CLAUDE.md": "claude", "GEMINI.md": "antigravity"}.get(path.name)


def validate_entry(entry: Any) -> Path:
    if not isinstance(entry, dict) or set(entry) != {"path", "adapter"} or not isinstance(entry["path"], str):
        raise ValueError("Invalid installation record entry")
    path = Path(entry["path"])
    if not path.is_absolute() or ".." in path.parts or adapter_for(path) != entry["adapter"] or entry["adapter"] not in IDE_NAMES:
        raise ValueError("Invalid installation record destination")
    if anchor(path.parent) / path.name != path:
        raise ValueError("Installation record destination must be canonical")
    return safe_path(path)


def installations(home: Path) -> dict[Path, str]:
    """Read local state without writing. Recover old default adapters from backups."""
    registry = safe_path(home / ".ide-config/installations.json")
    records = {}
    if registry.exists():
        value = json.loads(registry.read_text(encoding="utf-8"))
        if not isinstance(value, dict) or value.get("schema_version") != 1 or type(value.get("schema_version")) is not int or not isinstance(value.get("destinations"), list):
            raise ValueError("Invalid installation record; preserve it and recover manually")
        if value.get("installation_home") != str(home):
            raise ValueError("Installation record belongs to another home. Do not copy runtime state between computers.")
        for entry in value["destinations"]:
            path = validate_entry(entry)
            if path in records:
                raise ValueError("Duplicate installation record destination")
            records[path] = entry["adapter"]
        return records
    # Older releases had no registry. Only old default adapter layouts are adopted.
    # In particular, a spine updater's arbitrary AGENTS.md is never an app target.
    candidates = {home / ".codex/AGENTS.md", home / ".claude/CLAUDE.md", home / ".gemini/GEMINI.md"}
    backups = home / ".ide-config/backups"
    safe_path(backups / "placeholder")
    if backups.exists():
        for manifest in sorted(backups.glob("*/manifest.json")):
            safe_path(manifest)
            value = json.loads(manifest.read_text(encoding="utf-8"))
            if not isinstance(value, dict) or not isinstance(value.get("files"), list):
                raise ValueError("Invalid legacy backup manifest; recover manually")
            for item in value["files"]:
                if not isinstance(item, dict) or not isinstance(item.get("path"), str):
                    raise ValueError("Invalid legacy backup destination")
                candidate = Path(item["path"])
                if adapter_for(candidate) == "cursor" or candidate in candidates:
                    validate_entry({"path": str(candidate), "adapter": adapter_for(candidate)})
                    candidates.add(candidate)
    for path in sorted(candidates):
        # Discovery never follows links in unused default app locations. Selected
        # destinations and explicit records are still strictly rejected above.
        if any(item.is_symlink() for item in [path, *path.parents]):
            continue
        safe_path(path)
        if path.exists() and marker_span(path.read_bytes().decode("utf-8")):
            records[path] = adapter_for(path)
    return records


def registry_bytes(records: dict[Path, str], home: Path) -> bytes:
    value = {"schema_version": 1, "version_timestamp": VERSION, "installation_home": str(home),
             "destinations": [{"path": str(path), "adapter": records[path]} for path in sorted(records)]}
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def planned_changes(profile: dict[str, Any], plan: dict[str, Any], home: Path, workspace: Path | None,
                    roots: dict[str, Path] | None = None) -> dict[Path, bytes]:
    root = home / ".ide-config"
    manual = root / "manual"
    records = installations(home)
    # Capacity readings are ephemeral. Do not rewrite persisted files or invalidate
    # an approved diff solely because free disk changed between plan and apply.
    saved_plan = {key: value for key, value in plan.items() if key != "machine"}
    changes = {
        root / "profile.local.json": (json.dumps(profile, indent=2, sort_keys=True) + "\n").encode(),
        root / "plan.json": (json.dumps(saved_plan, indent=2, sort_keys=True) + "\n").encode(),
        manual / "chatgpt-custom-instructions.md": web_instruction(profile, plan, "ChatGPT").encode(),
        manual / "claude-web-project-instructions.md": web_instruction(profile, plan, "Claude").encode(),
        manual / "task-routing-guide.md": ("# Personal Task Routing Guide\n\nVersion-Timestamp: " + VERSION + "\n\n" + json.dumps(plan["routing"], indent=2) + "\n").encode(),
    }
    for path, cursor in instruction_targets(profile, home, workspace, roots):
        changes[path] = merged_content(path, managed_block(profile, plan), cursor)
        records[path] = adapter_for(path)
    if "cursor" in profile["ides"] and not workspace:
        changes[manual / "cursor-user-rules.md"] = compact_instruction(profile, plan).encode()
    # State is written last, in the same rollback boundary as instructions.
    changes[root / "installations.json"] = registry_bytes(records, home)
    for path in changes:
        safe_path(path)
    safe_path(root / "backups/placeholder")
    return changes


def removal_changes(profile: dict[str, Any], home: Path, workspace: Path | None,
                    roots: dict[str, Path] | None = None) -> dict[Path, bytes]:
    records = installations(home)
    for path, _ in instruction_targets(profile, home, workspace, roots):
        records[path] = adapter_for(path)
    changes = {}
    for path in sorted(records):
        safe_path(path)
        original = path.read_bytes().decode("utf-8") if path.exists() else ""
        span = marker_span(original)
        if span:
            changes[path] = (original[:span[0]] + original[span[1]:]).encode("utf-8")
    registry = home / ".ide-config/installations.json"
    if changes or registry.exists():
        changes[registry] = registry_bytes({}, home)
    return changes


def preview_changes(changes: dict[Path, bytes], operation: str) -> dict[str, Any]:
    entries = []
    for path, after in sorted(changes.items()):
        safe_path(path)
        before = path.read_bytes() if path.exists() else None
        diff = "".join(difflib.unified_diff(
            (before or b"").decode("utf-8").splitlines(keepends=True),
            after.decode("utf-8").splitlines(keepends=True),
            fromfile=str(path) + " (before)", tofile=str(path) + " (after)"))
        entries.append({"path": str(path), "action": "unchanged" if before == after else "create" if before is None else "update",
                        "before_sha256": hashlib.sha256(before).hexdigest() if before is not None else None,
                        "after_sha256": hashlib.sha256(after).hexdigest(), "diff": diff})
    bound = {"operation": operation, "files": [{key: value for key, value in entry.items() if key != "diff"} for entry in entries]}
    return {"operation": operation, "planned_files": [str(path) for path in changes], "changes": entries,
            "plan_sha256": hashlib.sha256(json.dumps(bound, sort_keys=True).encode()).hexdigest(),
            "privacy_notice": "Diffs include existing local instructions. Keep this preview private."}


def commit_reviewed(changes: dict[Path, bytes], home: Path, operation: str, expected: str | None = None) -> list[Path]:
    preview = preview_changes(changes, operation)
    if expected is not None and (len(expected) != 64 or any(c not in "0123456789abcdef" for c in expected) or expected != preview["plan_sha256"]):
        raise ValueError("Reviewed plan does not match current changes. Preview again before applying.")
    before_hashes = {Path(entry["path"]): entry["before_sha256"] for entry in preview["changes"]}
    return commit_changes(changes, home, before_hashes)


def apply(profile: dict[str, Any], plan: dict[str, Any], home: Path, workspace: Path | None,
          roots: dict[str, Path] | None = None, expected: str | None = None) -> list[Path]:
    home, workspace = anchor(home), anchor(workspace) if workspace else None
    return commit_reviewed(planned_changes(profile, plan, home, workspace, roots), home, "apply", expected)


def remove_managed_blocks(profile: dict[str, Any], home: Path, workspace: Path | None,
                          roots: dict[str, Path] | None = None, expected: str | None = None) -> list[Path]:
    home, workspace = anchor(home), anchor(workspace) if workspace else None
    return commit_reviewed(removal_changes(profile, home, workspace, roots), home, "remove", expected)


def installation_status(home: Path) -> dict[str, Any]:
    rows = []
    for path, adapter in installations(home).items():
        safe_path(path)
        state = "missing" if not path.exists() else "present" if marker_span(path.read_bytes().decode("utf-8")) else "block_missing"
        rows.append({"path": str(path), "adapter": adapter, "state": state})
    return {"destinations": rows, "app_loading_verified": False,
            "next_step": "Start each app and verify its instruction sources. This checks files only."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--scan", action="store_true", help="print non-secret machine capability information")
    mode.add_argument("--plan", action="store_true", help="print recommendations without writing files")
    mode.add_argument("--plan-remove", action="store_true", help="preview removal from all tracked destinations without writing")
    mode.add_argument("--status", action="store_true", help="check tracked instruction files without launching apps")
    mode.add_argument("--apply", action="store_true", help="write approved local configuration and prompt packs")
    mode.add_argument("--remove-managed-block", action="store_true", help="remove only this template's marked instruction blocks")
    parser.add_argument("--profile", type=Path, help="non-secret JSON profile for plan or non-interactive apply")
    parser.add_argument("--focus", choices=sorted(FOCUSES), default="general", help="limit the plan to a named implementation goal")
    parser.add_argument("--home", type=Path, help="home directory to configure")
    parser.add_argument("--codex-home", type=Path, help="explicit Codex configuration directory")
    parser.add_argument("--claude-home", type=Path, help="explicit Claude Code configuration directory")
    parser.add_argument("--expect-plan-sha256", help="require the exact hash printed by plan or plan-remove")
    parser.add_argument("--workspace", type=Path, help="workspace where a Cursor rule may be created")
    parser.add_argument("--non-interactive", action="store_true", help="require --profile instead of asking questions")
    parser.add_argument("--confirm", action="store_true", help="confirm a requested write or managed-block removal")
    args = parser.parse_args()
    explicit_home = args.home is not None
    args.home = anchor(args.home or Path.home())
    workspace = anchor(args.workspace) if args.workspace else None
    if args.status:
        status = installation_status(args.home)
        print(json.dumps(status, indent=2))
        return 1 if any(row["state"] != "present" for row in status["destinations"]) else 0
    machine = scan()
    if args.scan:
        print(json.dumps(machine, indent=2, sort_keys=True))
        return 0
    if (args.apply or args.remove_managed_block) and not args.confirm:
        print("ERROR - --apply and --remove-managed-block require --confirm after reviewing the plan.", file=sys.stderr)
        return 2
    if (args.remove_managed_block or args.plan_remove) and args.profile is None:
        saved = args.home / ".ide-config" / "profile.local.json"
        args.profile = saved if saved.exists() else None
    try:
        profile = {"ides": []} if (args.remove_managed_block or args.plan_remove) and args.profile is None else read_profile(args.profile, not args.non_interactive and args.profile is None)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR - {error}", file=sys.stderr)
        return 2
    roots = app_roots(args.home, {key: value for key, value in {"codex": args.codex_home, "claude": args.claude_home}.items() if value is not None}, use_env=not explicit_home, selected=profile["ides"])
    if args.plan_remove:
        print(json.dumps(preview_changes(removal_changes(profile, args.home, workspace, roots), "remove"), indent=2))
        return 0
    if args.remove_managed_block:
        outputs = remove_managed_blocks(profile, args.home, workspace, roots, args.expect_plan_sha256)
        for output in outputs:
            print(f"UPDATED - {output}")
        print("BACKUPS - " + str(args.home / ".ide-config" / "backups"))
        return 0
    plan = make_plan(profile, machine, args.focus)
    if args.plan:
        try:
            changes = planned_changes(profile, plan, args.home, workspace, roots)
            plan.update(preview_changes(changes, "apply"))
            plan["tracked_destinations"] = [str(path) for path in installations(args.home)]
        except (OSError, ValueError) as error:
            print(f"ERROR - {error}", file=sys.stderr)
            return 2
        print(json.dumps(plan, indent=2, sort_keys=True))
        return 0
    outputs = apply(profile, plan, args.home, workspace, roots, args.expect_plan_sha256)
    print("APPLIED - local personalized AI configuration")
    for output in outputs:
        print(f"WROTE - {output}")
    print(f"BACKUPS - {args.home / '.ide-config' / 'backups'}")
    print("MANUAL - copy the generated ChatGPT and Claude instructions into the corresponding web product settings.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as error:
        print(f"ERROR - {error}", file=sys.stderr)
        raise SystemExit(2)
