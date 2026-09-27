#!/usr/bin/env python3
"""Transcribe a local media file with a cached Faster Whisper model."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("media", type=Path)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--language", help="Language code; omit for detection")
    args = parser.parse_args()
    if not args.media.is_file():
        parser.error("media must be an existing local file")
    if not args.model.is_dir() or not (args.model / "model.bin").is_file():
        parser.error("model must be a cached model directory containing model.bin")

    from faster_whisper import WhisperModel

    model = WhisperModel(
        str(args.model.resolve()), device="cpu", compute_type="int8",
        local_files_only=True,
    )
    segments, info = model.transcribe(
        str(args.media.resolve()), language=args.language,
        condition_on_previous_text=False, vad_filter=True,
    )
    result = {
        "method": "local-asr",
        "language": info.language,
        "segments": [
            {"start": segment.start, "end": segment.end, "text": segment.text.strip()}
            for segment in segments
        ],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
