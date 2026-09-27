"""Input failures must stop before loading an ASR dependency or model."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/transcribe.py"


class InputTest(unittest.TestCase):
    def test_rejects_missing_media_and_uncached_model(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            media = root / "sample.wav"
            for expected in ("existing local file", "cached model directory"):
                result = subprocess.run(
                    [sys.executable, "-S", str(SCRIPT), str(media), "--model", str(root)],
                    capture_output=True, text=True,
                )
                self.assertEqual(result.returncode, 2)
                self.assertIn(expected, result.stderr)
                self.assertEqual(result.stdout, "")
                media.touch()


if __name__ == "__main__":
    unittest.main()
