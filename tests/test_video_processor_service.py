import unittest
import io
import cv2
import numpy as np
from app.services.video_processor_service import VideoProcessorService


class TestVideoProcessorService(unittest.TestCase):
    def setUp(self):
        self.service = VideoProcessorService()

    def test_process_video_frames_from_stream(self):
        frame_height, frame_width = 480, 640
        num_frames = 10
        video_path = '/tmp/test_video.mp4'

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(video_path, fourcc, 30, (frame_width, frame_height))
        for _ in range(num_frames):
            frame = np.random.randint(0, 256, (frame_height, frame_width, 3), dtype=np.uint8)
            out.write(frame)
        out.release()

        with open(video_path, 'rb') as f:
            video_stream = io.BytesIO(f.read())

        frames = self.service.process_video_frames_from_stream(self, video_stream)
        self.assertEqual(len(frames), num_frames)
        self.assertEqual(frames[0].shape, (frame_height, frame_width, 3))


if __name__ == '__main__':
    unittest.main()
