import os
import sys
import tempfile
import types
import unittest

if "yt_dlp" not in sys.modules:
    fake_yt_dlp = types.ModuleType("yt_dlp")
    fake_yt_dlp.__version__ = "test"
    fake_yt_dlp.YoutubeDL = object
    sys.modules["yt_dlp"] = fake_yt_dlp

import app


class VideoQualityTests(unittest.TestCase):
    def test_theme_preferences_round_trip(self):
        original_path = app._theme_preferences_path
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                theme_path = os.path.join(temp_dir, "theme.json")
                app._theme_preferences_path = lambda: theme_path
                app.save_theme_key("ocean")
                self.assertEqual(app.load_theme_key(), "ocean")
                app.save_theme_key("unknown")
                self.assertEqual(app.load_theme_key(), "dark")
        finally:
            app._theme_preferences_path = original_path

    def test_extracts_unique_video_heights_and_ignores_audio_only(self):
        info = {
            "formats": [
                {"vcodec": "none", "height": None},
                {"vcodec": "avc1", "height": 720},
                {"vcodec": "vp9", "height": 1080},
                {"vcodec": "avc1", "height": 720},
                {"vcodec": "av01", "height": 0},
            ]
        }
        self.assertEqual(app.extract_video_heights(info), [1080, 720])

    def test_uses_top_level_height_when_formats_do_not_expose_one(self):
        self.assertEqual(app.extract_video_heights({"formats": [], "height": 480}), [480])
        self.assertEqual(app.extract_video_heights({"formats": []}), [])

    def test_selected_selector_keeps_height_as_a_maximum(self):
        selector = app.build_video_format_selector("mp4", 720)
        self.assertIn("height<=720", selector)
        self.assertNotIn("wv*+ba/w", selector)
        self.assertEqual(app.build_video_format_selector("mkv", None), "bv*+ba/b")

    def test_cli_parser_supports_quality_with_and_without_limit(self):
        parser = app.build_argument_parser()
        without_limit = parser.parse_args(["--no-gui", "-u", "https://example.test/video", "-f", "mp4"])
        with_limit = parser.parse_args([
            "--no-gui",
            "-u",
            "https://example.test/video",
            "-f",
            "mp4",
            "--video-quality",
            "720",
        ])
        self.assertIsNone(without_limit.video_quality)
        self.assertEqual(with_limit.video_quality, 720)
        with self.assertRaises(SystemExit):
            parser.parse_args(["--video-quality", "0"])

    def test_cli_passes_video_limit_to_yt_dlp(self):
        captured_options = []

        class FakeYoutubeDL:
            def __init__(self, options):
                captured_options.append(options)

            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def extract_info(self, _url, download=False):
                self.assert_download_false = download
                return {"title": "Test video"}

            def download(self, _urls):
                return None

        original_youtube_dl = app.yt_dlp.YoutubeDL
        original_ffmpeg = app.get_ffmpeg_path
        original_optimize = app.optimize_network
        try:
            app.yt_dlp.YoutubeDL = FakeYoutubeDL
            app.get_ffmpeg_path = lambda: ffmpeg_path
            app.optimize_network = lambda: None
            with tempfile.TemporaryDirectory() as output_dir:
                ffmpeg_path = os.path.join(output_dir, "ffmpeg.exe")
                open(ffmpeg_path, "w", encoding="utf-8").close()
                app.run_cli_download(
                    "https://example.test/video",
                    "mp4",
                    output_dir,
                    "192",
                    video_quality=720,
                )
        finally:
            app.yt_dlp.YoutubeDL = original_youtube_dl
            app.get_ffmpeg_path = original_ffmpeg
            app.optimize_network = original_optimize

        self.assertIn("height<=720", captured_options[-1]["format"])


if __name__ == "__main__":
    unittest.main()
