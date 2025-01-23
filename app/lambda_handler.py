import json
from app.services.video_processor_service import VideoProcessorService
from app.services.zip_creator_service import ZipCreatorService
from app.services.aws.s3_service import S3Service


class LambdaHandler:
    def __init__(self):
        self.video_processor = VideoProcessorService()
        self.zip_creator = ZipCreatorService()
        self.s3_service = S3Service()

    def process_event(self, event):
        try:
            record = event['Records'][0]
            message = json.loads(record['body'])
            video_s3_bucket = message['video_s3_bucket']
            video_s3_key = message['video_s3_key']
            output_s3_bucket = message['s3_bucket']
            output_s3_key = message['s3_key']

            video_stream = self.s3_service.get_object_stream(video_s3_bucket, video_s3_key)
            frames = self.video_processor.process_video_frames_from_stream(self, video_stream)

            zip_buffer = self.zip_creator.create_zip_from_frames(frames)

            self.s3_service.upload_buffer_to_s3(zip_buffer, output_s3_bucket, output_s3_key)

            return {
                'statusCode': 200,
                'body': f'Video processado e zipado no s3://{output_s3_bucket}/{output_s3_key}'
            }

        except Exception as e:
            return {
                'statusCode': 500,
                'body': str(e)
            }


lambda_handler_instance = LambdaHandler()


def lambda_handler(event, context):
    return lambda_handler_instance.process_event(event)
