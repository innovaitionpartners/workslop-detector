#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts import build_packages


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.2"
EXPECTED_RUNTIME_FILES = {
    "SKILL.md",
    "agents/arbiter-prompt.md",
    "agents/baseline-responder-prompt.md",
    "agents/cold-reader-prompt.md",
    "references/platform-execution.md",
    "references/tone-guide.md",
    "references/verdict-rubric.md",
    "scripts/scan_ai_residue.py",
    "scripts/validate_agent_output.py",
}


class ManifestTests(unittest.TestCase):
    def load(self, relative_path: str) -> dict:
        return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))

    def test_codex_manifest_has_canonical_metadata(self) -> None:
        manifest = self.load(".codex-plugin/plugin.json")
        self.assertEqual(manifest["name"], "workslop-detector")
        self.assertEqual(manifest["version"], VERSION)
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertEqual(manifest["license"], "MIT")
        self.assertEqual(
            manifest["repository"],
            "https://github.com/innovaitionpartners/workslop-detector",
        )
        prompts = manifest["interface"]["defaultPrompt"]
        self.assertLessEqual(len(prompts), 3)
        self.assertTrue(all(len(prompt) <= 128 for prompt in prompts))

    def test_claude_manifest_points_to_the_same_skill_tree(self) -> None:
        manifest = self.load(".claude-plugin/plugin.json")
        self.assertEqual(manifest["name"], "workslop-detector")
        self.assertEqual(manifest["version"], VERSION)
        self.assertEqual(manifest["skills"], "./skills/")

    def test_shared_manifest_metadata_stays_aligned(self) -> None:
        codex = self.load(".codex-plugin/plugin.json")
        claude = self.load(".claude-plugin/plugin.json")
        for key in (
            "name",
            "version",
            "description",
            "author",
            "homepage",
            "repository",
            "license",
            "keywords",
        ):
            self.assertEqual(codex[key], claude[key], key)


class RuntimeTreeTests(unittest.TestCase):
    def test_runtime_tree_is_exactly_allowlisted(self) -> None:
        skill = ROOT / "skills/workslop-detector"
        actual = {
            path.relative_to(skill).as_posix()
            for path in skill.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        }
        self.assertEqual(actual, EXPECTED_RUNTIME_FILES)

    def test_platform_mapping_has_honest_fallback(self) -> None:
        text = (
            ROOT / "skills/workslop-detector/references/platform-execution.md"
        ).read_text(encoding="utf-8")
        for phrase in (
            "Agent Plugin hosts",
            "Claude Code and Cowork",
            "INCONCLUSIVE",
            "Never simulate",
        ):
            self.assertIn(phrase, text)


