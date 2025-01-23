import unittest
import numpy as np
from app.services.zip_creator_service import ZipCreatorService
import zipfile


class TestZipCreatorService(unittest.TestCase):
    def setUp(self):
        self.service = ZipCreatorService()

    def test_create_zip_from_frames(self):
        frame_height, frame_width = 480, 640
        num_frames = 3
        frames = [
            np.random.randint(0, 256, (frame_height, frame_width, 3), dtype=np.uint8)
            for _ in range(num_frames)
        ]

        zip_buffer = self.service.create_zip_from_frames(frames)

        with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
            zip_content = zip_file.namelist()
            self.assertEqual(len(zip_content), num_frames)
            for idx in range(num_frames):
                self.assertIn(f'frame_{idx:04d}.jpg', zip_content)


if __name__ == '__main__':
    unittest.main()
