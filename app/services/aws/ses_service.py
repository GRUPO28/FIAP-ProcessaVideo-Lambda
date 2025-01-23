import boto3


class SesService:
    def __init__(self):
        self.ses = boto3.client('ses')

    def send_email(self, from_email, to_emails, subject, body):
        try:
            response = self.ses.send_email(
                Source=from_email,
                Destination={
                    'ToAddresses': to_emails
                },
                Message={
                    'Subject': {
                        'Data': subject
                    },
                    'Body': {
                        'Text': {
                            'Data': body
                        }
                    }
                }
            )
            print(f"E-mail enviado com sucesso: {response['MessageId']}")
            return response
        except Exception as e:
            print(f"Erro ao enviar e-mail: {str(e)}")
            raise
