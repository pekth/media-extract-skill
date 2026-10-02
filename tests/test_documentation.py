"""Exercise documentation writes and checks in a temporary repository."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/documentation.py"


class DocumentationTest(unittest.TestCase):
    def test_index_refresh_and_broken_link(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            (root / "docs").mkdir()
            shutil.copyfile(SCRIPT, root / "scripts/documentation.py")
            knowledge = root / "docs/KB.md"
            knowledge.write_text("# Knowledge\n\nKeep this fact.\n")
            readme = root / "README.md"
            readme.write_text("[Knowledge](docs/KB.md)\n")
            subprocess.run(["git", "init", "-q", str(root)], check=True)

            def run(flag):
                return subprocess.run(
                    [sys.executable, str(root / "scripts/documentation.py"), flag],
                    capture_output=True, text=True,
                )

            self.assertIn("index is stale", run("--check").stderr)
            self.assertEqual(run("--write").returncode, 0)
            self.assertIn("Keep this fact.", knowledge.read_text())
            self.assertEqual(run("--check").returncode, 0)
            (root / "docs/new.md").write_text("# New document\n")
            self.assertIn("index is stale", run("--check").stderr)
            self.assertEqual(run("--write").returncode, 0)
            self.assertIn("docs/new.md", knowledge.read_text())
            self.assertEqual(run("--check").returncode, 0)
            readme.write_text("[Missing](docs/missing.md)\n")
            failed = run("--check")
            self.assertEqual(failed.returncode, 2)
            self.assertIn("missing local file link", failed.stderr)
            malformed = knowledge.read_text() + "\n<!-- documentation:start -->\n"
            knowledge.write_text(malformed)
            self.assertEqual(run("--write").returncode, 2)
            self.assertEqual(knowledge.read_text(), malformed)


if __name__ == "__main__":
    unittest.main()
