from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_packages.py"
SPEC = importlib.util.spec_from_file_location("build_packages", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PackageTests(unittest.TestCase):
    def test_cowork_skill_archive_has_one_top_level_skill_folder(self) -> None:
        with tempfile.TemporaryDirectory() as output:
            archives = MODULE.build_archives(ROOT, Path(output))
            cowork = next(
                (path for path in archives if "cowork-skill" in path.name),
                None,
            )
            self.assertIsNotNone(cowork, "Cowork skill archive was not built")

            assert cowork is not None
            with zipfile.ZipFile(cowork) as archive:
                names = archive.namelist()

            self.assertIn("workslop-detector/SKILL.md", names)
            self.assertTrue(
                all(name.startswith("workslop-detector/") for name in names)
            )
            self.assertNotIn(
                "workslop-detector/.claude-plugin/plugin.json",
                names,
            )


if __name__ == "__main__":
    unittest.main()
