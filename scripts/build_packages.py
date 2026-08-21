#!/usr/bin/env python3
"""Build deterministic Workslop Detector plugin archives."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import zipfile
from pathlib import Path


PLUGIN_NAME = "workslop-detector"
RUNTIME_ROOT = Path("skills/workslop-detector")
RUNTIME_FILES = {
    Path("SKILL.md"),
    Path("agents/arbiter-prompt.md"),
    Path("agents/baseline-responder-prompt.md"),
    Path("agents/cold-reader-prompt.md"),
    Path("references/platform-execution.md"),
    Path("references/tone-guide.md"),
    Path("references/verdict-rubric.md"),
    Path("scripts/scan_ai_residue.py"),
    Path("scripts/validate_agent_output.py"),
}
SHARED_ROOT_FILES = {Path("README.md"), Path("LICENSE"), Path("CHANGELOG.md")}
MANIFESTS = {
    "agent-plugin": Path(".codex-plugin/plugin.json"),
    "claude-plugin": Path(".claude-plugin/plugin.json"),
}
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?$")
UNFINISHED_MARKERS = ("TODO", "TBD", "FIXME", "[TODO:")
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


class PackageError(ValueError):
    """Raised when the release source is unsafe or internally inconsistent."""


def load_manifest(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PackageError(f"Cannot load manifest {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise PackageError(f"Manifest must contain a JSON object: {path}")
    return payload


def validate_archive_name(name: str) -> None:
    path = Path(name)
    if not name or name.startswith(("/", "\\")) or path.is_absolute():
        raise PackageError(f"Unsafe archive path: {name!r}")
    if any(part in ("", ".", "..") for part in path.parts):
        raise PackageError(f"Unsafe archive path: {name!r}")
    if "\\" in name:
        raise PackageError(f"Archive paths must use forward slashes: {name!r}")


def _assert_regular_file(root: Path, relative: Path) -> None:
    path = root / relative
    if not path.exists():
        raise PackageError(f"Missing required file: {relative.as_posix()}")
    if path.is_symlink():
        raise PackageError(f"Symlinks are not allowed: {relative.as_posix()}")
    if not path.is_file():
        raise PackageError(f"Expected a regular file: {relative.as_posix()}")


def _scan_text(path: Path, relative: Path) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return
    for marker in UNFINISHED_MARKERS:
        if marker in text:
            raise PackageError(
                f"Unresolved release marker {marker!r} in {relative.as_posix()}"
            )


def validate_source_tree(root: Path) -> tuple[str, list[Path]]:
    root = root.resolve()
    runtime_dir = root / RUNTIME_ROOT
    if runtime_dir.is_symlink():
        raise PackageError(f"Symlinks are not allowed: {RUNTIME_ROOT.as_posix()}")
    if not runtime_dir.is_dir():
        raise PackageError(f"Missing runtime directory: {RUNTIME_ROOT.as_posix()}")

    actual_runtime: set[Path] = set()
    for path in runtime_dir.rglob("*"):
        relative = path.relative_to(runtime_dir)
        if path.is_symlink():
            raise PackageError(
                f"Symlinks are not allowed: {(RUNTIME_ROOT / relative).as_posix()}"
            )
        if "__pycache__" in relative.parts or relative.name == ".DS_Store":
            continue
        if path.is_file():
            actual_runtime.add(relative)
    if actual_runtime != RUNTIME_FILES:
        missing = sorted(path.as_posix() for path in RUNTIME_FILES - actual_runtime)
        unexpected = sorted(path.as_posix() for path in actual_runtime - RUNTIME_FILES)
        raise PackageError(
            f"Runtime allowlist mismatch; missing={missing}, unexpected={unexpected}"
        )

    manifests: dict[str, dict[str, object]] = {}
    required = set(SHARED_ROOT_FILES)
    required.update(MANIFESTS.values())
    required.update(RUNTIME_ROOT / path for path in RUNTIME_FILES)
    for relative in sorted(required, key=lambda item: item.as_posix()):
        validate_archive_name(relative.as_posix())
        _assert_regular_file(root, relative)
        _scan_text(root / relative, relative)

    for package_type, relative in MANIFESTS.items():
        manifest = load_manifest(root / relative)
        manifests[package_type] = manifest
        if manifest.get("name") != PLUGIN_NAME:
            raise PackageError(f"Wrong plugin name in {relative.as_posix()}")
        if manifest.get("skills") != "./skills/":
            raise PackageError(f"Wrong skills path in {relative.as_posix()}")

    version = manifests["agent-plugin"].get("version")
    if not isinstance(version, str) or SEMVER.fullmatch(version) is None:
        raise PackageError("Agent Plugin version must be strict semantic versioning")
    if manifests["claude-plugin"].get("version") != version:
        raise PackageError("Agent Plugin and Claude manifest versions do not match")

    package_files = sorted(required, key=lambda item: item.as_posix())
    return version, package_files


def _archive_files(package_type: str) -> set[Path]:
    manifest = MANIFESTS[package_type]
    return (
        set(SHARED_ROOT_FILES)
        | {manifest}
        | {RUNTIME_ROOT / path for path in RUNTIME_FILES}
    )


def _write_archive(root: Path, destination: Path, files: set[Path]) -> None:
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for relative in sorted(files, key=lambda item: item.as_posix()):
            name = relative.as_posix()
            validate_archive_name(name)
            info = zipfile.ZipInfo(name, date_time=ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (root / relative).read_bytes())


def _validate_archive(path: Path, expected: set[Path]) -> None:
    expected_names = sorted(item.as_posix() for item in expected)
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if names != expected_names:
            raise PackageError(f"Archive allowlist mismatch in {path.name}")
        for name in names:
            validate_archive_name(name)
            info = archive.getinfo(name)
            if info.date_time != ZIP_TIMESTAMP:
                raise PackageError(f"Non-deterministic timestamp in {path.name}: {name}")
        bad_member = archive.testzip()
        if bad_member is not None:
            raise PackageError(f"Corrupt member in {path.name}: {bad_member}")


def build_archives(root: Path, output_dir: Path) -> tuple[Path, Path]:
    root = root.resolve()
    output_dir = output_dir.resolve()
    version, _ = validate_source_tree(root)
    output_dir.mkdir(parents=True, exist_ok=True)

    names = {
        package_type: f"{PLUGIN_NAME}-{package_type}-{version}.zip"
        for package_type in MANIFESTS
    }
    with tempfile.TemporaryDirectory(prefix=".workslop-build-", dir=output_dir) as tmp:
        temp_dir = Path(tmp)
        temporary: dict[str, Path] = {}
        for package_type in MANIFESTS:
            path = temp_dir / names[package_type]
            files = _archive_files(package_type)
            _write_archive(root, path, files)
            _validate_archive(path, files)
            temporary[package_type] = path

        completed: dict[str, Path] = {}
        for package_type in MANIFESTS:
            destination = output_dir / names[package_type]
            os.replace(temporary[package_type], destination)
            completed[package_type] = destination

    return completed["agent-plugin"], completed["claude-plugin"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    for archive in build_archives(root, root / "dist"):
        print(f"{sha256(archive)}  {archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
