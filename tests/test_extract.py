import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

MODULE = Path(__file__).resolve().parents[1] / "src" / "pptx_video_extractor.py"
spec = importlib.util.spec_from_file_location("extractor", MODULE)
extractor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extractor)


class ExtractionTests(unittest.TestCase):
    def test_extract_and_preserve_existing_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            pptx = root / "sample.pptx"
            with zipfile.ZipFile(pptx, "w") as archive:
                archive.writestr("ppt/media/movie.mp4", b"video bytes")
                archive.writestr("ppt/media/picture.png", b"image")
            output = root / "output"
            output.mkdir()
            (output / "movie.mp4").write_bytes(b"existing")
            files = extractor.extract_videos(pptx, output)
            self.assertEqual([p.name for p in files], ["movie_2.mp4"])
            self.assertEqual(files[0].read_bytes(), b"video bytes")
            self.assertEqual((output / "movie.mp4").read_bytes(), b"existing")

    def test_invalid_pptx_reports_error(self):
        with tempfile.TemporaryDirectory() as temp:
            pptx = Path(temp) / "invalid.pptx"
            pptx.write_text("not a presentation")
            with self.assertRaises(ValueError):
                extractor.extract_videos(pptx, Path(temp) / "output")


if __name__ == "__main__":
    unittest.main()
