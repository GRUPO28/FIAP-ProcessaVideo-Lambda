import json
from app.services.video_processor_service import VideoProcessorService
from app.services.zip_creator_service import ZipCreatorService
from app.services.aws.s3_service import S3Service
from app.services.aws.ses_service import SesService
from app.services.aws.dynamoDB_service import DynamoDBService

STATUS_MAPPING = {
    "Aguardando": 0,
    "Processando": 1,
    "Pronto": 2,
    "Falhou": 3
}


class LambdaHandler:
    def __init__(self):
        self.video_processor = VideoProcessorService()
        self.zip_creator = ZipCreatorService()
        self.s3_service = S3Service()
        self.ses_service = SesService()
        self.dynamoDB_service = DynamoDBService()

    def update_video_status(self, video_id, status_text, url_zip=None):
        try:
            if status_text not in STATUS_MAPPING:
                raise ValueError(f"Status inválido: {status_text}")

            self.dynamoDB_service.update_status(video_id, STATUS_MAPPING[status_text])
        except Exception as e:
            print(f"Erro ao atualizar o status do vídeo: {e}")
            raise

    def process_event(self, event):
        try:
            record = event['Records'][0]  # Pegando o primeiro registro do SQS
            message = json.loads(record['body'])

            video_id = message['Id']
            video_url = message['Url']

            video_data = self.dynamoDB_service.get_item(video_id)
            if not video_data:
                return {'statusCode': 404, 'body': 'Vídeo não encontrado no DynamoDB'}

            user_email = video_data['Email']
            video_s3_bucket, video_s3_key = video_url.replace("s3://", "").split("/", 1)
            output_s3_bucket = "app-processa-video"
            output_s3_key = f"imagens/{video_id}.zip"
            video_s3_key = f'videos/{video_s3_key}'
            self.update_video_status(video_id, "Processando")

            video_stream = self.s3_service.get_object_stream(video_s3_key)
            frames = self.video_processor.process_video_frames_from_stream(self, video_stream)
            zip_buffer = self.zip_creator.create_zip_from_frames(frames)
            self.s3_service.upload_buffer_to_s3(zip_buffer, output_s3_key)

            url_zip = f's3://{output_s3_bucket}/{output_s3_key}'
            self.update_video_status(video_id, "Pronto", url_zip)

            if user_email:
                self.ses_service.send_email(
                    from_email='paulo.avelinojunior@outlook.com',
                    to_emails=[user_email],
                    subject='Processamento de Vídeo Concluído',
                    body=f'Seu vídeo foi processado com sucesso. Arquivo disponível em: {url_zip}'
                )

            return {'statusCode': 200, 'body': f'Vídeo processado e zipado em {url_zip}'}

        except Exception as e:
            self.update_video_status(video_id, "Falhou")
            if user_email:
                self.ses_service.send_email(
                    from_email='paulo.avelinojunior@outlook.com',
                    to_emails=[user_email],
                    subject='Erro no Processamento de Vídeo',
                    body=f'O processamento do seu vídeo falhou. Erro: {str(e)}'
                )
            return {'statusCode': 500, 'body': str(e)}


lambda_handler_instance = LambdaHandler()


def lambda_handler(event, context):
    return lambda_handler_instance.process_event(event)
