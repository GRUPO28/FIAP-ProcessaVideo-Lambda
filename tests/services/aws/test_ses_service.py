import unittest
from unittest.mock import MagicMock, patch


class TestSesService(unittest.TestCase):
    @patch('boto3.client')
    def setUp(self, mock_boto_client):
        self.mock_ses = MagicMock()
        mock_boto_client.return_value = self.mock_ses
        from app.services.aws.ses_service import SesService
        self.ses_service = SesService()

    def test_send_email_success(self):
        self.mock_ses.send_email.return_value = {'MessageId': '12345'}

        from_email = 'sender@example.com'
        to_emails = ['recipient@example.com']
        subject = 'Test Subject'
        body = 'Test Body'

        response = self.ses_service.send_email(from_email, to_emails, subject, body)

        # Verificar se o método send_email foi chamado corretamente
        self.mock_ses.send_email.assert_called_once_with(
            Source=from_email,
            Destination={'ToAddresses': to_emails},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': body}}
            }
        )

        # Verificar o retorno
        self.assertEqual(response['MessageId'], '12345')

    def test_send_email_failure(self):
        self.mock_ses.send_email.side_effect = Exception('Erro ao enviar e-mail')

        from_email = 'sender@example.com'
        to_emails = ['recipient@example.com']
        subject = 'Test Subject'
        body = 'Test Body'

        with self.assertRaises(Exception) as context:
            self.ses_service.send_email(from_email, to_emails, subject, body)

        # Verificar se a exceção foi levantada
        self.assertEqual(str(context.exception), 'Erro ao enviar e-mail')

        # Verificar se o método send_email foi chamado corretamente
        self.mock_ses.send_email.assert_called_once_with(
            Source=from_email,
            Destination={'ToAddresses': to_emails},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': body}}
            }
        )
