# media-extract

An agent skill for reading media without opening a browser or playing it.
Uses yt-dlp for public URLs, FFmpeg for inspection and still frames, and a small
Faster Whisper helper for local speech transcription.

## Install

```bash
git clone --branch feat/cli-media-extraction --single-branch https://github.com/pekth/media-extract-skill.git
npx skills add ./media-extract-skill --skill media-extract
```

The initial skill is on the review branch above. After it merges into `main`,
install directly with `npx skills add pekth/media-extract-skill`.

The skill needs the tools for the requested operation. Installing the skill
does not install yt-dlp, FFmpeg, Python dependencies, or speech models. Follow
[local transcription setup](references/local-transcription.md) when needed.

Example requests:

- "Summarize this YouTube video's captions without playing it."
- "Extract the transcript from this public TikTok URL."
- "Transcribe this local recording and mark uncertain names."
- "Inspect these timestamps from a local video as still images."

## Scope and limits

YouTube, TikTok, Facebook, and Instagram have yt-dlp extractors. Support depends
on the exact URL, site changes, available captions, and public access. Login-only
content, bot checks, and rate limits are stop conditions. This skill does not
scrape feeds, import browser cookies, publish posts, or bypass access controls.

Captions are preferred. When a recording has no captions, authorized media can
be transcribed locally with a cached model. The helper produces timestamped
JSON, uses CPU INT8, and does not perform diarization. Model output still needs
review for hallucinations, names, and numbers.

The default workflow does not play media or upload it to a cloud transcription
service. External tools still make network requests to fetch public metadata,
captions, authorized downloads, dependencies, or models. The helper is not a
network sandbox.

## Development checks

```bash
python -m unittest discover -s tests
python scripts/transcribe.py --help
```

For an integration check, run the helper against an authorized short speech
sample and a cached model. Confirm nonempty, ordered timestamps and plausible
words. Keep the sample, model, output, and logs outside this repository.

## Related work

Existing skills informed the fit review: [video-transcript-downloader](https://github.com/steipete/agent-scripts/tree/main/skills/video-transcript-downloader)
for online sources and [OpenClaw's local Whisper skill](https://github.com/openclaw/openclaw/tree/main/skills/openai-whisper)
for local speech. This skill provides a combined workflow with explicit
no-playback, local-processing, and caption-evidence rules. It does not replace
or vendor yt-dlp, FFmpeg, or Faster Whisper.

MIT licensed. See [LICENSE](LICENSE).
