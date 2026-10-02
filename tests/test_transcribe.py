"""Check local inputs and CUDA fallback through the helper entry point."""
import io
import json
import runpy
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

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


class InferenceTest(unittest.TestCase):
    def test_cuda_fallback_includes_lazy_inference(self):
        for cuda_count, failure in (
            (0, None), (1, None), (1, "load"), (1, "transcribe"), (1, "segments"),
        ):
            with self.subTest(cuda_count=cuda_count, failure=failure):
                output, warning, devices = self.run_helper(cuda_count, failure)
                self.assertEqual(json.loads(output), {
                    "method": "local-asr", "language": "en",
                    "segments": [{"start": 0.0, "end": 1.0, "text": "hello"}],
                })
                self.assertEqual(devices, ["cpu"] if cuda_count == 0 else
                                 ["cuda", "cpu"] if failure else ["cuda"])
                self.assertEqual(bool(warning), bool(failure))

    def test_cpu_failure_propagates_without_partial_json(self):
        for cuda_count in (0, 1):
            with self.subTest(cuda_count=cuda_count):
                with self.assertRaisesRegex(RuntimeError, "CPU unavailable"):
                    self.run_helper(cuda_count, "segments", cpu_failure=True)

    def run_helper(self, cuda_count, failure, cpu_failure=False):
        devices = []

        def whisper_model(path, *, device, compute_type, local_files_only):
            devices.append(device)
            self.assertTrue(Path(path).is_absolute())
            self.assertTrue(local_files_only)
            self.assertEqual(compute_type, "float16" if device == "cuda" else "int8")
            if device == "cuda" and failure == "load":
                raise RuntimeError("CUDA unavailable")

            def transcribe(media, *, language, condition_on_previous_text, vad_filter):
                self.assertTrue(Path(media).is_absolute())
                self.assertEqual(language, "en")
                self.assertFalse(condition_on_previous_text)
                self.assertTrue(vad_filter)
                if device == "cuda" and failure == "transcribe":
                    raise RuntimeError("CUDA unavailable")

                def segments():
                    if device == "cuda" and failure == "segments":
                        yield SimpleNamespace(start=0.0, end=0.5, text="partial CUDA text")
                        raise RuntimeError("CUDA unavailable")
                    if device == "cpu" and cpu_failure:
                        raise RuntimeError("CPU unavailable")
                    yield SimpleNamespace(start=0.0, end=1.0, text=" hello ")

                return segments(), SimpleNamespace(language="en")

            return SimpleNamespace(transcribe=transcribe)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            media = root / "sample.wav"
            media.touch()
            (root / "model.bin").touch()
            output, warning = io.StringIO(), io.StringIO()
            modules = {
                "ctranslate2": SimpleNamespace(get_cuda_device_count=lambda: cuda_count),
                "faster_whisper": SimpleNamespace(WhisperModel=whisper_model),
            }
            argv = [str(SCRIPT), str(media), "--model", str(root), "--language", "en"]
            with patch.dict(sys.modules, modules), patch.object(sys, "argv", argv):
                with redirect_stdout(output), redirect_stderr(warning):
                    try:
                        runpy.run_path(str(SCRIPT), run_name="__main__")
                    except RuntimeError:
                        self.assertEqual(output.getvalue(), "")
                        self.assertLessEqual(len(devices), 2)
                        raise
            return output.getvalue(), warning.getvalue(), devices


if __name__ == "__main__":
    unittest.main()
