#!/usr/bin/env python3
"""Create a safe, role-aware, local AI-IDE configuration plan.

The wizard stores non-secret preferences on the current computer. It never reads
credentials, downloads models, enables paid APIs, or modifies configuration until
the caller supplies --apply --confirm.

Version-Timestamp: 2026-08-28 12:00:00 AST
"""

from __future__ import annotations

import argparse
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
VERSION = "2026-08-28 12:00:00 AST"
ROLES = {"developer", "designer", "writer", "product", "operations", "analyst", "general"}
PRIVACY_LEVELS = {"public", "internal", "confidential"}
IDE_NAMES = {"codex", "claude", "cursor", "antigravity"}
PROFILE_FIELDS = {"$schema", "schema_version", "version_timestamp", "name", "role", "goals", "stack", "privacy", "ides", "subscriptions"}
SUBSCRIPTION_FIELDS = {"chatgpt", "claude", "gemini", "cursor", "openrouter_free"}
FOCUSES = {"general", "llm-routing"}
LLM_ROUTING_GOAL = "Implement a safe LLM routing and fallback strategy for this person and computer."

ROLE_SKILLS = {
    "developer": ["test-driven-development", "systematic-debugging", "verification-before-completion"],
    "designer": ["visual-and-code-quality-gate", "accessibility-compliance-accessibility-audit"],
    "writer": ["content-development", "copy-editing", "content-quality-gate"],
    "product": ["brainstorming", "writing-plans", "acceptance-orchestrator"],
    "operations": ["agentic-actions-auditor", "acceptance-orchestrator"],
    "analyst": ["data-analysis", "advanced-evaluation"],
    "general": ["verification-before-completion"],
}


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def command_output(*command: str) -> str | None:
    try:
        return subprocess.check_output(command, text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
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
    return {"name": name, "role": role, "goals": goals, "stack": stack, "privacy": privacy, "ides": ides, "subscriptions": subscriptions}


def read_profile(path: Path | None, interactive: bool) -> dict[str, Any]:
    profile = interview() if interactive else json.loads(path.read_text()) if path else None
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
    if (
        profile["role"] not in ROLES
        or profile["privacy"] not in PRIVACY_LEVELS
        or not isinstance(profile["name"], str)
        or not isinstance(profile["schema_version"], int)
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
    return profile


def routing(profile: dict[str, Any], machine: dict[str, Any]) -> dict[str, str]:
    subscriptions = profile["subscriptions"]
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
        "premium_review": "use an available subscription only for high-consequence synthesis or independent review",
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
    skills = ", ".join(plan["recommended_skills"])
    return f"""# Personalized AI Working Instructions

Version-Timestamp: {VERSION}

## Role and objective

Support {profile['name']}, a {profile['role']}. Primary goals: {goals}.
Main stack or tools: {', '.join(profile['stack']) or 'varies by project'}.

## Operating rules

1. Start with deterministic checks, search, tests, formatting, and builds when they answer the question.
2. Treat {profile['privacy']} material as the default data boundary. Do not send it to an unapproved external provider.
3. Select the smallest safe model route. Do not enable paid API fallback or fast mode automatically.
4. Use a relevant skill only when it supplies a concrete method. Suggested skills: {skills}.
5. Before claiming work is complete, run the relevant tests or validation and report any gaps.
6. For code and visual changes, validate real rendered behavior when applicable. For public content, ground facts and edit for the intended audience.

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
```

Routing note: {plan['routing']['default']}. {plan['routing']['openrouter']}.
"""


def managed_block(profile: dict[str, Any], plan: dict[str, Any]) -> str:
    return f"{MARKER_START}\n{compact_instruction(profile, plan)}{MARKER_END}\n"


def backup(path: Path, backup_root: Path) -> None:
    if not path.exists():
        return
    backup_root.mkdir(parents=True, exist_ok=True)
    target = backup_root / path.name
    suffix = 1
    while target.exists():
        target = backup_root / f"{path.stem}-{suffix}{path.suffix}"
        suffix += 1
    shutil.copy2(path, target)


def merge_block(path: Path, block: str, backup_root: Path) -> None:
    if path.is_symlink():
        path = path.resolve()
    original = path.read_text() if path.exists() else ""
    if MARKER_START in original and MARKER_END in original:
        start = original.index(MARKER_START)
        end = original.index(MARKER_END, start) + len(MARKER_END)
        updated = original[:start] + block.rstrip() + original[end:]
    else:
        updated = original.rstrip() + ("\n\n" if original.strip() else "") + block
    if updated != original:
        backup(path, backup_root)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(updated)


def remove_block(path: Path, backup_root: Path) -> bool:
    if path.is_symlink():
        path = path.resolve()
    if not path.exists():
        return False
    original = path.read_text()
    if MARKER_START not in original or MARKER_END not in original:
        return False
    start = original.index(MARKER_START)
    end = original.index(MARKER_END, start) + len(MARKER_END)
    updated = (original[:start] + original[end:]).replace("\n\n\n", "\n\n").strip() + "\n"
    backup(path, backup_root)
    path.write_text(updated)
    return True


def write_local(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    try:
        path.chmod(0o600)
    except OSError:
        pass


def apply(profile: dict[str, Any], plan: dict[str, Any], home: Path, workspace: Path | None) -> list[Path]:
    root = home / ".ide-config"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    backups = root / "backups" / stamp
    outputs: list[Path] = []
    write_local(root / "profile.local.json", json.dumps(profile, indent=2, sort_keys=True) + "\n")
    write_local(root / "plan.json", json.dumps(plan, indent=2, sort_keys=True) + "\n")
    outputs.extend([root / "profile.local.json", root / "plan.json"])
    manual = root / "manual"
    write_local(manual / "chatgpt-custom-instructions.md", web_instruction(profile, plan, "ChatGPT"))
    write_local(manual / "claude-web-project-instructions.md", web_instruction(profile, plan, "Claude"))
    write_local(manual / "task-routing-guide.md", "# Personal Task Routing Guide\n\n" + json.dumps(plan["routing"], indent=2) + "\n")
    outputs.extend([manual / "chatgpt-custom-instructions.md", manual / "claude-web-project-instructions.md", manual / "task-routing-guide.md"])
    block = managed_block(profile, plan)
    if "codex" in profile["ides"]:
        path = home / ".codex" / "AGENTS.md"
        merge_block(path, block, backups)
        outputs.append(path)
    if "claude" in profile["ides"]:
        path = home / ".claude" / "CLAUDE.md"
        merge_block(path, block, backups)
        outputs.append(path)
    if "cursor" in profile["ides"]:
        if workspace:
            path = workspace / ".cursor" / "rules" / "ide-config-template.mdc"
            cursor_block = f"---\ndescription: Personalized team operating rules\nalwaysApply: true\n---\n\n{managed_block(profile, plan)}"
            backup(path, backups)
            write_local(path, cursor_block)
            outputs.append(path)
        else:
            write_local(manual / "cursor-user-rules.md", compact_instruction(profile, plan))
            outputs.append(manual / "cursor-user-rules.md")
    if "antigravity" in profile["ides"]:
        path = home / ".gemini" / "GEMINI.md"
        merge_block(path, block, backups)
        outputs.append(path)
    return outputs


def remove_managed_blocks(profile: dict[str, Any], home: Path, workspace: Path | None) -> list[Path]:
    root = home / ".ide-config"
    backups = root / "backups" / datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    targets: list[Path] = []
    if "codex" in profile["ides"]:
        targets.append(home / ".codex" / "AGENTS.md")
    if "claude" in profile["ides"]:
        targets.append(home / ".claude" / "CLAUDE.md")
    if "antigravity" in profile["ides"]:
        targets.append(home / ".gemini" / "GEMINI.md")
    if "cursor" in profile["ides"] and workspace:
        targets.append(workspace / ".cursor" / "rules" / "ide-config-template.mdc")
    return [path for path in targets if remove_block(path, backups)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--scan", action="store_true", help="print non-secret machine capability information")
    mode.add_argument("--plan", action="store_true", help="print recommendations without writing files")
    mode.add_argument("--apply", action="store_true", help="write approved local configuration and prompt packs")
    mode.add_argument("--remove-managed-block", action="store_true", help="remove only this template's marked instruction blocks")
    parser.add_argument("--profile", type=Path, help="non-secret JSON profile for plan or non-interactive apply")
    parser.add_argument("--focus", choices=sorted(FOCUSES), default="general", help="limit the plan to a named implementation goal")
    parser.add_argument("--home", type=Path, default=Path.home(), help="home directory to configure")
    parser.add_argument("--workspace", type=Path, help="workspace where a Cursor rule may be created")
    parser.add_argument("--non-interactive", action="store_true", help="require --profile instead of asking questions")
    parser.add_argument("--confirm", action="store_true", help="confirm a requested write or managed-block removal")
    args = parser.parse_args()
    machine = scan()
    if args.scan:
        print(json.dumps(machine, indent=2, sort_keys=True))
        return 0
    if (args.apply or args.remove_managed_block) and not args.confirm:
        print("ERROR - --apply and --remove-managed-block require --confirm after reviewing the plan.", file=sys.stderr)
        return 2
    if args.remove_managed_block and args.profile is None:
        args.profile = args.home / ".ide-config" / "profile.local.json"
    try:
        profile = read_profile(args.profile, not args.non_interactive and args.profile is None)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR - {error}", file=sys.stderr)
        return 2
    plan = make_plan(profile, machine, args.focus)
    if args.plan:
        print(json.dumps(plan, indent=2, sort_keys=True))
        return 0
    if args.remove_managed_block:
        outputs = remove_managed_blocks(profile, args.home, args.workspace)
        for output in outputs:
            print(f"REMOVED - managed block from {output}")
        print(f"BACKUPS - {args.home / '.ide-config' / 'backups'}")
        return 0
    outputs = apply(profile, plan, args.home, args.workspace)
    print("APPLIED - local personalized AI configuration")
    for output in outputs:
        print(f"WROTE - {output}")
    print(f"BACKUPS - {args.home / '.ide-config' / 'backups'}")
    print("MANUAL - copy the generated ChatGPT and Claude instructions into the corresponding web product settings.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
