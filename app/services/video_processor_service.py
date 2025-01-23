import cv2
import numpy as np
import os


class VideoProcessorService:
    @staticmethod
    def process_video_frames_from_stream(self, video_stream):
        frames = []

        byte_array = np.asarray(bytearray(video_stream.read()), dtype=np.uint8)

        # Diretorio para o video temporario
        temp_dir = '/tmp'
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        video_file = os.path.join(temp_dir, 'temp_video.mp4')
        with open(video_file, 'wb') as temp_file:
            temp_file.write(byte_array)

        cap = cv2.VideoCapture(video_file)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)

        cap.release()

        if os.path.exists(video_file):
            os.remove(video_file)

        return frames