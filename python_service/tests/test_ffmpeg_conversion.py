"""Real-ffmpeg checks for _convert_flac_to_aiff.

Soulseek peers choose the bytes of every download, and ffmpeg picks a demuxer
from a file's contents, not its name. The conversion pins the input format to
FLAC so a file named .flac is only ever parsed as FLAC.
"""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from src.processor import AudioProcessor
from tests.test_processor_retry import DummyConfig

FFMPEG = shutil.which("ffmpeg")
FFPROBE = shutil.which("ffprobe")


def _make_audio(path: Path, fmt: str) -> None:
    subprocess.run(
        [FFMPEG, "-nostdin", "-loglevel", "error", "-f", "lavfi", "-i", "sine=frequency=440:duration=1",
         "-ar", "48000", "-f", fmt, str(path)],
        check=True,
    )


@unittest.skipUnless(FFMPEG and FFPROBE, "ffmpeg/ffprobe not installed")
class FlacConversionTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.processor = AudioProcessor(DummyConfig(self.root))

    def tearDown(self):
        self._tmp.cleanup()

    def test_genuine_flac_becomes_16_bit_44_1_khz_aiff(self):
        src = self.root / "complete" / "track.flac"
        dst = self.root / "processed" / "track.aiff"
        _make_audio(src, "flac")

        self.assertTrue(self.processor._convert_flac_to_aiff(src, dst))

        probe = subprocess.run(
            [FFPROBE, "-v", "error", "-show_entries", "stream=codec_name,sample_rate:format=format_name",
             "-of", "json", str(dst)],
            capture_output=True, text=True, check=True,
        )
        info = json.loads(probe.stdout)
        self.assertEqual(info["format"]["format_name"], "aiff")
        self.assertEqual(info["streams"][0]["codec_name"], "pcm_s16be")
        self.assertEqual(info["streams"][0]["sample_rate"], "44100")

    def test_non_flac_content_named_flac_is_refused(self):
        src = self.root / "complete" / "disguised.flac"
        dst = self.root / "processed" / "disguised.aiff"
        _make_audio(src, "wav")

        self.assertFalse(self.processor._convert_flac_to_aiff(src, dst))
        self.assertTrue(src.exists(), "the source must be left in place")

    def test_playlist_named_flac_is_refused(self):
        src = self.root / "complete" / "playlist.flac"
        dst = self.root / "processed" / "playlist.aiff"
        src.write_text(
            "#EXTM3U\n#EXT-X-TARGETDURATION:1\n#EXT-X-MEDIA-SEQUENCE:0\n"
            "#EXTINF:1,\nfile:///etc/hosts\n#EXT-X-ENDLIST\n"
        )

        self.assertFalse(self.processor._convert_flac_to_aiff(src, dst))


if __name__ == "__main__":
    unittest.main()
