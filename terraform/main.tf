provider "aws" {
  region = "us-east-1"
}

# Role da Lambda
resource "aws_iam_role" "lambda_role" {
  name = "lambda_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Política de permissões da Lambda
resource "aws_iam_policy" "lambda_policy" {
  name        = "lambda_access_policy"
  description = "Permissões para Lambda acessar S3, DynamoDB e SES"
  policy      = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "dynamodb:GetItem",
          "dynamodb:UpdateItem"
        ],
        Resource = "arn:aws:dynamodb:980029326297:table/Videos"
      },
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ],
        Resource = [
          "arn:aws:s3:980029326297:processa-video-app/*",
          "arn:aws:s3:980029326297:processa-video-infra/*",
        ]
      },
      {
        Effect = "Allow",
        Action = "ses:SendEmail",
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "arn:aws:980029326297:log-group:/aws/lambda/video_processor:*"
      }
    ]
  })
}

# Anexa a política ao Role
resource "aws_iam_role_policy_attachment" "attach_lambda_policy" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

# Função Lambda
resource "aws_lambda_function" "video_processor" {
  function_name    = "video_processor"
  role            = aws_iam_role.lambda_role.arn
  handler        = "lambda_function.lambda_handler"
  runtime        = "python3.8"
  timeout        = 60
  memory_size    = 512
  s3_bucket      = "processa-video-infra"
  s3_key         = "video_processor.zip"

  environment {
    variables = {
      TABLE_NAME = "Videos"
    }
  }

  depends_on = [aws_iam_role_policy_attachment.attach_lambda_policy]
}

# Permissão para a Lambda ser acionada por eventos do SQS (se necessário)
resource "aws_lambda_permission" "allow_sqs" {
  statement_id  = "AllowExecutionFromSQS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.video_processor.function_name
  principal     = "sqs.amazonaws.com"
  source_arn    = "arn:aws:sqs:us-east-1:980029326297:videos-queue"
}