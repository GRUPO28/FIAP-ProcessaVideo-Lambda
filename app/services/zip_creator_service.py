import io
import zipfile

import cv2


class ZipCreatorService:
    @staticmethod
    def create_zip_from_frames(frames):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for idx, frame in enumerate(frames):
                _, buffer = cv2.imencode('.jpg', frame)
                zip_file.writestr(f'frame_{idx:04d}.jpg', buffer.tobytes())
        zip_buffer.seek(0)
        return zip_buffer
