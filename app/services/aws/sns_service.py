import boto3


class SnsService:
    def __init__(self):
        self.sns = boto3.client('sns')

    def notify_user(self, email, message):
        try:
            response = self.sns.publish(
                TopicArn='arn:aws:sns:us-east-1:617932910341:EMAIL',
                Message=message,
                Subject='Notificação de Processamento de Vídeo',
                MessageAttributes={
                    'email': {
                        'DataType': 'String',
                        'StringValue': email
                    }
                }
            )
            print(f"Notificação enviada com sucesso para {email}: {response}")
        except Exception as e:
            print(f"Erro ao enviar notificação para {email}: {str(e)}")
            raise
