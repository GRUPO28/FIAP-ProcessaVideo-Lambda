import json
import boto3
from app.services.video_processor_service import VideoProcessorService
from app.services.zip_creator_service import ZipCreatorService
from app.services.aws.s3_service import S3Service
from app.services.aws.ses_service import SesService

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = "Videos"

def get_video_record(video_id):
    table = dynamodb.Table(TABLE_NAME)
    response = table.get_item(Key={'Id': video_id})
    return response.get('Item')

def update_video_status(video_id, status, url_zip=None):
    table = dynamodb.Table(TABLE_NAME)
    update_expr = "SET Status = :s"
    expr_values = {":s": status}
    
    if url_zip:
        update_expr += ", UrlZip = :z"
        expr_values[":z"] = url_zip
    
    table.update_item(
        Key={'Id': video_id},
        UpdateExpression=update_expr,
        ExpressionAttributeValues=expr_values
    )

class LambdaHandler:
    def __init__(self):
        self.video_processor = VideoProcessorService()
        self.zip_creator = ZipCreatorService()
        self.s3_service = S3Service()
        self.ses_service = SesService()

    def process_event(self, event):
        try:
            record = event['Records'][0]  # Pegando o primeiro registro do SQS
            message = json.loads(record['body'])
            
            video_id = message['Id']
            user = message['Usuario']
            video_url = message['Url']

            video_data = get_video_record(video_id)
            if not video_data:
                return {'statusCode': 404, 'body': 'Vídeo não encontrado no DynamoDB'}

            user_email = video_data['Email']
            video_s3_bucket, video_s3_key = video_url.replace("s3://", "").split("/", 1)
            output_s3_bucket = "meu-bucket-output"
            output_s3_key = f"imagens/{video_id}.zip"

            update_video_status(video_id, "Processando")

            video_stream = self.s3_service.get_object_stream(video_s3_bucket, video_s3_key)
            frames = self.video_processor.process_video_frames_from_stream(video_stream)
            zip_buffer = self.zip_creator.create_zip_from_frames(frames)
            self.s3_service.upload_buffer_to_s3(zip_buffer, output_s3_bucket, output_s3_key)

            url_zip = f's3://{output_s3_bucket}/{output_s3_key}'
            update_video_status(video_id, "Pronto", url_zip)

            if user_email:
                self.ses_service.send_email(
                    from_email='paulo.avelinojunior@outlook.com',
                    to_emails=[user_email],
                    subject='Processamento de Vídeo Concluído',
                    body=f'Seu vídeo foi processado com sucesso. Arquivo disponível em: {url_zip}'
                )

            return {'statusCode': 200, 'body': f'Vídeo processado e zipado em {url_zip}'}

        except Exception as e:
            update_video_status(video_id, "Falhou")
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
