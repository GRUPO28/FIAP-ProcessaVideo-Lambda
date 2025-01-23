from lambda_handler import lambda_handler

event = {
  "Records": [
    {
      "messageId": "12345678-1234-5678-1234-567812345678",
      "receiptHandle": "AQEB...exampleReceiptHandle...",
      "body": "{\"video_s3_bucket\": \"app-processa-video\", \"video_s3_key\": \"videos/sample_video.mp4\", \"s3_bucket\": \"app-processa-video\", \"s3_key\": \"imagens/frames.zip\", \"user_email\": \"p.avelinojunior@gmail.com\"}",
      "attributes": {
        "ApproximateReceiveCount": "1",
        "SentTimestamp": "1674567890123",
        "SenderId": "AIDAIEXAMPLE",
        "ApproximateFirstReceiveTimestamp": "1674567890123"
      },
      "messageAttributes": {},
      "md5OfBody": "098f6bcd4621d373cade4e832627b4f6",
      "eventSource": "aws:sqs",
      "eventSourceARN": "arn:aws:sqs:us-east-1:123456789012:MyQueue",
      "awsRegion": "us-east-1"
    }
  ]
}
a = lambda_handler(event, None)
print(a)
