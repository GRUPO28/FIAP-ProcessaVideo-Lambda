import json
from app.services.video_processor_service import VideoProcessorService
from app.services.zip_creator_service import ZipCreatorService
from app.services.aws.s3_service import S3Service
from app.services.aws.sns_service import SnsService


class LambdaHandler:
    def __init__(self):
        self.video_processor = VideoProcessorService()
        self.zip_creator = ZipCreatorService()
        self.s3_service = S3Service()
        self.sns_service = SnsService()

    def process_event(self, event):
        try:
            record = event['Records'][0]  # Pegando o primeiro registro
            message = json.loads(record['body'])  # Carregando o JSON do campo `body`
            video_s3_bucket = message['video_s3_bucket']
            video_s3_key = message['video_s3_key']
            output_s3_bucket = message['s3_bucket']
            output_s3_key = message['s3_key']
            user_email = message.get('user_email')

            video_stream = self.s3_service.get_object_stream(video_s3_bucket, video_s3_key)
            frames = self.video_processor.process_video_frames_from_stream(self, video_stream)

            zip_buffer = self.zip_creator.create_zip_from_frames(frames)

            self.s3_service.upload_buffer_to_s3(zip_buffer, output_s3_bucket, output_s3_key)

            if user_email:
                self.sns_service.notify_user(user_email,
                                             f'Seu vídeo foi processado com sucesso. Arquivo disponível em: s3://{output_s3_bucket}/{output_s3_key}')

            return {
                'statusCode': 200,
                'body': f'Video processado e zipado no s3://{output_s3_bucket}/{output_s3_key}'
            }

        except Exception as e:
            if user_email:
                self.sns_service.notify_user(user_email, f'O processamento do seu vídeo falhou: {str(e)}')
            return {
                'statusCode': 500,
                'body': str(e)
            }


lambda_handler_instance = LambdaHandler()


def lambda_handler(event, context):
    return lambda_handler_instance.process_event(event)
