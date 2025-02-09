from lambda_handler import lambda_handler

event = {
  "Records": [
    {
      "messageId": "1",
      "receiptHandle": "abc123",
      "body": "{\"Id\": \"5DB47\", \"Usuario\": \"teste@example.com\", \"Url\": \"s3://meu-bucket/sample_video.mp4\"}",
      "attributes": {
        "ApproximateReceiveCount": "1",
        "SentTimestamp": "1647289200000",
        "SenderId": "sender-id",
        "ApproximateFirstReceiveTimestamp": "1647289200000"
      },
      "messageAttributes": {},
      "md5OfBody": "c8e05a1bd4f0c7d22c44db181b6a1299",
      "eventSource": "aws:sqs",
      "eventSourceARN": "arn:aws:sqs:us-east-1:123456789012:my-queue",
      "awsRegion": "us-east-1"
    }
  ]
}
a = lambda_handler(event, None)
print(a)
