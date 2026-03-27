#!/usr/bin/env python3
"""
Harness Skill — Project Analyzer.
Scans a project directory and produces a structured JSON report:
language, framework, existing tooling, module map, harness gaps.
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "env", ".env",
    "dist", "build", ".next", ".nuxt", "target", "vendor", ".tox",
    ".mypy_cache", ".ruff_cache", ".pytest_cache", "site-packages",
    ".cache", "coverage", ".coverage", "htmlcov",
}

EXT_TO_LANG = {
    ".py": "python", ".js": "javascript", ".ts": "typescript",
    ".tsx": "typescript-react", ".jsx": "javascript-react",
    ".go": "go", ".rs": "rust", ".java": "java", ".kt": "kotlin",
    ".rb": "ruby", ".php": "php", ".cs": "csharp", ".cpp": "cpp",
    ".c": "c", ".swift": "swift", ".scala": "scala", ".ex": "elixir",
    ".exs": "elixir", ".hs": "haskell", ".lua": "lua", ".dart": "dart",
    ".vue": "vue", ".svelte": "svelte",
}

SOURCE_EXTS = set(EXT_TO_LANG.keys())


def _walk(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        yield Path(dirpath), dirnames, filenames


def _read(path: Path) -> str:
    try:
        return path.read_text(errors="ignore")
    except Exception:
        return ""


# ── Language detection ────────────────────────────────────────────────

def detect_languages(root: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    for dirpath, _, filenames in _walk(root):
        for f in filenames:
            if lang := EXT_TO_LANG.get(Path(f).suffix.lower()):
                counts[lang] = counts.get(lang, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: -x[1]))


# ── Package manager ──────────────────────────────────────────────────

def detect_package_manager(root: Path) -> dict[str, Any]:
    checks = [
        ("uv",      "pyproject.toml", "uv.lock"),
        ("poetry",  "pyproject.toml", "poetry.lock"),
        ("pip",     "requirements.txt", None),
        ("pipenv",  "Pipfile",        "Pipfile.lock"),
        ("pnpm",    "package.json",   "pnpm-lock.yaml"),
        ("yarn",    "package.json",   "yarn.lock"),
        ("bun",     "package.json",   "bun.lockb"),
        ("npm",     "package.json",   "package-lock.json"),
        ("cargo",   "Cargo.toml",     "Cargo.lock"),
        ("go",      "go.mod",         "go.sum"),
        ("gradle",  "build.gradle",   None),
        ("maven",   "pom.xml",        None),
        ("mix",     "mix.exs",        "mix.lock"),
        ("bundler", "Gemfile",        "Gemfile.lock"),
        ("composer","composer.json",   "composer.lock"),
    ]
    for mgr, deps, lock in checks:
        if not (root / deps).exists():
            continue
        # Extra checks for python managers
        if mgr == "uv" and not (root / "uv.lock").exists():
            continue
        if mgr == "poetry" and "[tool.poetry]" not in _read(root / deps):
            continue
        # For JS: require specific lockfile
        if mgr in ("pnpm", "yarn", "bun") and (lock and not (root / lock).exists()):
            continue
        return {
            "manager": mgr,
            "deps_file": deps,
            "lockfile": lock if lock and (root / lock).exists() else None,
        }
    return {"manager": None, "deps_file": None, "lockfile": None}


# ── Framework detection ──────────────────────────────────────────────

def detect_framework(root: Path) -> str | None:
    # Fast checks on specific config files first
    fast = [
        ("nextjs",   ["next.config.js", "next.config.mjs", "next.config.ts"]),
        ("nuxt",     ["nuxt.config.js", "nuxt.config.ts"]),
        ("sveltekit",["svelte.config.js"]),
    ]
    for fw, files in fast:
        if any((root / f).exists() for f in files):
            return fw

    # Content-based checks
    content_checks: list[tuple[str, str, str]] = [
        ("fastapi",  "pyproject.toml", r"fastapi"),
        ("django",   "manage.py",      r"django"),
        ("flask",    "pyproject.toml",  r"flask"),
        ("express",  "package.json",   r"\"express\""),
        ("react",    "package.json",   r"\"react\""),
        ("vue",      "package.json",   r"\"vue\""),
        ("svelte",   "package.json",   r"\"svelte\""),
        ("rails",    "Gemfile",        r"rails"),
        ("spring",   "pom.xml",        r"spring-boot"),
        ("spring",   "build.gradle",   r"spring-boot"),
        ("gin",      "go.mod",         r"github\.com/gin-gonic"),
        ("echo",     "go.mod",         r"github\.com/labstack/echo"),
        ("fiber",    "go.mod",         r"github\.com/gofiber/fiber"),
        ("actix",    "Cargo.toml",     r"actix-web"),
        ("axum",     "Cargo.toml",     r"axum"),
        ("rocket",   "Cargo.toml",     r"rocket"),
        ("phoenix",  "mix.exs",        r"phoenix"),
        ("laravel",  "composer.json",  r"laravel"),
    ]
    for fw, file, pattern in content_checks:
        p = root / file
        if p.exists() and re.search(pattern, _read(p)):
            return fw

    # Scan source files for framework imports (slower, last resort)
    py_imports = [
        ("fastapi", r"from\s+fastapi"),
        ("django",  r"from\s+django"),
        ("flask",   r"from\s+flask"),
    ]
    for dirpath, _, filenames in _walk(root):
        for f in filenames:
            if f.endswith(".py"):
                content = _read(Path(dirpath) / f)
                for fw, pattern in py_imports:
                    if re.search(pattern, content):
                        return fw
    return None


# ── Tooling detection ────────────────────────────────────────────────

def detect_tooling(root: Path) -> dict[str, Any]:
    t: dict[str, Any] = {
        "linters": [], "formatters": [], "test_framework": None,
        "type_checker": None, "ci": None, "docker": False,
        "makefile": False, "pre_commit": False,
    }

    # Config file → tool mapping
    tool_map = {
        ".eslintrc": ("eslint", "linters"), ".eslintrc.js": ("eslint", "linters"),
        ".eslintrc.json": ("eslint", "linters"), "eslint.config.js": ("eslint", "linters"),
        "eslint.config.mjs": ("eslint", "linters"), "biome.json": ("biome", "linters"),
        ".prettierrc": ("prettier", "formatters"), ".prettierrc.json": ("prettier", "formatters"),
        "prettier.config.js": ("prettier", "formatters"),
        "ruff.toml": ("ruff", "linters"), ".flake8": ("flake8", "linters"),
        ".rubocop.yml": ("rubocop", "linters"), "rustfmt.toml": ("rustfmt", "formatters"),
        ".golangci.yml": ("golangci-lint", "linters"), ".golangci.yaml": ("golangci-lint", "linters"),
    }
    for fname, (tool, cat) in tool_map.items():
        if (root / fname).exists() and tool not in t[cat]:
            t[cat].append(tool)

    # pyproject.toml tool sections
    pyp = _read(root / "pyproject.toml")
    if pyp:
        for section, tool, cat in [
            ("[tool.ruff]", "ruff", "linters"), ("[tool.black]", "black", "formatters"),
            ("[tool.isort]", "isort", "formatters"), ("[tool.mypy]", "mypy", "type_checker"),
            ("[tool.pyright]", "pyright", "type_checker"),
        ]:
            if section in pyp:
                if cat == "type_checker":
                    t[cat] = tool
                elif tool not in t[cat]:
                    t[cat].append(tool)

    # Test frameworks
    test_checks = [
        ("pytest",     ["conftest.py", "pytest.ini"], r"pytest"),
        ("vitest",     ["vitest.config.ts", "vitest.config.js"], r""),
        ("jest",       ["jest.config.js", "jest.config.ts"], r""),
        ("mocha",      [".mocharc.yml", ".mocharc.json"], r""),
        ("rspec",      [".rspec"], r""),
        ("go-test",    ["go.mod"], r""),
        ("cargo-test", ["Cargo.toml"], r""),
        ("exunit",     ["mix.exs"], r""),
    ]
    for fw, files, _ in test_checks:
        if any((root / f).exists() for f in files):
            t["test_framework"] = fw
            break
    # Fallback: check pyproject for pytest
    if not t["test_framework"] and "pytest" in pyp:
        t["test_framework"] = "pytest"
    # Fallback: check package.json for test frameworks
    if not t["test_framework"]:
        pkg = _read(root / "package.json")
        for fw, pattern in [("vitest", r"vitest"), ("jest", r"jest"), ("mocha", r"mocha")]:
            if re.search(pattern, pkg):
                t["test_framework"] = fw
                break

    # Type checkers (if not found yet)
    if not t["type_checker"]:
        if (root / "mypy.ini").exists(): t["type_checker"] = "mypy"
        elif (root / "pyrightconfig.json").exists(): t["type_checker"] = "pyright"
        elif (root / "tsconfig.json").exists(): t["type_checker"] = "typescript"

    # CI
    ci_map = [
        (".github/workflows", "github-actions"), (".gitlab-ci.yml", "gitlab-ci"),
        ("Jenkinsfile", "jenkins"), (".circleci", "circleci"),
        (".travis.yml", "travis"), ("bitbucket-pipelines.yml", "bitbucket"),
    ]
    for path, ci in ci_map:
        if (root / path).exists():
            t["ci"] = ci
            break

    t["docker"] = any((root / f).exists() for f in ["Dockerfile", "docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"])
    t["makefile"] = (root / "Makefile").exists()
    t["pre_commit"] = (root / ".pre-commit-config.yaml").exists()

    return t


# ── Module map ───────────────────────────────────────────────────────

def map_modules(root: Path) -> list[dict[str, Any]]:
    src_candidates = ["src", "lib", "app", "pkg", "internal", "cmd", "server", "api", "core"]
    modules = []

    # Check for a clear src-like directory
    for src in src_candidates:
        src_path = root / src
        if src_path.is_dir():
            for child in sorted(src_path.iterdir()):
                if child.is_dir() and child.name not in SKIP_DIRS and not child.name.startswith("."):
                    n = sum(1 for _ in child.rglob("*") if _.is_file() and _.suffix in SOURCE_EXTS)
                    if n > 0:
                        modules.append({"path": str(child.relative_to(root)), "name": child.name, "files": n})
            if modules:
                return modules

    # Fallback: top-level directories with source code
    for child in sorted(root.iterdir()):
        if child.is_dir() and child.name not in SKIP_DIRS and not child.name.startswith("."):
            if child.name in ("tests", "test", "spec", "__tests__", "docs", "scripts", ".hooks"):
                continue
            n = sum(1 for _ in child.rglob("*") if _.is_file() and _.suffix in SOURCE_EXTS)
            if n > 0:
                modules.append({"path": child.name, "name": child.name, "files": n})
    return modules


# ── Existing harness detection ───────────────────────────────────────

def detect_harness(root: Path) -> dict[str, bool]:
    return {
        "claude_md":        (root / "CLAUDE.md").exists(),
        "agents_md":        (root / "AGENTS.md").exists(),
        "copilot_md":       (root / ".github" / "copilot-instructions.md").exists(),
        "claude_settings":  (root / ".claude" / "settings.json").exists(),
        "claude_commands":  (root / ".claude" / "commands").is_dir(),
        "docs_dir":         (root / "docs").is_dir(),
        "architecture_md":  (root / "docs" / "architecture.md").exists(),
        "golden_rules":     (root / "docs" / "golden-rules.md").exists(),
        "features_md":      (root / "docs" / "features.md").exists(),
        "progress_json":    (root / "docs" / "progress.json").exists(),
        "progress_md":      (root / "docs" / "progress.md").exists(),
        "verify_script":    any((root / "scripts" / f"verify.{e}").exists() for e in ("sh", "py", "bash")),
    }


# ── Makefile targets ─────────────────────────────────────────────────

def makefile_targets(root: Path) -> list[str]:
    mf = root / "Makefile"
    if not mf.exists():
        return []
    return re.findall(r"^([a-zA-Z_][\w-]*)\s*:", _read(mf), re.MULTILINE)


# ── Greenfield heuristic ─────────────────────────────────────────────

def is_greenfield(root: Path) -> bool:
    count = 0
    for _, _, filenames in _walk(root):
        for f in filenames:
            if Path(f).suffix in SOURCE_EXTS:
                count += 1
            if count > 5:
                return False
    return count <= 5


# ── Main ─────────────────────────────────────────────────────────────

def analyze(root_str: str) -> dict[str, Any]:
    root = Path(root_str).resolve()
    if not root.is_dir():
        return {"error": f"Not a directory: {root_str}"}

    langs = detect_languages(root)
    primary = next(iter(langs), None)
    pkg = detect_package_manager(root)
    fw = detect_framework(root)
    tools = detect_tooling(root)
    mods = map_modules(root)
    harness = detect_harness(root)
    mk_targets = makefile_targets(root)
    gf = is_greenfield(root)

    return {
        "root": str(root),
        "project_name": root.name,
        "is_greenfield": gf,
        "has_git": (root / ".git").is_dir(),
        "has_tests_dir": any((root / d).is_dir() for d in ("tests", "test", "__tests__", "spec")),
        "languages": langs,
        "primary_language": primary,
        "package_manager": pkg,
        "framework": fw,
        "tooling": tools,
        "modules": mods,
        "existing_harness": harness,
        "makefile_targets": mk_targets,
    }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    print(json.dumps(analyze(target), indent=2, ensure_ascii=False))
