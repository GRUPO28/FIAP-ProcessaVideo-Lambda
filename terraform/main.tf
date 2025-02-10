provider "aws" {
  region = "us-east-1"
}

# Gerar um identificador único para o nome da role
resource "random_id" "role_suffix" {
  byte_length = 4
}

# Role da Lambda
resource "aws_iam_role" "lambda_role" {
  name = "lambda_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
      {
        Effect = "Allow",
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ],
        Resource = aws_sqs_queue.video_queue.arn
      }
    ]
  })
}

# Buscar política IAM existente
data "aws_iam_policy" "existing_lambda_policy" {
  name = "lambda_access_policy"
}

resource "aws_iam_role_policy_attachment" "attach_lambda_policy" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = data.aws_iam_policy.existing_lambda_policy.arn
}

# Criar fila SQS, caso não exista
resource "aws_sqs_queue" "video_queue" {
  name                      = "videos-queue"
  visibility_timeout_seconds = 60
  message_retention_seconds = 86400  # 1 dia
}

# Permissões adicionais para a Lambda acessar a SQS
resource "aws_iam_policy" "lambda_sqs_policy" {
  name        = "lambda_sqs_policy_${random_id.role_suffix.hex}"
  description = "Permissões para a Lambda acessar SQS"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ],
        Resource = aws_sqs_queue.video_queue.arn
      }
    ]
  })
}

# Anexar política de permissões da SQS à role da Lambda
resource "aws_iam_role_policy_attachment" "attach_lambda_sqs_policy" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_sqs_policy.arn
}

# Criar Lambda apenas se não existir
resource "aws_lambda_function" "video_processor" {
  function_name = "video_processor"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.8"
  timeout       = 60
  memory_size   = 512
  s3_bucket     = "processa-video-infra"
  s3_key        = "video_processor.zip"

  environment {
    variables = {
      TABLE_NAME = "Videos"
    }
  }

  depends_on = [aws_iam_role_policy_attachment.attach_lambda_policy, aws_iam_role_policy_attachment.attach_lambda_sqs_policy]
}

# Permissão para a Lambda ser acionada por eventos do SQS
resource "aws_lambda_permission" "allow_sqs" {
  statement_id  = "AllowExecutionFromSQS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.video_processor.function_name
  principal     = "sqs.amazonaws.com"
  source_arn    = aws_sqs_queue.video_queue.arn
}

# Configurar a integração da SQS com a Lambda
resource "aws_lambda_event_source_mapping" "sqs_lambda_trigger" {
  event_source_arn = aws_sqs_queue.video_queue.arn
  function_name    = aws_lambda_function.video_processor.arn
  batch_size       = 10
}