class ArchiveTests(unittest.TestCase):
    @staticmethod
    def digest(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def test_archives_have_exact_roots_and_identical_skill_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            agent_path, claude_path = build_packages.build_archives(ROOT, Path(tmp))
            self.assertEqual(
                agent_path.name,
                "workslop-detector-agent-plugin-0.1.2.zip",
            )
            self.assertEqual(
                claude_path.name,
                "workslop-detector-claude-plugin-0.1.2.zip",
            )
            runtime = {
                f"skills/workslop-detector/{name}"
                for name in EXPECTED_RUNTIME_FILES
            }
            agent_roots = {
                ".codex-plugin/plugin.json",
                "README.md",
                "LICENSE",
                "CHANGELOG.md",
            }
            claude_roots = {
                ".claude-plugin/plugin.json",
                "README.md",
                "LICENSE",
                "CHANGELOG.md",
            }
            with zipfile.ZipFile(agent_path) as agent_zip, zipfile.ZipFile(
                claude_path
            ) as claude_zip:
                self.assertEqual(set(agent_zip.namelist()), agent_roots | runtime)
                self.assertEqual(set(claude_zip.namelist()), claude_roots | runtime)
                for member in runtime:
                    self.assertEqual(
                        agent_zip.read(member),
                        claude_zip.read(member),
                        member,
                    )

    def test_rebuild_is_byte_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            first_paths = build_packages.build_archives(ROOT, Path(first))
            second_paths = build_packages.build_archives(ROOT, Path(second))
            self.assertEqual(
                [self.digest(path) for path in first_paths],
                [self.digest(path) for path in second_paths],
            )

    def test_ignores_transient_python_cache_without_packaging_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "source"
            shutil.copytree(
                ROOT,
                root,
                ignore=shutil.ignore_patterns(".git", "dist", "__pycache__"),
            )
            cache = root / "skills/workslop-detector/scripts/__pycache__"
            cache.mkdir()
            (cache / "scanner.cpython-314.pyc").write_bytes(b"generated")
            agent_path, claude_path = build_packages.build_archives(
                root,
                Path(tmp) / "out",
            )
            for path in (agent_path, claude_path):
                with zipfile.ZipFile(path) as archive:
                    self.assertFalse(
                        any(
                            "__pycache__" in name or name.endswith(".pyc")
                            for name in archive.namelist()
                        )
                    )


class PackageRejectionTests(unittest.TestCase):
    def copy_repo(self, parent: Path) -> Path:
        clone = parent / "source"
        shutil.copytree(
            ROOT,
            clone,
            ignore=shutil.ignore_patterns(".git", "dist", "__pycache__"),
        )
        return clone

    def test_rejects_manifest_version_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self.copy_repo(Path(tmp))
            path = root / ".claude-plugin/plugin.json"
            manifest = json.loads(path.read_text(encoding="utf-8"))
            manifest["version"] = "0.1.3"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaises(build_packages.PackageError):
                build_packages.build_archives(root, Path(tmp) / "out")

    def test_rejects_unexpected_runtime_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self.copy_repo(Path(tmp))
            (root / "skills/workslop-detector/private-notes.md").write_text(
                "private",
                encoding="utf-8",
            )
            with self.assertRaises(build_packages.PackageError):
                build_packages.build_archives(root, Path(tmp) / "out")

    def test_rejects_unresolved_release_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self.copy_repo(Path(tmp))
            with (root / "README.md").open("a", encoding="utf-8") as handle:
                handle.write("\nTODO: rewrite\n")
            with self.assertRaises(build_packages.PackageError):
                build_packages.build_archives(root, Path(tmp) / "out")

    def test_rejects_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self.copy_repo(Path(tmp))
            os.symlink(
                root / "README.md",
                root / "skills/workslop-detector/leak.md",
            )
            with self.assertRaises(build_packages.PackageError):
                build_packages.build_archives(root, Path(tmp) / "out")

    def test_rejects_path_traversal_member(self) -> None:
        with self.assertRaises(build_packages.PackageError):
            build_packages.validate_archive_name("../escape")


class PublicDocumentationTests(unittest.TestCase):
    def test_readme_covers_the_public_contract(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        for phrase in (
            "What is workslop?",
            "Human delta",
            "What did the person add?",
            "How much work is left for the reader?",
            "Was it reviewed before sharing?",
            "Can its claims be trusted?",
            "Funny mode",
            "Serious mode",
            "original assignment",
            "submitted document",
            "Agent Plugin",
            "Claude and Cowork",
            "cannot prove AI authorship",
            "Want a version you can send back?",
        ):
            self.assertIn(phrase, text)

    def test_send_back_reply_is_opt_in(self) -> None:
        tone = (ROOT / "skills/workslop-detector/references/tone-guide.md").read_text(
            encoding="utf-8"
        )
        arbiter = (ROOT / "skills/workslop-detector/agents/arbiter-prompt.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Wait for the user to choose a format", tone)
        self.assertIn("Do not draft an outbound message", arbiter)
        self.assertNotIn("Funny draft-reply bank", tone)

    def test_packageable_text_has_no_private_markers(self) -> None:
        _, files = build_packages.validate_source_tree(ROOT)
        private_markers = (
            "/Users/",
            ".claude/skills",
            ".codex/worktrees",
            "10_Clients/",
            "Sally",
        )
        for relative in files:
            text = (ROOT / relative).read_text(encoding="utf-8")
            for marker in private_markers:
                self.assertNotIn(marker, text, f"{marker} in {relative}")


if __name__ == "__main__":
    unittest.main()
