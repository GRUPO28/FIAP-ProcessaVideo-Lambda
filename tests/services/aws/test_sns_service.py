import unittest
from unittest.mock import MagicMock
from app.services.aws.sns_service import SnsService


class TestSnsService(unittest.TestCase):
    def setUp(self):
        self.service = SnsService()
        self.service.sns = MagicMock()

    def test_notify_user_success(self):
        email = 'test@example.com'
        message = 'Seu vídeo foi processado com sucesso.'

        self.service.sns.publish.return_value = {'MessageId': '12345'}

        self.service.notify_user(email, message)

        self.service.sns.publish.assert_called_once_with(
            TopicArn='arn:aws:sns:us-east-1:123456789012:VideoProcessingNotifications',
            Message=message,
            Subject='Notificação de Processamento de Vídeo',
            MessageAttributes={
                'email': {
                    'DataType': 'String',
                    'StringValue': email
                }
            }
        )


if __name__ == '__main__':
    unittest.main()
